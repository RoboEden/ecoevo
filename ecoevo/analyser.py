from typing import Dict, List, Tuple

import numpy as np

from ecoevo.entities import ALL_ITEM_DATA, ALL_PERSONAE, EntityManager, Player
from ecoevo.types import Action, IdType, ItemNumType

persona_collect_cnt_key = "{}_collect_cnt"
persona_collect_match_cnt_key = "{}_collect_match_cnt"
persona_collect_match_ratio_key = "{}_collect_match_ratio"
item_final_utility_avg_key = "{}_final_utility_avg"
item_final_utility_std_key = "{}_final_utility_std"
final_iustd_avg_key = "final_iustd_avg"
final_iustd_std_key = "final_iustd_std"
final_iustd_min_key = "final_iustd_min"
final_iustd_max_key = "final_iustd_max"


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
                item_key('{}_consume_times') + item_key('{}_final_consume_amount') + \
                item_key(item_final_utility_avg_key) + item_key(item_final_utility_std_key) + \
                [final_iustd_avg_key, final_iustd_std_key, final_iustd_min_key, final_iustd_max_key]

    trade_result_keys = [f"avr_{trade_result}_per_step" for trade_result in ['absent', 'illegal', 'failed', 'success']]
    info_keys += trade_result_keys

    info_keys += different_item_pair_key('{}_{}_price')
    info_keys += different_item_pair_key('{}_{}_cnt')
    info_keys += different_item_pair_key('{}_{}_amount')
    info_keys += persona_key(persona_collect_cnt_key)
    info_keys += persona_key(persona_collect_match_cnt_key)
    info_keys += persona_key(persona_collect_match_ratio_key)

    def get_info(self, step: int, done: bool, info: Dict[str, int or float], players: List[Player],
                 entity_manager: EntityManager, transaction_graph: Dict[Tuple[IdType, IdType], ItemNumType],
                 executed_main_actions: Dict[int, Tuple[str, str]], reward_info: Dict[int,
                                                                                      Dict]) -> Dict[str, int or float]:
        """
        get info

        :param step:  current step
        :param done:  if episode done
        :param info:  info of last step
        :param players:  list of all players
        :param entity_manager:  entity manager
        :param transaction_graph:  trade item flows
        :param executed_main_actions:  validated actions dictionary, player id to action tuple
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
        for i, j in transaction_graph.keys():
            (sell_item, sell_num), (buy_item, buy_num) = transaction_graph[i, j], transaction_graph[j, i]
            price = buy_num / sell_num
            price_key = f"{buy_item}_{sell_item}_price"
            info[price_key] += price

            cnt_key = f"{buy_item}_{sell_item}_cnt"
            info[cnt_key] += 1

            amount_key = f"{buy_item}_{sell_item}_amount"
            info[amount_key] += sell_num

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
            if action_type == Action.collect and player.collect_remain == 0:
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

            # item final utility avg and std
            for item in ALL_ITEM_DATA:
                item_final_utility = np.array([r['item_utility'][item] for r in reward_info.values()])
                info[item_final_utility_avg_key.format(item)] = np.mean(item_final_utility).item()
                info[item_final_utility_std_key.format(item)] = np.std(item_final_utility).item()

            # player final iustd(item utility std)
            player_final_iustd = np.array([np.std(list(r['item_utility'].values())) for r in reward_info.values()])
            info[final_iustd_avg_key] = np.mean(player_final_iustd).item()
            info[final_iustd_std_key] = np.std(player_final_iustd).item()
            info[final_iustd_min_key] = np.amin(player_final_iustd).item()
            info[final_iustd_max_key] = np.amax(player_final_iustd).item()

            # final utility
            player_final_utility = np.array([r['utility'] for r in reward_info.values()])
            player_final_cost = np.array([r['cost'] for r in reward_info.values()])
            info['final_avr_utility'] = np.mean(player_final_utility).item()
            info['final_max_utility'] = np.amax(player_final_utility).item()
            info['final_min_utility'] = np.amin(player_final_utility).item()
            info['final_avr_cost'] = np.mean(player_final_cost).item()
            info['final_max_cost'] = np.amax(player_final_cost).item()
            info['final_min_cost'] = np.amin(player_final_cost).item()

        return info

    @staticmethod
    def get_trade_data(
            transaction_graph: Dict[Tuple[IdType, IdType], ItemNumType]) -> Tuple[int, Dict[str, int], Dict[str, int]]:
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
