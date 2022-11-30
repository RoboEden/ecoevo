import numpy as np
import json
from typing import Dict, Tuple
from ecoevo.entities.player import Player
from ecoevo.entities.items import Item
from ecoevo.config import MapSize


class MapGenerator:

    def __init__(self) -> None:
        path = 'ecoevo/maps/base.json'
        with open(path) as fp:
            self.data = dict(json.load(fp))

    def gen_map(self) -> Dict[Tuple[int, int], dict]:
        width = self.data['width']
        height = self.data['height']
        map = {}
        for x in range(width):
            for y in range(height):
                item_name = self.data['tiles'][x][y]
                if item_name == 'empty':
                    continue
                amount = self.data['amount'][x][y]
                map[(x, y)] = {
                    'item': Item(item_name, amount),
                    'player': None,
                }
        return map
