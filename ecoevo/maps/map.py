import json
import numpy as np

from typing import List, Dict, Optional
from dataclasses import dataclass
from ecoevo.config import MapSize, PlayerConfig
from ecoevo.entities.items import load_item, Item
from ecoevo.entities.player import Player
from ecoevo.entities.types import *


@dataclass
class Tile:
    item: Optional[Item]
    player: Optional[Player]


class MapManager:

    def __init__(self, path: str = 'ecoevo/maps/data/base.json') -> None:
        with open(path) as fp:
            self.data = dict(json.load(fp))
        self.width = self.data['width']
        self.height = self.data['height']
        assert self.width == MapSize.width, 'Config not as same as generated'
        assert self.height == MapSize.height, 'Config not as same as generated'
        self.map: Dict[PosType, Tile] = {}

    def reset_map(self) -> Dict[PosType, Tile]:
        item_array = {}
        for x in range(self.width):
            for y in range(self.height):
                item_name = self.data['tiles'][x][y]
                if item_name == 'empty':
                    pass
                else:
                    num = self.data['amount'][x][y]
                    item = load_item(item_name, num=num)
                    item_array[(x, y)] = item

        for pos, item in item_array.items():
            self.map[pos] = Tile(item=item, player=None)

        return self.map

    def sample(self, num: int) -> List[PosType]:
        points = []
        idxs = np.random.choice(self.width * self.height, num, replace=False)
        for idx in idxs:
            x = idx % self.width
            y = idx // self.width
            points.append((x, y))
        return points

    def load_players(self, players: List[Player]):
        # Clear player
        del_keys = []
        for pos in self.map:
            if self.map[pos].item is not None:
                self.map[pos].player = None
            else:
                self.map.__delitem__(pos)

        # Allocate player
        for player in players:
            if player.pos in self.map:
                self.map[player.pos].player = player
                player.item_under_feet = self.map[player.pos].item
            else:
                self.map[player.pos] = Tile(item=None, player=player)
                player.item_under_feet = None

    def execute(
        self,
        player: Player,
        action: ActionType,
    ):
        main_action, sell_offer, buy_offer = action
        primary_action, secondary_action = main_action
        self.health = max(0, self.health - PlayerConfig.comsumption_per_step)
        player.trade(sell_offer, buy_offer)
        if primary_action == Action.move:
            self.map[player.pos] = None
            player.pos = player.next_pos(secondary_action)
            self.map[player.pos] = player
            player.collect_remain = None
        elif primary_action == Action.collect:
            player.collect()
        elif primary_action == Action.consume:
            player.consume(secondary_action)
        else:
            raise ValueError(
                f'Failed to parse primary action. Player {player.id}: {primary_action} '
            )

        player.last_action = primary_action

    def refresh(self):
        raise NotImplementedError