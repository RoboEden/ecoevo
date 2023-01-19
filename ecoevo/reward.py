from typing import Dict

import numpy as np

from ecoevo.config import RewardConfig as rc
from ecoevo.entities import ALL_ITEM_DATA, ALL_PERSONAE, Player
from ecoevo.types import TradeResult


def cal_utility(volumes: Dict[str, int]) -> float:
    """
    calculate total utility, log method

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

    utility = (sum(
        (volumes[item] + 100)**rc.rho_nec * rc.alpha_nec
        for item in list_dis_nec) + rc.c_dis_nec)**(rc.eta_dis_nec / rc.rho_nec) - (sum(
            (100)**rc.rho_nec * rc.alpha_nec for item in list_dis_nec) + rc.c_dis_nec)**(rc.eta_dis_nec / rc.rho_nec)
    utility += (sum(
        (volumes[item] + 100)**rc.rho_lux * rc.alpha_lux
        for item in list_dis_lux) + rc.c_dis_lux)**(rc.eta_dis_lux / rc.rho_lux) - (sum(
            (100)**rc.rho_lux * rc.alpha_lux for item in list_dis_lux) + rc.c_dis_lux)**(rc.eta_dis_lux / rc.rho_lux)
    utility += (sum(volumes[item] for item in list_dur_nec) +
                rc.c_dur_nec)**rc.eta_dur_nec * rc.lambda_nec - (rc.c_dur_nec)**rc.eta_dur_nec * rc.lambda_nec
    utility += (sum(volumes[item] for item in list_dur_lux) +
                rc.c_dur_lux)**rc.eta_dur_lux * rc.lambda_lux - (rc.c_dur_nec)**rc.eta_dur_nec * rc.lambda_nec

    return utility


def cal_utility_log(volumes: Dict[str, int], den: int = 10, coef_disposable: int = 2, coef_luxury: int = 1) -> float:
    """
    calculate total utility, log method

    :param volumes:  count dict based on item names
    :param den:  denominator of volumes
    :param coef_disposable:  magnification times of disposable items
    :param coef_luxury:  magnification times of luxury item volumes

    :return: utility:  total utility
    """

    utility = 0
    for item, vol in volumes.items():
        vol /= den
        vol *= coef_luxury if ALL_ITEM_DATA[item]['luxury'] else 1
        u = np.log(vol + 1) * coef_disposable if ALL_ITEM_DATA[item]['disposable'] else np.log(vol + 1)
        utility += u

    return utility


class RewardParser:

    def __init__(self) -> None:
        self.player_types = list(ALL_PERSONAE.keys())
        self.item_names = list(ALL_ITEM_DATA.keys())

        self.last_utilities = {}
        self.last_costs = {}
        self.total_costs = {}

        # utility calculation method
        self.ultility_mode = 'base'
        # self.ultility_mode = 'log'

    def reset(self) -> None:
        self.last_utilities = {}
        self.last_costs = {}
        self.total_costs = {}

    def utility(self, player: Player) -> float:
        volumes = {}
        for _, item_name in enumerate(self.item_names):
            volumes[item_name] = player.stomach[item_name].num * player.stomach[item_name].capacity

        utility = cal_utility_log(volumes=volumes, coef_disposable=3,
                                  coef_luxury=3) if self.ultility_mode == 'log' else cal_utility(volumes=volumes)

        return utility

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
