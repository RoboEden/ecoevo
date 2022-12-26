
from typing import Dict, Tuple

from ecoevo import types as tp
from ecoevo.entities import ALL_ITEM_DATA
from ecoevo.types import Action


class Analyser(object):
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_info(rewards: Dict[int, float], matched_deals: Dict[
        tp.IdType, tp.DealType], actions_valid: Dict[int, Tuple[str, str]]) -> Dict[str, int or float]:
        """
        tarder parser

        :param rewards:  rewards dictionary, player id to reward
        :param matched_deals:  matched deals
        :param actions_valid:  validated actions dictionary, player id to action tuple

        :return: trade_times:  total trade times
        """

        info = {}

        sum_reward = sum(rewards.values())
        info['sum_reward'] = sum_reward

        # trade info
        trade_times, item_trade_times, item_trade_amount = Analyser.get_trade_data(matched_deals=matched_deals)
        info['trade_times'] = trade_times
        for item in ALL_ITEM_DATA.keys():
            info['{}_trade_times'.format(item)] = item_trade_times[item]
        for item in ALL_ITEM_DATA.keys():
            info['{}_trade_amount'.format(item)] = item_trade_amount[item]

        # food consume times
        food_consume = 0
        for pid in actions_valid:
            (action_type, action_item) = actions_valid[pid]
            if action_type == Action.consume and bool(ALL_ITEM_DATA[action_item]['disposable']):
                food_consume += 1
        info['food_consume'] = food_consume

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
