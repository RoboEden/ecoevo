import yaml
from yaml.loader import SafeLoader
from pydantic import BaseModel

from enum import Enum
from ecoevo.entities.items import Item, load_item

PATH = ''
with open('ecoevo/entities/player.yaml') as file:
    player_types = yaml.load(file, Loader=SafeLoader)


class Player:
    name: str
    supply: int
    grow_rate: float
    collect_time: int
    capacity: float
    harvest: int
    expiry: int
    disposable: bool

    def __init__(self, amount) -> None:
        self.amount = amount

    def __str__(self) -> str:
        return type(self).__name__


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


class Player:

    def __init__(self, name: str):
        self.name = name
        self.preference = dict(player_types[name]['preference'])
        self.ability = dict(player_types[name]['ability'])
        self.backpack = Bag()
        self.stomach = Bag()
        self.pos_x = 0
        self.pos_y = 0
        self.local_obs = None
        self.id = 0

    def update_local_obs(self, obs):
        self.local_obs = obs.getobs(self.id)

    def collect(self, item: Item):
        self.backpack[item.name] += item.harvest

    def consume(self, item: Item):
        self.backpack[item.name] -= 1
        self.stomach[item.name] -= 1

    @property
    def pos(self):
        return self.pos_x, self.pos_y

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