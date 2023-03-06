from typing import Dict, Optional

from pydantic import BaseModel

from ecoevo.config import PlayerConfig
from ecoevo.data.items import ALL_ITEM_DATA


class Item(BaseModel):
    name: str
    num: int = 0
    locked_num: int = 0
    refresh_remain: int = 0

    @property
    def disposable(self) -> bool:
        return bool(ALL_ITEM_DATA[self.name]['disposable'])

    @property
    def divisible(self) -> bool:
        return bool(ALL_ITEM_DATA[self.name]['divisible'])

    @property
    def luxury(self) -> bool:
        return bool(ALL_ITEM_DATA[self.name]['luxury'])

    @property
    def supply(self) -> int:
        return int(ALL_ITEM_DATA[self.name]['supply'])

    @property
    def refresh_time(self) -> int:
        return int(ALL_ITEM_DATA[self.name]['refresh_time'])

    @property
    def capacity(self) -> int:
        return int(ALL_ITEM_DATA[self.name]['capacity'])

    @property
    def reserve_num(self) -> int:
        return int(ALL_ITEM_DATA[self.name]['reserve_num'])

    @property
    def harvest_num(self) -> int:
        return int(ALL_ITEM_DATA[self.name]['harvest_num'])

    @property
    def consume_num(self) -> int:
        return int(ALL_ITEM_DATA[self.name]['consume_num'])

    @property
    def expiry(self) -> int:
        return int(ALL_ITEM_DATA[self.name]['expiry'])
    
    @property
    def free_num(self) -> int:
        return self.num - self.locked_num


def load_item(name: str) -> Item:
    return Item(name=name)


class Bag(BaseModel):
    gold: Item = load_item('gold')
    hazelnut: Item = load_item('hazelnut')
    coral: Item = load_item('coral')
    sand: Item = load_item('sand')
    pineapple: Item = load_item('pineapple')
    peanut: Item = load_item('peanut')
    stone: Item = load_item('stone')
    pumpkin: Item = load_item('pumpkin')
    locked_volume: int = 0

    def __getitem__(self, name: str) -> Item:
        if name in self.__dict__:
            item = self.__getattribute__(name)
            if isinstance(item, Item):
                return self.__getattribute__(name)
            else:
                raise TypeError(f'Get {item} by {name}')
        else:
            raise NotImplementedError(f'No such item "{name}" exist')

    def dict(self, **kwargs) -> Dict[str, Item]:
        _dict = {}
        for item_name in self.__dict__:
            item = self.__getattribute__(item_name)
            if isinstance(item, Item):
                _dict[item.name] = item
        return _dict

    @property
    def used_volume(self) -> float:
        used = 0
        for item in self.dict().values():
            used += item.num * item.capacity
        return used

    @property
    def remain_volume(self) -> float:
        return PlayerConfig.bag_volume - self.used_volume - self.locked_volume
