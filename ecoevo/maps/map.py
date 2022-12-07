import json
import numpy as np

from typing import List, Dict
from dataclasses import dataclass
from ecoevo.entities.items import load_item, Item
from ecoevo.entities.player import Player
from ecoevo.entities.types import *


@dataclass
class Tile:
    item: Item or None
    player: Player or None


class MapManager:

    def __init__(self) -> None:
        path = 'ecoevo/maps/data/base.json'
        with open(path) as fp:
            self.data = dict(json.load(fp))
        self.width = self.data['width']
        self.height = self.data['height']
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
            y = idx % self.height
            points.append((x, y))
        return points

    def allocate(self, players: List[Player]):
        for player in players:
            # Allocate player
            if player.pos not in self.map:
                self.map[player.pos] = Tile(item=None, player=player)
                player.item_under_feet = None
            else:
                self.map[player.pos].player = player
                player.item_under_feet = self.map[player.pos].item

    def refresh(self):
        raise NotImplementedError