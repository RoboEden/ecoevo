import yaml
from yaml.loader import SafeLoader
from pydantic import BaseModel

from enum import Enum
from ecoevo.entities.items import Item, load_item

with open('ecoevo/entities/player.yaml') as file:
    ALL_PLAYER_TYPES = yaml.load(file, Loader=SafeLoader)

# def load_item(name, amount) -> Item:
#     with open('ecoevo/entities/items.yaml') as file:
#         data = dict(yaml.load(file, Loader=SafeLoader))
#     subclass = type(name, (Item, ), data[name])
#     return subclass(amount)


class Action(Enum):
    MOVE = 0
    COLLECT = 1
    CONSUME = 2
    TRADE = 3


class Bag(BaseModel):
    gold = load_item('gold', num=0)
    pepper = load_item('pepper', num=0)
    coral = load_item('coral', num=0)
    sand = load_item('sand', num=0)
    pineapple = load_item('pineapple', num=0)
    peanut = load_item('peanut', num=0)
    stone = load_item('stone', num=0)
    pumpkin = load_item('pumpkin', num=0)


class ItemRatio(BaseModel):
    gold: float
    pepper: float
    coral: float
    sand: float
    pineapple: float
    peanut: float
    stone: float
    pumpkin: float


class Player:

    def __init__(self, name: str):
        self.name = name
        self.preference = ItemRatio(**ALL_PLAYER_TYPES[name]['preference'])
        self.ability = ItemRatio(**ALL_PLAYER_TYPES[name]['ability'])
        self.backpack = Bag()
        self.stomach = Bag()
        self.pos = (None, None)
        self.local_obs = None
        self.id = 0

    def update_local_obs(self, obs):
        self.local_obs = obs.getobs(self.id)

    def collect(self, item: Item):
        self.backpack[item.name] += item.harvest

    def consume(self, item: Item):
        self.backpack[item.name] -= 1
        self.stomach[item.name] -= 1

    def move(self, direction: int):
        if direction == 1:
            self.pos_y += 1
        elif direction == 2:
            self.pos_x += 1
        elif direction == 3:
            self.pos_y -= 1
        elif direction == 4:
            self.pos_x -= 1
        else:
            return False
        return True

    def buy(item):
        pass

    def sell(item):
        pass