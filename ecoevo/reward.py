from typing import Dict

import numpy as np

from ecoevo.config import RewardConfig as rc
from ecoevo.entities import ALL_ITEM_DATA, ALL_PERSONAE, Player


def cal_utility(volumes: Dict[str, int]) -> float:
    u = 0
    for item_name, volume in volumes.items():
        volume /= 10
        u += np.log(volume + 1)

    return u


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
