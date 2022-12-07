import yaml
from yaml.loader import SafeLoader
from pydantic import BaseModel
from typing import Dict
from ecoevo.config import EnvConfig

with open('ecoevo/entities/items.yaml') as file:
    ALL_ITEM_DATA = dict(yaml.load(file, Loader=SafeLoader))


class Item(BaseModel):
    name: str
    num: int

    @property
    def supply(self) -> int:
        return int(ALL_ITEM_DATA[self.name]['supply'])

    @property
    def refresh_rate(self) -> float:
        return float(ALL_ITEM_DATA[self.name]['refresh_rate'])

    @property
    def collect_time(self) -> int:
        return int(ALL_ITEM_DATA[self.name]['collect_time'])

    @property
    def capacity(self) -> float:
        return int(ALL_ITEM_DATA[self.name]['capacity'])

    @property
    def harvest(self) -> int:
        return int(ALL_ITEM_DATA[self.name]['harvest'])

    @property
    def expiry(self) -> int:
        return int(ALL_ITEM_DATA[self.name]['expiry'])

    @property
    def disposable(self) -> bool:
        return bool(ALL_ITEM_DATA[self.name]['disposable'])


def load_item(name: str, num=0) -> Item:
    return Item(**{
        'name': name,
        'num': num,
    })


class Bag(BaseModel):
    gold: Item = load_item('gold', num=0)
    hazelnut: Item = load_item('hazelnut', num=0)
    coral: Item = load_item('coral', num=0)
    sand: Item = load_item('sand', num=0)
    pineapple: Item = load_item('pineapple', num=0)
    peanut: Item = load_item('peanut', num=0)
    stone: Item = load_item('stone', num=0)
    pumpkin: Item = load_item('pumpkin', num=0)

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
        return EnvConfig.bag_volume - self.used_volume


class ScoreForEachItem(BaseModel):
    gold: float
    hazelnut: float
    coral: float
    sand: float
    pineapple: float
    peanut: float
    stone: float
    pumpkin: float