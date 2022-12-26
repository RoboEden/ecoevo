import json
from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np
import tree

from ecoevo.config import DataPath, MapConfig, PlayerConfig
from ecoevo.entities import Item, Player, load_item
from ecoevo.types import *


@dataclass
class Tile:
    item: Optional[Item]
    player: Optional[Player]


class EntityManager:

    def __init__(self, path: str = DataPath.map_json) -> None:
        with open(path) as fp:
            self.data = dict(json.load(fp))
        self.width = self.data['width']
        self.height = self.data['height']
        assert self.width == MapConfig.width, 'Config not as same as generated'
        assert self.height == MapConfig.height, 'Config not as same as generated'
        self.map: Dict[PosType, Tile] = {}

    @property
    def item_array(self) -> dict:
        array = {}
        for x in range(self.width):
            for y in range(self.height):
                item_name = self.data['tiles'][x][y]
                if item_name == 'empty':
                    pass
                else:
                    num = self.data['amount'][x][y]
                    item = load_item(item_name, num=num)
                    array[(x, y)] = item
        return array

    def reset_map(self, players: List[Player]) -> None:
        self.map = {}
        for pos, item in self.item_array.items():
            self.map[pos] = Tile(item=item, player=None)
        for player in players:
            self.add_player(player)

    def sample(self, num: int) -> List[PosType]:
        points = []
        idxs = np.random.choice(self.width * self.height, num, replace=False)
        for idx in idxs:
            x = idx % self.width
            y = idx // self.width
            points.append((x, y))
        return points

    def add_player(self, player: Player):
        if player.pos in self.map:
            tile = self.map[player.pos]
            if tile.player is None:
                tile.player = player
            else:
                raise ValueError(f'Player already exists at {tile}.')
        else:
            self.map[player.pos] = Tile(item=None, player=player)

    def remove_player(self, player: Player):
        tile = self.map[player.pos]
        if tile.item is not None:
            tile.player = None
        else:
            del self.map[player.pos]

    def move_player(self, player: Player, secondary_action):
        self.remove_player(player)
        player.pos = player.next_pos(secondary_action)
        self.add_player(player)
        player.collect_remain = None

    def execute(
        self,
        player: Player,
        action: ActionType,
    ):
        main_action, sell_offer, buy_offer = action
        primary_action, secondary_action = main_action
        if sell_offer is not None and buy_offer is not None:
            player.trade(sell_offer, buy_offer)
        if primary_action == Action.idle:
            pass
        elif primary_action == Action.move:
            self.move_player(player, secondary_action)
        elif primary_action == Action.collect:
            player.collect(self.map[player.pos].item)
        elif primary_action == Action.consume:
            player.consume(secondary_action)
        else:
            raise ValueError(
                f'Failed to parse primary action. Player {player.id}: {primary_action} '
            )

        # reset the remaining collection steps
        if primary_action != Action.collect:
            player.collect_remain = None

    def refresh_item(self):

        def _tile_check(tile: Tile) -> None:
            if tile is None or tile.item is None:
                return
            item = tile.item
            assert item.num >= 0
            if item.num == 0:
                if item.refresh_remain is None:
                    item.refresh_remain = item.refresh_time
                elif item.refresh_remain > 0:
                    item.refresh_remain -= 1
                else:
                    item.num = item.reserve_num
                    item.refresh_remain = None
            else:
                item.refresh_remain = None

        tree.map_structure(_tile_check, self.map)