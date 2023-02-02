import ecoevo.types as et
from typing import List
from ecoevo.gamecore import GameCore
from ecoevo.config import EnvConfig


class EcoEvo:

    def __init__(self,
                 render_mode: bool = False,
                 config=EnvConfig,
                 logging_level="WARNING",
                 logging_path="out.log") -> None:
        self._env = GameCore(config=config, logging_level=logging_level, logging_path=logging_path)
        self.render_mode = render_mode
        if self.render_mode:
            from ecoevo.render import WebApp
            self.app = WebApp(self._env)
            self.app.run_server(debug=False)

    @property
    def players(self):
        return self._env.players

    def reset(self):
        if self.render_mode:
            obs, _, _, info = self.app.get_output()
        else:
            obs, info = self._env.reset()
        return obs, info

    def step(self, actions: List[et.ActionType]):
        if self.render_mode:
            self.app.put_action(actions)
            obs, rewards, done, info = self.app.get_output()
        else:
            obs, rewards, done, info = self._env.step(actions)
        return obs, rewards, done, info