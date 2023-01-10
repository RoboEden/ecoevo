import math
import random
from datetime import datetime
from typing import Dict, List, Tuple

from loguru import logger
from ortools.linear_solver import pywraplp
from ecoevo.entities.player import Player
from ecoevo.types import Action, TradeResult, IdType, OfferType, DealType, ActionType
from ecoevo.entities import ALL_ITEM_DATA


class Trader(object):
    """
    trader
    """

    def __init__(self, trade_radius: int, mode='heu') -> None:
        """
        trader, initialise

        :param trade_radius:  trade radius
        """

        self.trade_radius = trade_radius
        self.mode = mode  # 'heu'/'ip' heuristic method/ IP mode

        # env info
        # self.players: List[Player] = []
        # self.actions: List[ActionType] = []
        # self.legal_deals: Dict[IdType, DealType] = {}

        # result: matched deals, DealType
        self.match_deals = {}
        # result: actual item flows during the trades
        self.dict_flow = {}

    def parse(self, players: List[Player], actions: List[ActionType]) -> Dict[IdType, DealType]:
        """
        tarder parser

        :param players:  list of players
        :param actions:  list of actions

        :return: match_deals:  result of matched deals
        """
        self.legal_deals = self._get_legal_deals()
        if self.mode == 'IP':
            match_deals, dict_flow = self._ip()
        else:
            match_deals, dict_flow = self._heuristic()
        self.dict_flow = dict_flow
        return self.match_deals

    def _ip(self):
        match_deals = {}
        dict_flow = {}
        list_deal = list(self.legal_deals.values())
        mat_if_match, mat_volume = self._ip_process(list_deal=list_deal)
        list_match = self._ip_model(list_deal=list_deal, mat_if_match=mat_if_match, mat_volume=mat_volume)

        # result process
        idx2key = list(self.legal_deals.keys())
        for match in list_match:
            idx_1, idx_2 = match
            key_1, key_2 = idx2key[idx_1], idx2key[idx_2]
            deal_1, deal_2 = self.legal_deals[key_1], self.legal_deals[key_2]

            min_deal_1, min_deal_2 = self._mini_close(deal_1=deal_1, deal_2=deal_2)
            match_deals[key_1], match_deals[key_2] = min_deal_1, min_deal_2

            _, (sell_name_1, sell_num_1), (buy_name_1, buy_num_1) = min_deal_1
            dict_flow[key_1, key_2] = ((sell_name_1, sell_num_1), (buy_name_1, -buy_num_1))
        return match_deals, dict_flow

    def _get_legal_deals(self) -> Dict[IdType, DealType]:
        """
        tarder parser

        :return: legal_deals:  dict of legal deals, player ID to deal
        """

        legal_deals = {}
        for player in self.players:
            main_action, sell_offer, buy_offer = self.actions[player.id]
            primary_action, secondary_action = main_action

            # parse offer
            if sell_offer is None or buy_offer is None:
                player.trade_result = TradeResult.absent
                continue

            sell_item_name, sell_num = sell_offer
            buy_item_name, buy_num = buy_offer
            if sell_item_name == buy_item_name:
                player.trade_result = TradeResult.illegal
                logger.debug(f'Invalid: sell item is the same as buy item {sell_item_name}')
                continue
            if sell_num >= 0:
                player.trade_result = TradeResult.illegal
                logger.debug(f'Invalid sell_num {sell_num}, should be < 0')
                continue
            if buy_num <= 0:
                player.trade_result = TradeResult.illegal
                logger.debug(f'Invalid buy_num {buy_num}, should be > 0')
                continue
            sell_num, buy_num = abs(sell_num), abs(buy_num)

            # check sell
            sell_item = player.backpack[sell_item_name]

            # handle sell and consume same item
            least_amount = sell_num
            if primary_action == Action.consume:
                consume_item_name = secondary_action
                if sell_item_name == consume_item_name:
                    least_amount += sell_item.consume_num

            if sell_item.num < least_amount:
                logger.debug(f'Insufficient {sell_item_name}: {sell_item.num} sell_num {sell_num}')
                player.trade_result = TradeResult.illegal
                continue

            # check buy
            buy_item_volumne = player.backpack[buy_item_name].capacity * buy_num
            if player.backpack.remain_volume < buy_item_volumne:
                player.trade_result = TradeResult.illegal
                logger.debug(f'Insufficient backpack remain volume: {player.backpack.remain_volume}')
                continue

            legal_deals[player.id] = (player.pos, sell_offer, buy_offer)

        return legal_deals

    def _ip_process(self, list_deal: List[DealType]) -> Tuple[List[List[bool]], List[List[int]]]:
        """
        data process for IP model

        :param list_deal:  list of legal deals

        :return: mat_if_match:  available matching matrix
        :return: mat_volume:  trading volume matrix
        """

        mat_if_match = [[False for _ in list_deal] for _ in list_deal]
        mat_volume = [[0 for _ in list_deal] for _ in list_deal]
        for i in range(len(list_deal)):
            for j in range(len(list_deal)):
                ((pos_x_i, pos_y_i), (item_sell_i, num_sell_i), (item_buy_i, num_buy_i)) = list_deal[i]
                ((pos_x_j, pos_y_j), (item_sell_j, num_sell_j), (item_buy_j, num_buy_j)) = list_deal[j]

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

    def _ip_model(self, list_deal: List[DealType], mat_if_match: List[List[bool]],
                  mat_volume: List[List[int]]) -> List[Tuple[int, int]]:
        """
        IP model for automated trade matching

        :param list_deal:  list of legal deals
        :param mat_if_match:  available matching matrix
        :param mat_volume:  trading volume matrix

        :return: list_match:  matching list, (deal index, deal index)
        """

        # parameters
        num_deal = len(list_deal)

        solver = pywraplp.Solver(name='location', problem_type=pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

        # variable: if choose a match
        x = [[solver.BoolVar('x_{}_{}'.format(i, j)) for j in range(num_deal)] for i in range(num_deal)]

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
        solver.Maximize(sum(sum(mat_volume[i][j] * x[i][j] / 2 for j in range(num_deal)) for i in range(num_deal)))

        # solve
        dts = datetime.now()
        status = solver.Solve()
        dte = datetime.now()
        tm = round((dte - dts).seconds + (dte - dts).microseconds / (10**6), 3)
        logger.debug(f"trading model solving time: {tm}s")

        # case 1: optimal
        list_match = []
        if status == pywraplp.Solver.OPTIMAL:
            obj_ = solver.Objective().Value()
            logger.debug(f"objective value: {round(obj_)}")
            x_ = [[x[i][j].solution_value() for j in range(num_deal)] for i in range(num_deal)]

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

    def _mini_close(self, deal_1: DealType, deal_2: DealType):
        """
        get deals tuple with actual trading volume

        :param deal_1:  deal 1
        :param deal_2:  deal 2

        :return: min_deal_1:  deal 1 with actual trading volume
        :return: min_deal_2:  deal 2 with actual trading volume
        """

        pos_1, (sell_name_1, sell_num_1), (buy_name_1, buy_num_1) = deal_1
        pos_2, (sell_name_2, sell_num_2), (buy_name_2, buy_num_2) = deal_2

        sell_num_1, buy_num_1 = -min(abs(sell_num_1), buy_num_2), min(abs(sell_num_2), buy_num_1)
        sell_num_2, buy_num_2 = -buy_num_1, abs(sell_num_1)

        min_deal_1 = pos_1, (sell_name_1, sell_num_1), (buy_name_1, buy_num_1)
        min_deal_2 = pos_2, (sell_name_2, sell_num_2), (buy_name_2, buy_num_2)

        return min_deal_1, min_deal_2

    def _heuristic(self) -> Tuple[Dict[IdType, DealType], Dict[Tuple[IdType, IdType], Tuple[OfferType, OfferType]]]:
        """
        heuristic method for automated trade matching

        :return: self.match_deals:  result of matched deals with actual trade amount
        :return: self.dict_flow:  actual item flows during the trades
        """

        dts = datetime.now()

        idx_pos, idx_sell, idx_buy = 0, 1, 2
        idx_item_name, idx_item_num = 0, 1

        # deal infos during processing, transfer tuples to lists
        dict_deal = {}
        for i in self.legal_deals:
            dict_deal[i] = [
                list(self.legal_deals[i][idx_pos]),
                list(self.legal_deals[i][idx_sell]),
                list(self.legal_deals[i][idx_buy])
            ]

        self.dict_flow = {}

        random.seed(42)
        list_deal_id = list(dict_deal.keys())
        list_remain_volume = [player.backpack.remain_volume for player in self.players]
        random.shuffle(list_deal_id)
        for i in list_deal_id:
            (x_i, y_i), (sell_name_i, sell_num_i), (buy_name_i, buy_num_i) = dict_deal[i]

            # deal i already finished
            if sell_num_i >= 0 or buy_num_i <= 0:
                continue

            # get deal candidates
            dict_deal_match = {}
            for j in list_deal_id:
                # jump over same deals
                if j == i:
                    continue

                (x_j, y_j), (sell_name_j, sell_num_j), (buy_name_j, buy_num_j) = dict_deal[j]

                # deal j already finished
                if sell_num_j >= 0 or buy_num_j <= 0:
                    continue

                # too far to trade
                if abs(x_i - x_j) > self.trade_radius or abs(y_i - y_j) > self.trade_radius:
                    continue

                # items cannot match
                if sell_name_i != buy_name_j or buy_name_i != sell_name_j:
                    continue

                dict_deal_match[j] = dict_deal[j]

            # matching
            while sell_num_i < 0 and buy_num_i > 0:
                ratio_i = abs(sell_num_i) / buy_num_i

                # get best match deal
                pid_cur, match_ratio = None, 0
                for j in dict_deal_match:
                    (x_j, y_j), (sell_name_j, sell_num_j), (buy_name_j, buy_num_j) = dict_deal_match[j]
                    ratio_j = abs(sell_num_j) / buy_num_j
                    if ratio_i * ratio_j >= 1:
                        # get a new match deal
                        if pid_cur is None:
                            pid_cur, match_ratio = j, ratio_j

                        # may update match deal
                        else:
                            # if get a bigger supply-demand ratio, update match deal
                            if ratio_j > match_ratio:
                                pid_cur, match_ratio = j, ratio_j

                            # if get an equal supply-demand ratio, choose the nearer one
                            elif ratio_j == match_ratio:
                                (x_cur, y_cur) = dict_deal[pid_cur][idx_pos]
                                dist_cur, dist_j = abs(x_i - x_cur) + abs(y_i - y_cur), abs(x_i - x_j) + abs(y_i - y_j)
                                if dist_j < dist_cur:
                                    pid_cur, match_ratio = j, ratio_j

                # no matched deals
                if not pid_cur:
                    break

                # get trade amount
                actual_buy_num_i, actual_buy_num_cur = self._heuristic_match(deal_1=dict_deal[i],
                                                                             deal_2=dict_deal_match[pid_cur],
                                                                             remain_volume_1=list_remain_volume[i])
                dict_deal_match.pop(pid_cur)

                # update deal info
                dict_deal[i][idx_sell][idx_item_num] += actual_buy_num_cur
                dict_deal[i][idx_buy][idx_item_num] -= actual_buy_num_i
                dict_deal[pid_cur][idx_sell][idx_item_num] += actual_buy_num_i
                dict_deal[pid_cur][idx_buy][idx_item_num] -= actual_buy_num_cur
                self.dict_flow[i, pid_cur] = ((dict_deal[i][idx_sell][idx_item_name], -actual_buy_num_cur),
                                              (dict_deal[i][idx_buy][idx_item_name], -actual_buy_num_i))
                sell_num_i, buy_num_i = dict_deal[i][idx_sell][idx_item_num], dict_deal[i][idx_buy][idx_item_num]

                # update remain volumes
                capacity_i = ALL_ITEM_DATA[dict_deal[i][idx_buy][idx_item_name]]['capacity']
                capacity_cur = ALL_ITEM_DATA[dict_deal[pid_cur][idx_buy][idx_item_name]]['capacity']
                list_remain_volume[
                    i] = list_remain_volume[i] - actual_buy_num_i * capacity_i + actual_buy_num_cur * capacity_cur
                list_remain_volume[pid_cur] = list_remain_volume[
                    pid_cur] - actual_buy_num_cur * capacity_cur + actual_buy_num_i * capacity_i

        # result info
        self.match_deals = {}
        for i in self.legal_deals:
            sell_num = dict_deal[i][idx_sell][idx_item_num] - self.legal_deals[i][idx_sell][idx_item_num]
            buy_num = self.legal_deals[i][idx_buy][idx_item_num] - dict_deal[i][idx_buy][idx_item_num]
            if sell_num == 0 or buy_num == 0:
                continue

            self.match_deals[i] = (self.legal_deals[i][idx_pos], (self.legal_deals[i][idx_sell][idx_item_name],
                                                                  -sell_num),
                                   (self.legal_deals[i][idx_buy][idx_item_name], buy_num))

        dte = datetime.now()
        tm = round((dte - dts).seconds + (dte - dts).microseconds / (10**6), 3)
        logger.debug(f"heuristic processing time: {tm} s")

        return self.match_deals, self.dict_flow

    def _heuristic_match(self, deal_1: DealType, deal_2: DealType, remain_volume_1: int) -> Tuple[int, int]:
        """
        get trade amount of a couple of deals

        :param deal_1:  deal 1
        :param deal_2:  deal 2
        :param remain_volume_1:  backpack remain volume of player 1

        :return: actual_buy_num_1:  actual buy item amout of deal 1, equals to sell item amout of deal 2
        :return: actual_buy_num_2:  actual buy item amout of deal 2, equals to sell item amout of deal 1
        """

        _, (_, sell_num_1), (buy_item_1, buy_num_1) = deal_1
        _, (_, sell_num_2), (buy_item_2, buy_num_2) = deal_2
        sell_num_1, sell_num_2 = abs(sell_num_1), abs(sell_num_2)

        # use deal 2 as pivot
        actual_buy_num_2 = min(buy_num_2, sell_num_1)

        # consider remaining backpack volume of player 1
        ratio_2 = sell_num_2 / buy_num_2
        buy_num_1_ratio = math.floor(actual_buy_num_2 * ratio_2)
        capacity_1 = ALL_ITEM_DATA[buy_item_1]['capacity']
        buy_num_1_ub = math.floor(remain_volume_1 / capacity_1)
        actual_buy_num_1 = min(buy_num_1_ratio, sell_num_2, buy_num_1_ub)

        return actual_buy_num_1, actual_buy_num_2
