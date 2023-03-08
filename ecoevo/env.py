import os
import signal
from typing import List
from ecoevo.config import EnvConfig, MapConfig, PlayerConfig
from ecoevo.gamecore import GameCore
from ecoevo.types import ActionType


class EcoEvo:

    def __init__(self,
                 render_mode: bool = False,
                 config=EnvConfig,
                 logging_level="WARNING",
                 logging_path="out.log") -> None:
        self._env = GameCore(config=config, logging_level=logging_level, logging_path=logging_path)
        self.render_mode = render_mode

        if self.render_mode:
            from ecoevo.webapp.app import WebApp
            init_message = {
                'totalStep': config.total_step,
                'mapSize': MapConfig.width,
                'bagVolume': PlayerConfig.bag_volume,
                }
            self.webapp = WebApp(self._env, init_message)
            self.webapp.run()

    @property
    def players(self):
        return self._env.players

    def reset(self):
        if self.render_mode:
            obs, info = self.webapp.output_queue.get()
        else:
            obs, info = self._env.reset()
        return obs, info

    def step(self, actions: List[ActionType]):
        if self.render_mode:
            try:
                self.webapp.action_queue.put(actions)
                obs, rewards, done, info = self.webapp.output_queue.get()
            except KeyboardInterrupt:
                os.kill(os.getpid(), signal.SIGKILL)
        else:
            obs, rewards, done, info = self._env.step(actions)
        return obs, rewards, done, info