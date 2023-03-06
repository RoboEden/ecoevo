import io
from typing import Dict, Optional, Tuple, List

from loguru import logger

import ecoevo.entities.items
from ecoevo.gamecore import GameCore
from ecoevo.config import EnvConfig, MapConfig
from ecoevo.types import Action, ActionType, IdType, Move, PosType, OfferType
from ecoevo.entities import Player


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
        self.gamecore = GameCore(logging_level="DEBUG")
        self.cfg = EnvConfig
        self.info_log = io.StringIO()
        self.warning_log = io.StringIO()
        self.error_log = io.StringIO()
        logger.add(self.info_log, level='INFO')
        logger.add(self.warning_log, level='WARNING')
        logger.add(self.error_log, level='ERROR')

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
        self.cfg.random_generate_map = False

        map_item = [['empty'] * MapConfig.height for _ in range(MapConfig.width)]
        map_amount = [[0] * MapConfig.height for _ in range(MapConfig.width)]
        for pos, offer in tile_dict.items():
            item, amount = offer
            map_item[pos[0]][pos[1]] = item
            map_amount[pos[0]][pos[1]] = amount
        self.gamecore.entity_manager.data = dict(
            tiles=map_item,
            amount=map_amount,
        )
        self.tile_dict = tile_dict

    def reset(self):
        self.obs, self.info = self.gamecore.reset()
        if hasattr(self, 'tile_dict'):
            for pos, offer in self.tile_dict.items():
                item, amount = offer
                self.gamecore.entity_manager.map[pos].item.num = amount


    def step(self, action_dict: Dict[IdType, ActionType]):
        """ {id: action ...} """
        actions = [(('idle', None), None, None, None) for _ in range(self.gamecore.num_player)]
        for id, action in action_dict.items():
            actions[id] = action

        self.obs, self.rewards, self.done, self.info = self.gamecore.step(actions)

    def set_bag(self, id: IdType, bag: Dict[str, int]):
        """ {(item, num)...} """
        for item in ITEMS.dict():
            self.gamecore.players[id].backpack[item].num = 0
        for item, num in bag.items():
            self.gamecore.players[id].backpack[item].num = num
    
    def get_player(self, id: IdType) -> Player:
        return self.gamecore.players[id]
    
    def get_player_offers(self, id: IdType) -> List[OfferType]:
        return [o for o in self.get_player(id).offers if o]

    def get_tile_item(self, pos: PosType) -> Tuple[str, int]:
        """ pos """
        tile = self.gamecore.entity_manager.map.get(pos)
        item = tile.item if tile else None
        return (item.name, item.num) if item else ('empty', 0)
    
    def get_tile_player(self, pos: PosType) -> Optional[Player]:
        """ pos """
        tile = self.gamecore.entity_manager.map.get(pos)
        player = tile.player if tile else None
        return player

    def get_map_items(self) -> Dict[PosType, Optional[Tuple[str, int]]]:
        map_items = {}
        for pos in self.gamecore.entity_manager.map:
            map_items[pos] = self.get_tile_item(pos)
        return map_items

    def get_bag(self, id: IdType) -> Dict[str, int]:
        """ id """
        bag = {}
        for item in self.gamecore.players[id].backpack.dict().values():
            if item.num > 0:
                bag[item.name] = item.num
        return bag

    def get_stomach(self, id: IdType) -> Dict[str, int]:
        """ id """
        stomach = {}
        for item in self.gamecore.players[id].stomach.dict().values():
            if item.num > 0:
                stomach[item.name] = item.num
        return stomach

    def get_info_log(self) -> str:
        return self.info_log.getvalue()

    def get_warning_log(self) -> str:
        return self.warning_log.getvalue()

    def get_error_log(self) -> str:
        return self.error_log.getvalue()
