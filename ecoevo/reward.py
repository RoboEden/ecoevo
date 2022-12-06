import numpy as np
from ecoevo.entities.player import Player
from ecoevo.entities.player import ALL_PERSONAE
from ecoevo.entities.items import ALL_ITEM_TYPES
from ecoevo.config import RewardConfig


def cal_utility(alpha: np.ndarray, cnt: np.ndarray, rho: float):
    u = np.power(cnt, rho)
    u = alpha * u
    u = np.sum(u)
    u = np.power(u, 1 / rho)
    return u


class RewardParser:

    def __init__(self) -> None:
        self.player_types = list(ALL_PERSONAE.keys())
        self.item_names = list(ALL_ITEM_TYPES.keys())
        self.last_utilities = {}

        # Calculate alphas
        self.alphas = {
            player_type: np.zeros(len(self.item_names), dtype=np.float32)
            for player_type in ALL_PERSONAE
        }
        for player_type in ALL_PERSONAE:
            player_pref = ALL_PERSONAE[player_type]["preference"]
            total_pref = sum(player_pref.values())
            for idx, item_name in enumerate(self.item_names):
                item_pref = player_pref[item_name]
                alpha_i = item_pref / total_pref
                self.alphas[player_type][idx] = alpha_i

    def utility(self, player: Player):
        alpha = self.alphas[player.persona]
        cnts = np.zeros(len(self.item_names), dtype=np.float32)
        for idx, item_name in enumerate(self.item_names):
            cnts[idx] = player.stomach.get_item(item_name).num
        utility = cal_utility(alpha, cnts, RewardConfig.rho)
        return utility

    def cost(self, player: Player):
        penalty_flag = player.health <= RewardConfig.threshold
        cost = RewardConfig.weight_coef * player.backpack.used_volume + penalty_flag * RewardConfig.penalty
        return cost

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
        cost = self.cost(player)

        # Reward
        reward = du - cost

        return reward