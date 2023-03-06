import random
import sys
from copy import deepcopy
from typing import Dict, List, Optional, Tuple

from loguru import logger

from ecoevo.analyser import Analyser
from ecoevo.config import EnvConfig, MapConfig, PlayerConfig
from ecoevo.entities import ALL_ITEM_DATA, EntityManager, Player, Tile
from ecoevo.reward import RewardParser
from ecoevo.market.market import Market
from ecoevo.types import Action, ActionType, IdType, PosType, TradeResult


class GameCore:

    def __init__(self, config=EnvConfig, logging_level="WARNING", logging_path="out.log"):
        self.cfg = config
        self.entity_manager = EntityManager(use_move_solver=EnvConfig.use_move_solver)
        self.market = Market()
        self.reward_parser = RewardParser()
        self.players: List[Player] = []

        self.info = {}

        # Logging
        logger.remove()
        logger.add(sys.stderr, level=logging_level)
        logger.add(logging_path, level=logging_level)

    @property
    def num_player(self) -> int:
        return len(self.players)

    @property
    def all_item_names(self) -> List[str]:
        return list(ALL_ITEM_DATA.keys())

    def reset(self) -> Tuple[Dict[IdType, Dict[PosType, Tile]], Dict[IdType, dict]]:
        self.players = []
        self.curr_step = 0
        self.reward_parser.reset()
        self.analyser = Analyser()
        points = self.cfg.init_points or self.entity_manager.sample(len(self.cfg.personae))
        for id, persona in enumerate(self.cfg.personae):
            player = Player(persona=persona, id=id, pos=points[id])
            self.players.append(player)

        self.entity_manager.reset_map(self.players, random_generate=self.cfg.random_generate_map)

        obs = {player.id: self.get_obs(player) for player in self.players}
        self.info = {}

        self.shuffled_ids = [player.id for player in self.players]

        return obs, deepcopy(self.info)

    def step(
        self, actions: List[ActionType]
    ) -> Tuple[Dict[IdType, Dict[PosType, Tile]], Dict[IdType, float], bool, Dict[IdType, dict]]:
        random.shuffle(self.shuffled_ids)
        self.curr_step += 1
        
        for id in self.shuffled_ids:
            self.players[id].memorize_action(actions[id])
        
        # match and execute trade
        transaction_graph = self.market.trade(self.players, actions)

        # main action
        self.entity_manager.move_reset()
        executed_main_actions = {}
        for id in self.shuffled_ids:
            player = self.players[id]
            action = actions[id]
            if self.entity_manager.execute_main_action(player, action):
                executed_main_actions[id] = action[0]
        self.entity_manager.move_execute(self.players)

        # health decrease
        for id in self.shuffled_ids:
            player = self.players[id]
            player.health = max(0, player.health - PlayerConfig.comsumption_per_step)

        # refresh items
        self.entity_manager.refresh_item()

        # generate obs, reward, info
        obs = {player.id: self.get_obs(player) for player in self.players}
        rewards = {player.id: self.reward_parser.parse(player) for player in self.players}
        done = self.curr_step >= self.cfg.total_step
        self.info = self.analyser.get_info(
            self.curr_step,
            done,
            self.info,
            self.players,
            self.entity_manager,
            transaction_graph,
            executed_main_actions,
            {
                player.id: {
                    "reward": rewards[player.id],
                    "utility": self.reward_parser.last_utilities[player.id],
                    "item_utility": self.reward_parser.last_item_utilities[player.id],
                    "cost": self.reward_parser.total_costs[player.id],
                }
                for player in self.players
            },
        )
        self.info["transaction_graph"] = transaction_graph

        return obs, rewards, done, deepcopy(self.info)

    def get_obs(self, player: Player) -> Dict[PosType, Tile]:
        player_x, player_y = player.pos
        x_min = max(player_x - self.cfg.visual_radius, 0)
        x_max = min(player_x + self.cfg.visual_radius, MapConfig.width - 1)
        y_min = max(player_y - self.cfg.visual_radius, 0)
        y_max = min(player_y + self.cfg.visual_radius, MapConfig.height - 1)

        local_obs = {}
        for x in range(x_min, x_max + 1):
            for y in range(y_min, y_max + 1):
                tile = self.entity_manager.map.get((x, y))
                if tile:
                    local_x = x - player_x + self.cfg.visual_radius
                    local_y = y - player_y + self.cfg.visual_radius
                    local_obs[(local_x, local_y)] = tile

        return local_obs
