import json
from pydantic import BaseModel
from typing import Dict, List, Optional

import numpy as np
import tree
from loguru import logger

from ecoevo.config import DataPath, MapConfig
from ecoevo.entities import ALL_ITEM_DATA, Item, Player, load_item
from ecoevo.entities.move_solver import MoveSolver
from ecoevo.types import Action, ActionType, PosType, IdType, Move

MOVE_DIRECTIONS = {
    Move.right: (1, 0),
    Move.up: (0, 1),
    Move.left: (-1, 0),
    Move.down: (0, -1),
}


class Tile(BaseModel):
    item: Optional[Item]
    player: Optional[Player]


class EntityManager:

    def __init__(self, path: str = DataPath.map_json, use_move_solver=True) -> None:
        with open(path) as fp:
            self.data = dict(json.load(fp))
        self.width = self.data["width"]
        self.height = self.data["height"]
        self.use_move_solver = use_move_solver
        assert self.width == MapConfig.width, "Config not as same as generated"
        assert self.height == MapConfig.height, "Config not as same as generated"
        self.map: Dict[PosType, Tile] = {}

    @property
    def item_array(self) -> dict:
        array = {}
        for x in range(self.width):
            for y in range(self.height):
                item_name = self.data["tiles"][x][y]
                if item_name == "empty":
                    pass
                else:
                    item = load_item(item_name)
                    item.num = item.reserve_num
                    array[(x, y)] = item
        return array

    def reset_map(self, players: List[Player], random_generate: bool) -> None:
        self.map = {}
        array = self.random_item_array() if random_generate else self.item_array

        for pos, item in array.items():
            self.map[pos] = Tile(item=item, player=None)
        for player in players:
            self.add_player(player)

    def random_item_array(self) -> Dict[PosType, Item]:
        item_names = list(ALL_ITEM_DATA.keys())
        block_num = len(item_names) * MapConfig.generate_num_block_resource
        assert block_num <= MapConfig.width * MapConfig.height
        array = {}
        for i, pos in enumerate(self.sample(block_num)):
            item = load_item(item_names[i % len(item_names)])
            item.num = item.reserve_num
            array[pos] = item
        return array

    def sample(self, num: int) -> List[PosType]:
        points = []
        idxs = np.random.choice(self.width * self.height, num, replace=False)
        for idx in idxs:
            x = idx % self.width
            y = idx // self.width
            points.append((x, y))
        return points

    def get_item(self, pos: PosType) -> Optional[Item]:
        tile = self.map.get(pos)
        return tile.item if tile else None

    def get_player(self, pos: PosType) -> Optional[Player]:
        tile = self.map.get(pos)
        return tile.player if tile else None

    def add_player(self, player: Player):
        if player.pos in self.map:
            tile = self.map[player.pos]
            if tile.player is None:
                tile.player = player
            else:
                raise ValueError(f"Player already exists at {tile}.")
        else:
            self.map[player.pos] = Tile(item=None, player=player)

    def remove_player(self, player: Player):
        tile = self.map[player.pos]
        if tile.item is not None:
            tile.player = None
        else:
            del self.map[player.pos]

    def move_reset(self):
        self.player_dest: Dict[IdType, PosType] = {}

    def move_execute(self, players: List[Player]):
        if not self.use_move_solver:
            return
        va = MoveSolver.solve(players, self.player_dest)
        for pid in va:
            self.remove_player(players[pid])
            players[pid].pos = self.player_dest[pid]
        for pid in va:
            self.add_player(players[pid])

    def move_player(self, player: Player, secondary_action):
        dx, dy = MOVE_DIRECTIONS[secondary_action]
        x, y = (player.pos[0] + dx, player.pos[1] + dy)
        if x < 0 or x >= MapConfig.width or y < 0 or y >= MapConfig.height:
            logger.warning(f"Player {player.id} move towards map boarder")
            return False
        next_pos = (x, y)

        if self.use_move_solver:
            self.player_dest[player.id] = next_pos
            return True
        # If destination has agent, skip move action
        if next_pos in self.map:
            tile = self.map[next_pos]
            if tile.player:
                return False

        self.remove_player(player)
        player.pos = next_pos
        self.add_player(player)

    def execute_main_action(self, player: Player, action: ActionType, curr_step: int):
        (primary_action, secondary_action), *_ = action

        if primary_action != Action.collect:
            player.collect_remain = 0

        if primary_action == Action.idle:
            return True

        if primary_action == Action.move:
            if secondary_action is None:
                logger.error(f"Player {player.id} {primary_action} secondary action is None")
                return False
            return self.move_player(player, secondary_action)

        if primary_action == Action.collect:
            item = self.get_item(player.pos)
            if not item:
                logger.warning(f"Player {player.id} collect at {player.pos} but no item exists")
                return False
            return player.collect(item)

        if primary_action == Action.consume:
            if secondary_action is None:
                logger.error(f"Player {player.id} {primary_action} secondary action is None")
                return False
            return player.consume(secondary_action, curr_step)

        if primary_action == Action.wipeout:
            if secondary_action is None:
                logger.error(f"Player {player.id} {primary_action} secondary action is None")
                return False
            return player.wipeout(secondary_action)

        logger.error(f"Player {player.id} primary action is invalid: '{primary_action}'")
        return False

    def refresh_item(self):
        for pos in self.map:
            item = self.get_item(pos)
            if not item or item.num > 0:
                continue
            item.refresh_remain = (item.refresh_remain or item.refresh_time) - 1
            if not item.refresh_remain:
                item.num = item.reserve_num
