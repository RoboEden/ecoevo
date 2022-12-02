import numpy as np
from ecoevo.entities.player import Player
from ecoevo.entities.player import Action
from ecoevo.entities.player import ALL_PLAYER_TYPES
from ecoevo.entities.items import ALL_ITEM_TYPES
from ecoevo.config import RewardConfig


def cal_utility(alpha: np.ndarray, cnt: np.ndarray, rho: float):
    u = np.power(cnt, rho)
    u = alpha * u
    u = np.power(u, 1 / rho)
    u = np.sum(u)
    return u


class RewardParser:

    def __init__(self) -> None:
        self.player_types = list(ALL_PLAYER_TYPES.keys())
        self.item_names = list(ALL_ITEM_TYPES.keys())
        self.last_utilities = {}

        # Calculate alphas
        self.alphas = {
            player_type: np.zeros(len(self.item_names), dtype=np.float32)
            for player_type in ALL_PLAYER_TYPES
        }
        for player_type in ALL_PLAYER_TYPES:
            player_pref = ALL_PLAYER_TYPES[player_type]["preference"]
            total_pref = sum(player_pref.values())
            for idx, item_name in enumerate(self.item_names):
                item_pref = player_pref[item_name]
                alpha_i = item_pref / total_pref
                self.alphas[player_type][idx] = alpha_i

    def utility(self, player: Player):
        alpha = self.alphas[player.name]
        cnts = np.zeros(len(self.item_names), dtype=np.float32)
        for idx, item_name in enumerate(self.item_names):
            cnt_i = player.consume_cnts[item_name]
            cnts[idx] = cnt_i
        utility = cal_utility(alpha, cnts, RewardConfig.rho)
        return utility

    def parse(self, player: Player):
        # Utility
        u = self.utility(player)
        if player.id not in self.last_utilities:
            last_u = u
        else:
            last_u = self.last_utilities[player.id]
        du = u - last_u
        self.last_utilities[player.id] = u

        # Cost
        penalty_flag = player.health <= RewardConfig.threshold
        cost = RewardConfig.w * player.weight + penalty_flag * RewardConfig.penalty

        # Reward
        reward = du + cost

        return reward