from typing import Dict, List, Tuple

from ecoevo.entities import ALL_ITEM_DATA, Player
from ecoevo.types import Action, DealType, IdType, TradeResult


class Analyser(object):

    def __init__(self) -> None:
        pass

    @staticmethod
    def get_info(done: bool, info: Dict[str, int or float], players: List[Player],
                 matched_deals: Dict[IdType, DealType], executed_main_actions: Dict[int, Tuple[str, str]],
                 reward_info: Dict[int, Dict]) -> Dict[str, int or float]:
        """
        :param done:  if episode done
        :param info:  info of last step
        :param players:  list of all players
        :param matched_deals:  matched deals
        :param actions_valid:  validated actions dictionary, player id to action tuple
        :param reward_info:  reward info dictionary: rewards, utilities and costs

        :return: info:  info of current step
        """

        # check keys
        info_keys = ['curr_step'] + \
                    ['trade_times'] + \
                    ['{}_trade_times'.format(item) for item in ALL_ITEM_DATA.keys()] + \
                    ['{}_trade_amount'.format(item) for item in ALL_ITEM_DATA.keys()] + \
                    ['{}_consume_times'.format(item) for item in ALL_ITEM_DATA.keys()] + \
                    ['{}_final_consume_amount'.format(item) for item in ALL_ITEM_DATA.keys()] + \
                    ['final_avr_utility', 'final_max_utility', 'final_min_utility'] + \
                    ['final_avr_cost', 'final_max_cost', 'final_min_cost']
        trade_result_keys = [
            f"avr_{trade_result}_per_step" for trade_result in ['absent', 'illegal', 'failed', 'success']
        ]
        info_keys += trade_result_keys

        for key in info_keys:
            if key not in info:
                info[key] = 0

        num_player = len(players)

        # trade info
        trade_times, item_trade_times, item_trade_amount = Analyser.get_trade_data(matched_deals=matched_deals)
        info['trade_times'] += trade_times / num_player
        for item in ALL_ITEM_DATA.keys():
            info['{}_trade_times'.format(item)] += item_trade_times[item] / num_player
        for item in ALL_ITEM_DATA.keys():
            info['{}_trade_amount'.format(item)] += item_trade_amount[item] / num_player

        # trade result
        for player in players:
            info_key = f"avr_{player.trade_result}_per_step"
            info[info_key] += 1

        if done:
            for key in trade_result_keys:
                info[key] /= info['curr_step'] + 1

        # consume times
        for pid in executed_main_actions:
            (action_type, action_item) = executed_main_actions[pid]
            if action_type == Action.consume:
                info['{}_consume_times'.format(action_item)] += 1 / num_player

        # final consume amount
        if done:
            for player in players:
                for item in ALL_ITEM_DATA.keys():
                    info['{}_final_consume_amount'.format(item)] += player.stomach[item].num / num_player

        # final utility
        utilities = {pid: reward_info[pid]['utility'] for pid in reward_info}
        costs = {pid: reward_info[pid]['cost'] for pid in reward_info}
        if done:
            info['final_avr_utility'] = sum(utilities.values()) / len(players)
            info['final_max_utility'] = max(utilities.values())
            info['final_min_utility'] = min(utilities.values())
            info['final_avr_cost'] = sum(costs.values()) / len(players)
            info['final_max_cost'] = max(costs.values())
            info['final_min_cost'] = min(costs.values())

        return info

    @staticmethod
    def get_trade_data(matched_deals: Dict[IdType, DealType]) -> Tuple[int, Dict[str, int], Dict[str, int]]:
        """
        tarder parser

        :param matched_deals:  matched deals

        :return: trade_times:  total trade times
        :return: item_trade_times:  trade times of each item
        :return: item_trade_amount:  trade amount of each item
        """

        # the number of trades
        trade_times = round(len(matched_deals) / 2)

        # trade times and amounts of each items
        list_item = list(ALL_ITEM_DATA.keys())
        item_trade_times, item_trade_amount = {item: 0 for item in list_item}, {item: 0 for item in list_item}
        for player_id in matched_deals:
            _, _, (buy_name, buy_num) = matched_deals[player_id]
            item_trade_times[buy_name] += 1
            item_trade_amount[buy_name] += buy_num

        return trade_times, item_trade_times, item_trade_amount
