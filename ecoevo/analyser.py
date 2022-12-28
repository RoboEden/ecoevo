
from typing import List, Dict, Tuple

from ecoevo import types as tp
from ecoevo.entities import Player, ALL_ITEM_DATA
from ecoevo.types import Action


class Analyser(object):
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_info(done: bool, players: List[Player], dict_reward_info: Dict[int, Dict], matched_deals: Dict[
        tp.IdType, tp.DealType], actions_valid: Dict[int, Tuple[str, str]]) -> Dict[str, int or float]:
        """
        tarder parser

        :param done:  if episode done
        :param players:  list of all players
        :param dict_reward_info:  reward info dictionary: rewards, utilities and costs
        :param matched_deals:  matched deals
        :param actions_valid:  validated actions dictionary, player id to action tuple

        :return: info:  info of current step
        """

        rewards = {pid: dict_reward_info[pid]['reward'] for pid in dict_reward_info}
        utilities = {pid: dict_reward_info[pid]['utility'] for pid in dict_reward_info}
        costs = {pid: dict_reward_info[pid]['cost'] for pid in dict_reward_info}

        info = {}
        info['sum_reward'] = sum(rewards.values())
        info['sum_cost'] = sum(costs.values())

        # trade info
        trade_times, item_trade_times, item_trade_amount = Analyser.get_trade_data(matched_deals=matched_deals)
        info['trade_times'] = trade_times
        for item in ALL_ITEM_DATA.keys():
            info['{}_trade_times'.format(item)] = item_trade_times[item]
        for item in ALL_ITEM_DATA.keys():
            info['{}_trade_amount'.format(item)] = item_trade_amount[item]

        # consume times
        for item in ALL_ITEM_DATA.keys():
            info['{}_consume_times'.format(item)] = 0
        for pid in actions_valid:
            (action_type, action_item) = actions_valid[pid]
            if action_type == Action.consume:
                info['{}_consume_times'.format(action_item)] += 1

        # final consume amount
        for item in ALL_ITEM_DATA.keys():
            info['{}_final_consume_amount'.format(item)] = 0
        if done:
            for player in players:
                for item in ALL_ITEM_DATA.keys():
                    info['{}_final_consume_amount'.format(item)] += player.stomach[item].num

        # final utility
        info['final_avr_utility'], info['final_max_utility'], info['final_min_utility'] = 0, 0, 0
        if done:
            info['final_avr_utility'] = sum(utilities.values()) / len(players)
            info['final_max_utility'] = max(utilities.values())
            info['final_min_utility'] = min(utilities.values())

        return info

    @staticmethod
    def get_trade_data(matched_deals: Dict[tp.IdType, tp.DealType]) -> Tuple[int, Dict[str, int], Dict[str, int]]:
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
