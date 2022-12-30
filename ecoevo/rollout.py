from typing import List
from ecoevo.env import EcoEvo
from ecoevo.types import ActionType

class RollOut:

    def __init__(self):
        self.env: EcoEvo = None

    def get_current_obs(self):
        assert self.env is not None, "Attr 'env' is None."
        obs = {
            player.id: self.env.get_obs(player)
            for player in self.env.players
        }
        return obs

    def get_actions() -> List[ActionType]:
        raise NotImplementedError