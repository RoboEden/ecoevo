from collections import defaultdict

from ecoevo.config import RewardConfig as rc
from ecoevo.config import PlayerConfig
from ecoevo.entities import ALL_ITEM_DATA, ALL_PERSONAE, Player
from ecoevo.types import MainActionType
import numpy as np


def cal_utility(x: np.ndarray, p: float = -5.0, mask=None) -> float:
    if mask is None:
        mask = np.ones_like(x)
    u = x[mask == 1]
    u += 1
    u = np.mean(np.power(u, p))
    u = np.power(u, 1 / p)
    return u


class RewardParser:

    def __init__(self) -> None:
        self.player_types = list(ALL_PERSONAE.keys())
        self.item_names = list(sorted(ALL_ITEM_DATA.keys()))
        self.reset()

    def reset(self):
        dummy = np.zeros(len(self.item_names), )
        self.last_utilities = defaultdict(lambda: cal_utility(dummy))
        self.last_item_utilities = defaultdict(lambda: {k: 0 for k in self.item_names})
        self.last_costs = {}
        self.total_costs = {}

    def utility(
        self,
        player: Player,
        coef_volume: float = 0.01,
        coef_luxury: float = 1.0,
    ) -> float:
        if player.last_action.main_action.primary != "consume":
            return self.last_utilities[player.id]

        volume = np.zeros(len(self.item_names))
        for i, item_name in enumerate(self.item_names):
            item = player.x_stomach[item_name]
            volume[i] = coef_volume * item.num * item.capacity
            if item.luxury:
                volume[i] *= coef_luxury

        utility = cal_utility(volume, mask=None)
        return utility

    def cost(self, player: Player) -> float:
        c = 0
        if player.last_action.main_action.primary == "consume":
            c += rc.consume_penalty
        return c

    def parse(self, player: Player) -> float:
        # reward
        utility = self.utility(player)
        reward = utility - self.last_utilities[player.id]
        self.last_utilities[player.id] = utility

        # cost
        cost = self.cost(player)
        self.last_costs[player.id] = cost
        self.total_costs[player.id] = self.total_costs[player.id] + cost if player.id in self.total_costs else cost

        reward = reward + cost

        return reward