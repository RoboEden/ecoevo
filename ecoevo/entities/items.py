import yaml
from yaml.loader import SafeLoader
from pydantic import BaseModel
from ecoevo.config import EnvConfig

with open('ecoevo/entities/items.yaml') as file:
    ALL_ITEM_DATA = dict(yaml.load(file, Loader=SafeLoader))


class Item(BaseModel):
    name: str
    num: int
    supply: int
    refresh_rate: float
    collect_time: int
    capacity: float
    harvest: int
    expiry: int
    disposable: bool


def load_item(name: str, num=0) -> Item:
    return Item(**{
        'name': name,
        'num': num,
        **ALL_ITEM_DATA[name],
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

    def get_item(self, name: str) -> Item:
        if name in self.__dict__:
            return self.__getattribute__(name)
        else:
            raise NotImplementedError(f'No such item "{name}" exist')

    @property
    def used_volume(self):
        used = 0
        for item_name in self.__dict__:
            item = self.__getattribute__(item_name)
            if isinstance(item, Item):
                used += item.num * item.capacity
        return used

    @property
    def remain_volume(self):
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