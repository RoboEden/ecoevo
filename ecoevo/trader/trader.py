from datetime import datetime
from rich import print
from typing import Dict, List, Tuple

from loguru import logger
from ortools.linear_solver import pywraplp
from ecoevo.entities.types import OrderType, IdType

from ecoevo.entities.types import OrderType


class Trader(object):
    """
    trader
    """

    def __init__(self, trade_radius) -> None:
        """
        trader, initialise

        :param list_order:  list of orders
        """

        # param
        self.trade_radius = trade_radius

        # order info
        self.list_order = []
        self.mat_if_match, self.mat_volume = [[]], [[]]
        self.list_match = []

    def parse(self, legal_orders: Dict[IdType,
                                       OrderType]) -> Dict[IdType, OrderType]:
        self.list_order = list(legal_orders.values())

        # process data and run model
        self.mat_if_match, self.mat_volume = self._process()
        self.list_match = self._trade()

        idx2key = list(legal_orders.keys())
        match_orders = {}
        for match in self.list_match:
            idx_A, idx_B = match
            key_A = idx2key[idx_A]
            key_B = idx2key[idx_B]
            order_A = legal_orders[key_A]
            order_B = legal_orders[key_B]

            min_order_A, min_order_B = self.mini_close(order_A, order_B)

            match_orders[key_A] = min_order_A
            match_orders[key_B] = min_order_B

        return match_orders

    def mini_close(
        self,
        order_A: OrderType,
        order_B: OrderType,
    ):
        pos_A, sell_offer_A, buy_offer_A = order_A
        sell_A_name, sell_A_num = sell_offer_A
        buy_A_name, buy_A_num = buy_offer_A

        pos_B, sell_offer_B, buy_offer_B = order_B
        sell_B_name, sell_B_num = sell_offer_B
        buy_B_name, buy_B_num = buy_offer_B

        sell_A_num = -min(abs(sell_A_num), buy_B_num)
        buy_A_num = min(abs(sell_B_num), buy_A_num)

        sell_B_num = -buy_A_num
        buy_B_num = abs(sell_A_num)

        min_order_A = pos_A, (sell_A_name, sell_A_num), (buy_A_name, buy_A_num)
        min_order_B = pos_B, (sell_B_name, sell_B_num), (buy_B_name, buy_B_num)

        return min_order_A, min_order_B

    def _process(self) -> Tuple[List[List[bool]], List[List[int]]]:
        """
        data process for model

        :return: mat_if_match:  available matching matrix
        :return: mat_volume:  trading volume matrix
        """

        mat_if_match = [[False for _ in self.list_order] for _ in self.list_order]
        mat_volume = [[0 for _ in self.list_order] for _ in self.list_order]
        for i in range(len(self.list_order)):
            for j in range(len(self.list_order)):
                ((pos_x_i, pos_y_i), (item_sell_i, num_sell_i), (item_buy_i, num_buy_i)) = self.list_order[i]
                ((pos_x_j, pos_y_j), (item_sell_j, num_sell_j), (item_buy_j, num_buy_j)) = self.list_order[j]

                # jump over same orders
                if i == j:
                    continue

                # too far to trade
                if abs(pos_x_i - pos_x_j) > self.trade_radius or abs(pos_y_i - pos_y_j) > self.trade_radius:
                    continue

                # items cannot match
                if item_sell_i != item_buy_j or item_buy_i != item_sell_j:
                    continue

                # item ratio cannot match
                if num_sell_i * num_sell_j != num_buy_i * num_buy_j:
                    continue

                mat_if_match[i][j] = True
                mat_volume[i][j] = min(abs(num_sell_i), num_buy_i, abs(num_sell_j), num_buy_j)

        return mat_if_match, mat_volume

    def _trade(self) -> List[Tuple[int, int]]:
        """
        IP Model for automated trade matching

        :return: list_match:  matching list, (order index, order index)
        """

        # parameters
        num_order = len(self.list_order)
        mat_if_match = self.mat_if_match
        mat_volume = self.mat_volume

        solver = pywraplp.Solver(
            name='location',
            problem_type=pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

        # variable: if choose a match
        x = [[
            solver.BoolVar('x_{}_{}'.format(i, j)) for j in range(num_order)
        ] for i in range(num_order)]

        # constraint: validation
        for i in range(num_order):
            for j in range(num_order):
                solver.Add(x[i][j] <= mat_if_match[i][j])

        # constraint: symmetry
        for i in range(num_order):
            for j in range(num_order):
                solver.Add(x[i][j] == x[j][i])

        # constraint: match only once
        for i in range(num_order):
            solver.Add(sum(x[i][j] for j in range(num_order)) <= 1)

        # objective: maximise the total trading volume
        solver.Maximize(
            sum(
                sum(mat_volume[i][j] * x[i][j] / 2 for j in range(num_order))
                for i in range(num_order)))

        # solve
        dts = datetime.now()
        status = solver.Solve()
        dte = datetime.now()
        tm = round((dte - dts).seconds + (dte - dts).microseconds / (10**6), 3)
        logger.debug(f"trading model solving time:{tm}s")

        # case 1: optimal
        list_match = []
        if status == pywraplp.Solver.OPTIMAL:
            obj_ = solver.Objective().Value()
            logger.debug(f"objective value:{round(obj_)}")
            x_ = [[x[i][j].solution_value() for j in range(num_order)]
                  for i in range(num_order)]

            # result
            for i in range(num_order):
                for j in range(num_order):
                    if j > i and x_[i][j] > 0.9:
                        list_match.append((i, j))
                        logger.debug(
                            f"Order {i} matches {j} with trading volume {mat_volume[i][j]}"
                        )

        # case 2: infeasible
        elif status == pywraplp.Solver.INFEASIBLE:
            raise Exception("Ineasible!")

        # case 3: others
        else:
            raise Exception("Unexpected status: {}!".format(status))

        return list_match