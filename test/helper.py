import io
from typing import Tuple

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


ALL_ITEMS = ecoevo.entities.items.Bag()


class Helper:

    def __init__(self):
        self.env = EcoEvo()
        self.cfg = EnvConfig
        self.error_log = io.StringIO()
        logger.add(self.error_log, level='ERROR')

    def reset(self):
        self.obs, self.info = self.env.reset()

        return self

    def init_points(self, *lst: Tuple[PosType, IdType]):
        """ (pos, id)... """
        pos_dict = {}
        visited = set()
        for pos, id in lst:
            pos_dict[id] = pos
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

        return self

    def set_bag(self, *lst: Tuple[IdType, str, int]):
        """ (id, item, amount)... """
        for id in range(self.env.num_player):
            for item in self.env.players[id].backpack.dict().values():
                item.num = 0
        for id, item, amount in lst:
            self.env.players[id].backpack.dict()[item].num = amount

        return self

    def init_tiles(self, *lst: Tuple[PosType, Item, int]):
        """ (pos, item, amount)... """
        map_item = [['empty'] * MapConfig.height for _ in range(MapConfig.width)]
        map_amount = [[0] * MapConfig.height for _ in range(MapConfig.width)]
        for pos, item, amount in lst:
            map_item[pos[0]][pos[1]] = item
            map_amount[pos[0]][pos[1]] = amount
        self.env.entity_manager.data = dict(
            tiles=map_item,
            amount=map_amount,
        )

        return self

    def step(self, *lst: Tuple[IdType, ActionType]):
        """ (id, action)... """
        actions = [(('idle', None), None, None) for _ in range(self.env.num_player)]
        for id, action in lst:
            actions[id] = action

        self.obs, self.rewards, self.done, self.info = self.env.step(actions)

        return self

    def assert_tiles(self, *lst: Tuple[PosType, str, int]):
        """ (pos, item, amount) """
        map_dict = {}
        for pos, item, amount in lst:
            map_dict[pos] = (item, amount)
        for x in range(MapConfig.width):
            for y in range(MapConfig.height):
                pos = (x, y)
                tile = self.env.entity_manager.map.get(pos)
                if tile is None or tile.item is None:
                    assert pos not in map_dict, pos
                else:
                    assert pos in map_dict, pos
                    item, amount = map_dict[pos]
                    assert tile.item.name == item, pos
                    assert tile.item.num == amount, pos

        return self

    def assert_bag(self, *lst: Tuple[IdType, str, int]):
        """ (id, item, amount)... """
        amount_dict = {}
        for id, item, amount in lst:
            amount_dict[(id, item)] = amount

        for id in range(self.env.num_player):
            for item_name, item in self.env.players[id].backpack.dict().items():
                answer = amount_dict.get((id, item_name))
                if answer is None:
                    assert item.num == 0, (id, item_name)
                else:
                    assert item.num == answer, (id, item_name)

        return self

    def assert_pos_player(self, *lst: Tuple[PosType, IdType]):
        for pos, id in lst:
            assert self.env.players[id].pos == pos

        return self

    def assert_no_error_log(self):
        assert self.error_log.getvalue() == ''

        return self
