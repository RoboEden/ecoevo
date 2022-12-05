from datetime import datetime
from typing import List, Dict, Tuple

from ortools.linear_solver import pywraplp


class Trader(object):
    """
    trader
    """

    def __init__(self, trade_radius) -> None:
        """
        trader, initialise

        :param list_order:  list of orders
        """

        # data process for model
        self.trade_radius = trade_radius
        # model result

    def parse(self, list_order: List[Tuple[Tuple[int, int], Tuple[str, int],
                                           Tuple[str, int]]]):
        # order: ((x, y), ('sand', -5), ('gold', 10))
        self.list_order = list_order
        self.mat_if_match, self.mat_volume = self._process()
        list_match = self._trade()

        match_order_list = [None] * len(list_order)
        for match in list_match:
            idx_A, idx_B = match
            order_A = list_order[idx_A][1:]
            order_B = list_order[idx_B][1:]
            min_order_A, min_order_B = self.mini_close(order_A, order_B)
            match_order_list[idx_A] = min_order_A
            match_order_list[idx_B] = min_order_B

        return match_order_list

    def mini_close(
        self,
        order_A: Tuple[Tuple[int, int], Tuple[str, int]],
        order_B: Tuple[Tuple[int, int], Tuple[str, int]],
    ):
        sell_offer_A, buy_offer_A = order_A
        sell_A_name, sell_A_num = sell_offer_A
        buy_A_name, buy_A_num = buy_offer_A

        sell_offer_B, buy_offer_B = order_B
        sell_B_name, sell_B_num = sell_offer_B
        buy_B_name, buy_B_num = buy_offer_B

        sell_A_num = -min(abs(sell_A_num), buy_B_num)
        buy_A_num = min(abs(sell_B_num), buy_A_num)

        sell_B_num = -buy_A_num
        buy_B_num = abs(sell_A_num)

        order_A = sell_offer_A, buy_offer_A
        order_B = sell_offer_B, buy_offer_B

        return order_A, order_B

    def _process(self) -> Tuple[List[List[bool]], List[List[int]]]:
        """
        data process for model

        :return: mat_if_match:  available matching matrix
        :return: mat_volume:  trading volume matrix
        """

        mat_if_match = [[False for _ in self.list_order]
                        for _ in self.list_order]
        mat_volume = [[0 for _ in self.list_order] for _ in self.list_order]
        for i in range(len(self.list_order)):
            for j in range(len(self.list_order)):
                # jump over same orders
                if i == j:
                    continue

                # too far to trade
                pos_i, pos_j = self.list_order[i][0], self.list_order[j][0]
                if abs(pos_i[0] - pos_j[0]) > self.trade_radius or abs(
                        pos_i[1] - pos_j[1]) > self.trade_radius:
                    continue

                # items cannot match
                if self.list_order[j][2][0] != self.list_order[i][1][
                        0] or self.list_order[j][1][0] != self.list_order[i][
                            2][0]:
                    continue

                # item ratio cannot match
                if self.list_order[i][1][1] * self.list_order[j][1][
                        1] != self.list_order[i][2][1] * self.list_order[j][2][
                            1]:
                    continue

                mat_if_match[i][j] = True
                mat_volume[i][j] = min(abs(self.list_order[i][1][1]),
                                       self.list_order[i][2][1],
                                       abs(self.list_order[j][1][1]),
                                       self.list_order[j][2][1])

        return mat_if_match, mat_volume

    def _trade(self):
        """
        IP Model for automated trade matching

        :return: dict_match:  matching list, (order index, order index)
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
        print("trading model solving time:  {} s".format(tm), '\n')

        # case 1: optimal
        list_match = []
        if status == pywraplp.Solver.OPTIMAL:
            print("solution:")
            obj_ = solver.Objective().Value()
            print("objective value:  {}".format(round(obj_)))
            x_ = [[x[i][j].solution_value() for j in range(num_order)]
                  for i in range(num_order)]

            # result
            for i in range(num_order):
                for j in range(num_order):
                    if j > i and x_[i][j] > 0.9:
                        list_match.append((i, j))
                        print("order {} matches {} with trading volume {}".
                              format(i, j, mat_volume[i][j]))
            print()

        # case 2: infeasible
        elif status == pywraplp.Solver.INFEASIBLE:
            raise Exception("Ineasible!")

        # case 3: others
        else:
            raise Exception("Unexpected status: {}!".format(status))
        return list_match