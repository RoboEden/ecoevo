from typing import Dict

import numpy as np

from ecoevo.config import RewardConfig as rc
from ecoevo.entities import ALL_ITEM_DATA, ALL_PERSONAE, Player


def cal_utility(volumes: Dict[str, int]) -> float:
    """
    calculate total utility

    :param volumes:  count dict based on item names

    :return: utility:  total utility
    """

    # lists of different type of items
    list_dis_nec = [
        item for item in ALL_ITEM_DATA if ALL_ITEM_DATA[item]['disposable'] and not ALL_ITEM_DATA[item]['luxury']
    ]
    list_dis_lux = [
        item for item in ALL_ITEM_DATA if ALL_ITEM_DATA[item]['disposable'] and ALL_ITEM_DATA[item]['luxury']
    ]
    list_dur_nec = [
        item for item in ALL_ITEM_DATA if not ALL_ITEM_DATA[item]['disposable'] and not ALL_ITEM_DATA[item]['luxury']
    ]
    list_dur_lux = [
        item for item in ALL_ITEM_DATA if not ALL_ITEM_DATA[item]['disposable'] and ALL_ITEM_DATA[item]['luxury']
    ]

    utility = (sum(volumes[item]**rc.rho_nec * rc.alpha_nec
                   for item in list_dis_nec) + rc.c_dis_nec)**(rc.eta_dis_nec / rc.rho_nec)
    utility += (sum(volumes[item]**rc.rho_lux * rc.alpha_lux
                    for item in list_dis_lux) + rc.c_dis_lux)**(rc.eta_dis_lux / rc.rho_lux)
    utility += (sum(volumes[item] for item in list_dur_nec) + rc.c_dur_nec)**rc.eta_dur_nec * rc.lambda_nec
    utility += (sum(volumes[item] for item in list_dur_lux) + rc.c_dur_lux)**rc.eta_dur_lux * rc.lambda_lux
    utility -= rc.c_base

    return utility


class RewardParser:

    def __init__(self) -> None:
        self.player_types = list(ALL_PERSONAE.keys())
        self.item_names = list(ALL_ITEM_DATA.keys())

        self.last_utilities = {}
        self.last_costs = {}
        self.total_costs = {}

    def reset(self) -> None:
        self.last_utilities = {}
        self.last_costs = {}
        self.total_costs = {}

    def utility(self, player: Player) -> float:
        volumes = {}
        for _, item_name in enumerate(self.item_names):
            volumes[item_name] = player.stomach[item_name].num * player.stomach[item_name].capacity

        return cal_utility(volumes=volumes)

    def cost(self, player: Player) -> float:
        penalty_flag = player.health <= rc.threshold
        cost = rc.weight_coef * player.backpack.used_volume + penalty_flag * rc.penalty
        return cost

    def parse(self, player: Player) -> float:
        # utility
        u = self.utility(player)
        last_u = self.last_utilities[player.id] if player.id in self.last_utilities else u
        du = u - last_u
        self.last_utilities[player.id] = u

        # cost
        cost = self.cost(player)
        self.last_costs[player.id] = cost
        self.total_costs[player.id] = self.total_costs[player.id] + cost if player.id in self.total_costs else cost

        # reward
        reward = du - cost

        return reward
