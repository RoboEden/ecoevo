
from typing import Dict, Tuple

from ecoevo import types as tp
from ecoevo.entities import ALL_ITEM_DATA


class Analyser(object):
    def __init__(self) -> None:
        pass

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
