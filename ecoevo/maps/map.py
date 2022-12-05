import json
from typing import Dict, Tuple
from ecoevo.entities.player import Player
from ecoevo.entities.items import load_item


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
                    item = None
                else:
                    num = self.data['amount'][x][y]
                    item = load_item(item_name, num=num)
                map[(x, y)] = {
                    'item': item,
                    'player': None,
                }
        return map
