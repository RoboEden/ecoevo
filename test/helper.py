import io
from typing import Dict, Optional, Tuple

from loguru import logger

import ecoevo.entities.items
from ecoevo import EcoEvo
from ecoevo.config import EnvConfig, MapConfig
from ecoevo.types import Action, ActionType, IdType, Move, PosType


class Item:
    gold = 'gold'
    hazelnut = 'hazelnut'
    coral = 'coral'
    sand = 'sand'
    pineapple = 'pineapple'
    peanut = 'peanut'
    stone = 'stone'
    pumpkin = 'pumpkin'


ITEMS = ecoevo.entities.items.Bag()


class Helper:

    def __init__(self):
        self.env = EcoEvo()
        self.cfg = EnvConfig
        self.error_log = io.StringIO()
        logger.add(self.error_log, level='ERROR')

    def reset(self):
        self.obs, self.info = self.env.reset()

    def init_pos(self, pos_dict: Dict[IdType, PosType]):
        """ {id: pos ...} """
        visited = set()
        for id, pos in pos_dict.items():
            assert pos not in visited
            visited.add(pos)
        visited.add(None)

        self.cfg.init_points = []
        idx = 0
        for id in range(len(self.cfg.personae)):
            pos = pos_dict.get(id)
            if pos is None:
                while pos in visited:
                    pos = divmod(idx, MapConfig.width)
                    idx += 1
                visited.add(pos)
            self.cfg.init_points.append(pos)

    def init_tiles(self, tile_dict: Dict[PosType, Tuple[str, int]]):
        """ {pos: (item, amount)...} """
        map_item = [['empty'] * MapConfig.height for _ in range(MapConfig.width)]
        map_amount = [[0] * MapConfig.height for _ in range(MapConfig.width)]
        for pos, offer in tile_dict.items():
            item, amount = offer
            map_item[pos[0]][pos[1]] = item
            map_amount[pos[0]][pos[1]] = amount
        self.env.entity_manager.data = dict(
            tiles=map_item,
            amount=map_amount,
        )

    def step(self, action_dict: Dict[IdType, ActionType]):
        """ {id: action}... """
        actions = [(('idle', None), None, None) for _ in range(self.env.num_player)]
        for id, action in action_dict.items():
            actions[id] = action

        self.obs, self.rewards, self.done, self.info = self.env.step(actions)

    def set_bag(self, id: IdType, bag: Dict[str, int]):
        """ {(item, num)...} """
        for item in ITEMS.dict():
            self.env.players[id].backpack[item].num = 0
        for item, num in bag.items():
            self.env.players[id].backpack[item].num = num

    def get_tile_item(self, pos: PosType) -> Optional[Tuple[str, int]]:
        """ pos """
        tile = self.env.gettile(pos)
        item = tile.item if tile else None
        return (item.name, item.num) if item else None

    def get_bag(self, id: IdType) -> Dict[str, int]:
        """ id """
        bag = {}
        for item in self.env.players[id].backpack.dict().values():
            if item.num > 0:
                bag[item.name] = item.num
        return bag

    def get_stomach(self, id: IdType) -> Dict[str, int]:
        """ id """
        stomach = {}
        for item in self.env.players[id].stomach.dict().values():
            if item.num > 0:
                stomach[item.name] = item.num
        return stomach

    def get_error_log(self) -> str:
        return self.error_log.getvalue()
