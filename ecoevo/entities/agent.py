import yaml
from enum import Enum
from items import Item
from dataclasses import dataclass
from yaml.loader import SafeLoader

PATH = ''


class Action(Enum):
    MOVE = 0
    COLLECT = 1
    CONSUME = 2
    TRADE = 3


@dataclass
class Bag:
    gold = 0
    pepper = 0
    coral = 0
    sand = 0
    pineapple = 0
    peanut = 0
    stone = 0
    pumpkin = 0


class Agent:

    def __init__(self, type: str):
        with open('ecoevo/entities/agent.yaml') as file:
            agent_types = yaml.load(file, Loader=SafeLoader)
        self.preference = dict(agent_types[type]['preference'])
        self.ability = dict(agent_types[type]['ability'])
        self.backpack = Bag()
        self.stomach = Bag()
        self.pos_x = 0
        self.pos_y = 0

    def collect(self, item: Item):
        self.backpack[item.name] += item.collect_amount

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