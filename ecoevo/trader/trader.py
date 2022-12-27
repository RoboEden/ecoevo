from datetime import datetime
from typing import Dict, List, Tuple

from loguru import logger
from ortools.linear_solver import pywraplp
from ecoevo.entities.player import Player
from ecoevo import types as tp


class Trader(object):
    """
    trader
    """

    def __init__(self, trade_radius) -> None:
        """
        trader, initialise

        :param list_deal:  list of deals
        """

        # param
        self.trade_radius = trade_radius

        # deal info
        self.list_deal = []
        self.mat_if_match, self.mat_volume = [[]], [[]]
        self.list_match = []

    def filter_legal_deals(self, players: List[Player], actions: List[tp.ActionType]) -> Dict[tp.IdType, tp.DealType]:
        """
        tarder parser

        :param players:  list of players
        :param actions:  list of actions

        :return: legal_deals:  dict of legal deals
        """

        legal_deals = {}

        for player in players:
            main_action, sell_offer, buy_offer = actions[player.id]
            primary_action, secondary_action = main_action

            # parse offer
            if sell_offer is None or buy_offer is None:
                player.trade_result = tp.TradeResult.absent
                continue

            sell_item_name, sell_num = sell_offer
            buy_item_name, buy_num = buy_offer
            if sell_item_name == buy_item_name:
                player.trade_result = tp.TradeResult.illegal
                logger.debug(f'Invalid: sell item is the same as buy item {sell_item_name}')
                continue
            if not sell_num < 0:
                player.trade_result = tp.TradeResult.illegal
                logger.debug(f'Invalid sell_num {sell_num}, should be < 0')
                continue
            if not buy_num > 0:
                player.trade_result = tp.TradeResult.illegal
                logger.debug(f'Invalid buy_num {buy_num}, should be > 0')
                continue
            sell_num, buy_num = abs(sell_num), abs(buy_num)

            # check sell
            sell_item = player.backpack[sell_item_name]

            # handle sell and consume same item
            least_amount = sell_num
            if primary_action == tp.Action.consume:
                consume_item_name = secondary_action
                if sell_item_name == consume_item_name:
                    least_amount += sell_item.consume_num

            if sell_item.num < least_amount:
                logger.debug(
                    f'Insufficient {sell_item_name}:{sell_item.num} sell_num {sell_num}'
                )
                player.trade_result = tp.TradeResult.illegal
                continue

            # check buy
            buy_item_volumne = player.backpack[buy_item_name].capacity * buy_num
            if player.backpack.remain_volume < buy_item_volumne:
                player.trade_result = tp.TradeResult.illegal
                logger.debug(
                    f'Insufficient backpack remain volume:{player.backpack.remain_volume}'
                )
                continue

            legal_deals[player.id] = (player.pos, sell_offer, buy_offer)

        return legal_deals

    def parse(self, legal_deals: Dict[tp.IdType, tp.DealType]) -> Dict[tp.IdType, tp.DealType]:
        """
        tarder parser

        :param legal_deals:  dictionary of legal deals

        :return: match_deals:  result of matched deals
        """

        self.list_deal = list(legal_deals.values())

        # process data and run model
        self.mat_if_match, self.mat_volume = self._process()
        self.list_match = self._trade()

        match_deals = {}
        idx2key = list(legal_deals.keys())
        self.num_trade = 0
        self.dict_num_trade, self.dict_amount_trade = {}, {}
        for match in self.list_match:
            idx_A, idx_B = match
            key_A, key_B = idx2key[idx_A], idx2key[idx_B]
            deal_A, deal_B = legal_deals[key_A], legal_deals[key_B]

            min_deal_A, min_deal_B = self._mini_close(deal_A, deal_B)
            match_deals[key_A], match_deals[key_B] = min_deal_A, min_deal_B
        
        return match_deals

    def _mini_close(self, deal_A: tp.DealType, deal_B: tp.DealType):
        """
        get deals tuple with actual trading volume

        :param deal_A:  deal A
        :param deal_B:  deal B

        :return: min_deal_A:  deal A with actual trading volume
        :return: min_deal_B:  deal B with actual trading volume
        """

        pos_A, (sell_name_A, sell_num_A), (buy_name_A, buy_num_A) = deal_A
        pos_B, (sell_name_B, sell_num_B), (buy_name_B, buy_num_B) = deal_B

        sell_num_A, buy_num_A = -min(abs(sell_num_A), buy_num_B), min(abs(sell_num_B), buy_num_A)
        sell_num_B, buy_num_B = -buy_num_A, abs(sell_num_A)

        min_deal_A = pos_A, (sell_name_A, sell_num_A), (buy_name_A, buy_num_A)
        min_deal_B = pos_B, (sell_name_B, sell_num_B), (buy_name_B, buy_num_B)

        return min_deal_A, min_deal_B

    def _process(self) -> Tuple[List[List[bool]], List[List[int]]]:
        """
        data process for model

        :return: mat_if_match:  available matching matrix
        :return: mat_volume:  trading volume matrix
        """

        mat_if_match = [[False for _ in self.list_deal]for _ in self.list_deal]
        mat_volume = [[0 for _ in self.list_deal] for _ in self.list_deal]
        for i in range(len(self.list_deal)):
            for j in range(len(self.list_deal)):
                ((pos_x_i, pos_y_i), (item_sell_i, num_sell_i), (item_buy_i, num_buy_i)) = self.list_deal[i]
                ((pos_x_j, pos_y_j), (item_sell_j, num_sell_j), (item_buy_j, num_buy_j)) = self.list_deal[j]

                # jump over same deals
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

        :return: list_match:  matching list, (deal index, deal index)
        """

        # parameters
        num_deal = len(self.list_deal)
        mat_if_match = self.mat_if_match
        mat_volume = self.mat_volume

        solver = pywraplp.Solver(
            name='location',
            problem_type=pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

        # variable: if choose a match
        x = [[solver.BoolVar('x_{}_{}'.format(i, j)) for j in range(num_deal)]
             for i in range(num_deal)]

        # constraint: validation
        for i in range(num_deal):
            for j in range(num_deal):
                solver.Add(x[i][j] <= mat_if_match[i][j])

        # constraint: symmetry
        for i in range(num_deal):
            for j in range(num_deal):
                solver.Add(x[i][j] == x[j][i])

        # constraint: match only once
        for i in range(num_deal):
            solver.Add(sum(x[i][j] for j in range(num_deal)) <= 1)

        # objective: maximise the total trading volume
        solver.Maximize(
            sum(
                sum(mat_volume[i][j] * x[i][j] / 2 for j in range(num_deal))
                for i in range(num_deal)))

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
            x_ = [[x[i][j].solution_value() for j in range(num_deal)]
                  for i in range(num_deal)]

            # result
            for i in range(num_deal):
                for j in range(num_deal):
                    if j > i and x_[i][j] > 0.9:
                        list_match.append((i, j))
                        logger.debug(f"Deal {i} matches {j} with trading volume {mat_volume[i][j]}")
            logger.debug(f"Matched deals: {len(list_match) * 2}  Total deals: {num_deal}")

        # case 2: infeasible
        elif status == pywraplp.Solver.INFEASIBLE:
            raise Exception("Ineasible!")

        # case 3: others
        else:
            raise Exception("Unexpected status: {}!".format(status))

        return list_match