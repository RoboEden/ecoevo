from typing import Dict, List, Tuple

from ecoevo.entities import ALL_ITEM_DATA, ALL_PERSONAE, EntityManager, Player
from ecoevo.types import Action, DealType, IdType, OfferType

persona_collect_cnt_key = "{}_collect_cnt"
persona_collect_match_cnt_key = "{}_collect_match_cnt"
persona_collect_match_ratio_key = "{}_collect_match_ratio"


def persona_key(key_format: str):
    return [key_format.format(persona) for persona in ALL_PERSONAE]


def item_key(key_format: str):
    return [key_format.format(item) for item in ALL_ITEM_DATA]


def different_item_pair_key(key_format: str):
    r = []
    for a in ALL_ITEM_DATA:
        for b in ALL_ITEM_DATA:
            if a != b:
                r.append(key_format.format(a, b))
    return r


class Analyser(object):
    # keys
    info_keys = ['curr_step', 'trade_times'] + \
                ['final_avr_utility', 'final_max_utility', 'final_min_utility'] + \
                ['final_avr_cost', 'final_max_cost', 'final_min_cost'] + \
                item_key('{}_trade_times') + item_key('{}_trade_amount') + \
                item_key('{}_consume_times') + item_key('{}_final_consume_amount')

    trade_result_keys = [f"avr_{trade_result}_per_step" for trade_result in ['absent', 'illegal', 'failed', 'success']]
    info_keys += trade_result_keys

    info_keys += different_item_pair_key('{}_{}_price')
    info_keys += different_item_pair_key('{}_{}_cnt')
    info_keys += persona_key(persona_collect_cnt_key)
    info_keys += persona_key(persona_collect_match_cnt_key)
    info_keys += persona_key(persona_collect_match_ratio_key)

    def get_info(self, step: int, done: bool, info: Dict[str, int or float], players: List[Player],
                 entity_manager: EntityManager, matched_deals: Dict[IdType, DealType],
                 transaction_graph: Dict[Tuple[IdType, IdType], OfferType],
                 executed_main_actions: Dict[int, Tuple[str, str]], reward_info: Dict[int,
                                                                                      Dict]) -> Dict[str, int or float]:
        """
        get infos

        :param step:  current step
        :param done:  if episode done
        :param info:  info of last step
        :param players:  list of all players
        :param transaction_graph:  trade item flows
        :param actions_valid:  validated actions dictionary, player id to action tuple
        :param reward_info:  reward info dictionary: rewards, utilities and costs

        :return: info:  info of current step
        """

        for key in self.info_keys:
            if key not in info:
                info[key] = 0

        info['curr_step'] = step

        num_player = len(players)

        # trade info
        trade_times, item_trade_times, item_trade_amount = Analyser.get_trade_data(transaction_graph=transaction_graph)
        info['trade_times'] += trade_times / num_player
        for item in ALL_ITEM_DATA.keys():
            info['{}_trade_times'.format(item)] += item_trade_times[item] / num_player
        for item in ALL_ITEM_DATA.keys():
            info['{}_trade_amount'.format(item)] += item_trade_amount[item] / num_player

        # trade result
        for player in players:
            info_key = f"avr_{player.trade_result}_per_step"
            info[info_key] += 1

        # price info
        for id, deal in matched_deals.items():
            _, sell_offer, buy_offer = deal
            sell_name, sell_num = sell_offer
            buy_name, buy_num = buy_offer

            price = abs(buy_num) / abs(sell_num)
            price_key = f"{buy_name}_{sell_name}_price"
            info[price_key] += price

            cnt_key = f"{buy_name}_{sell_name}_cnt"
            info[cnt_key] += 1

        if done:
            for key in self.trade_result_keys:
                info[key] /= info['curr_step']

            for buy_item_name in ALL_ITEM_DATA:
                for sell_item_name in ALL_ITEM_DATA:
                    if buy_item_name == sell_item_name:
                        continue
                    price_key = f"{buy_item_name}_{sell_item_name}_price"
                    cnt_key = f"{buy_item_name}_{sell_item_name}_cnt"
                    cnt = info[cnt_key]
                    if cnt > 0:
                        info[price_key] /= cnt

        for pid in executed_main_actions:
            (action_type, action_item) = executed_main_actions[pid]
            # consume times
            if action_type == Action.consume:
                info['{}_consume_times'.format(action_item)] += 1 / num_player

            # persona collect info
            player = players[pid]
            if action_type == Action.collect and player.collect_remain is None:
                cnt_key = persona_collect_cnt_key.format(player.persona)
                info[cnt_key] += 1

                tile = entity_manager.map[player.pos]
                if tile.item is None:
                    continue
                ability = player.ability[tile.item.name]
                min_ability = min(player.ability.values())
                if ability == min_ability:
                    match_cnt_key = persona_collect_match_cnt_key.format(player.persona)
                    info[match_cnt_key] += 1

        if done:
            # final consume amount
            for player in players:
                for item in ALL_ITEM_DATA.keys():
                    info['{}_final_consume_amount'.format(item)] += player.stomach[item].num / num_player

            # persona collect match ratio
            for persona in ALL_PERSONAE:
                cnt_key = persona_collect_cnt_key.format(persona)
                match_cnt_key = persona_collect_match_cnt_key.format(persona)
                match_ratio_key = persona_collect_match_ratio_key.format(persona)
                if info[cnt_key] > 0:
                    info[match_ratio_key] = info[match_cnt_key] / info[cnt_key]

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
    def get_trade_data(
            transaction_graph: Dict[Tuple[IdType, IdType], OfferType]) -> Tuple[int, Dict[str, int], Dict[str, int]]:
        """
        tarder parser

        :param transaction_graph:  trade item flows

        :return: trade_times:  total trade times
        :return: item_trade_times:  trade times of each item
        :return: item_trade_amount:  trade amount of each item
        """

        # the number of trades
        trade_times = len(transaction_graph) // 2

        # trade times and amounts of each items
        list_item = list(ALL_ITEM_DATA.keys())
        item_trade_times, item_trade_amount = {item: 0 for item in list_item}, {item: 0 for item in list_item}
        for (i, j), (item_name, item_num) in transaction_graph.items():
            item_trade_times[item_name] += 1
            item_trade_amount[item_name] += item_num

        return trade_times, item_trade_times, item_trade_amount
