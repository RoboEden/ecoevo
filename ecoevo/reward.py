import numpy as np
from ecoevo.entities import Player, ALL_PERSONAE, ALL_ITEM_DATA
from ecoevo.config import RewardConfig


def cal_utility(alpha: np.ndarray, cnt: np.ndarray, rho: float) -> float:
    u = np.power(cnt, rho)
    u = alpha * u
    u = np.sum(u)
    u = np.power(u, 1 / rho)
    return u


class RewardParser:

    def __init__(self) -> None:
        self.player_types = list(ALL_PERSONAE.keys())
        self.item_names = list(ALL_ITEM_DATA.keys())

        # get alphas
        self.alphas = {
            player_type: np.array([ALL_PERSONAE[
                player_type]["preference"][item_name] for item_name in self.item_names], dtype=np.float32)
            for player_type in ALL_PERSONAE
        }

        self.last_utilities = {}
        self.last_costs = {}
        self.total_costs = {}

    def reset(self) -> None:
        self.last_utilities = {}
        self.last_costs = {}
        self.total_costs = {}

    def utility(self, player: Player) -> float:
        alpha = self.alphas[player.persona]
        cnts = np.zeros(len(self.item_names), dtype=np.float32)
        for idx, item_name in enumerate(self.item_names):
            cnts[idx] = player.stomach[item_name].num * player.stomach[item_name].capacity
        return cal_utility(alpha, cnts, RewardConfig.rho)

    def cost(self, player: Player) -> float:
        penalty_flag = player.health <= RewardConfig.threshold
        cost = RewardConfig.weight_coef * player.backpack.used_volume + penalty_flag * RewardConfig.penalty
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