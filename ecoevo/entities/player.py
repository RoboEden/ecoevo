import yaml
from yaml.loader import SafeLoader
from pydantic import BaseModel

from enum import Enum
from ecoevo.entities.items import Item, load_item
from ecoevo.config import MapSize, EnvConfig, PlayerConfig
from rich import print as rprint

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
    gold: Item = load_item('gold', num=0)
    pepper: Item = load_item('pepper', num=0)
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
            raise NotImplementedError

    @property
    def remain_volume(self):
        usage = 0
        for item_name in self.__dict__:
            item = self.__getattribute__(item_name)
            if isinstance(item, Item):
                usage += item.num * item.capacity
        return EnvConfig.bag_volume - usage


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

    def __init__(self, name: str, id: int):
        self.name = name
        self.preference = ItemRatio(**ALL_PLAYER_TYPES[name]['preference'])
        self.ability = ItemRatio(**ALL_PLAYER_TYPES[name]['ability'])
        self.backpack = Bag()
        self.stomach = Bag()
        self.pos = (None, None)
        self.local_obs = None
        self.id = 0
        # self.consume_cnts = {
        #     item_type: 0
        #     for item_type in ALL_ITEM_TYPES.keys()
        # }
        self.health = PlayerConfig.max_health

    def collect(self, item: Item):
        if isinstance(item, Item):
            if self.cast_remain == None:
                self.cast_remain = item.collect_time
            elif self.cast_remain == 0:
                self.backpack[item.name] += item.harvest
            elif self.cast_remain > 0:
                self.cast_remain -= 1
            else:
                raise NameError('hehehe???')
        else:
            rprint(f'Player {self.id} cannot collect {item} at pos {self.pos}')

    def consume(self, item: Item):
        if self.backpack.get_item(item.name).num > 0:
            if self.backpack.get_item(item.name).disposable:
                self.backpack.get_item(item.name).num -= 1
                self.stomach.get_item(item.name).num += 1
            else:
                self.stomach.get_item(item.name).num = self.backpack.get_item(
                    item.name).num
            self.health = min(self.health + item.supply,
                              PlayerConfig.max_health)
        else:
            rprint(
                f'Player {self.id} cannot consume {item} since no such item left.'
            )

    def move(self, direction: int):
        x, y = self.pos
        if direction == 'up':
            y = min(y + 1, MapSize.height)
        elif direction == 'down':
            y = max(y - 1, 0)
        elif direction == 'right':
            x = min(x + 1, MapSize.width)
        elif direction == 'left':
            x = max(x - 1, 0)
        else:
            rprint(
                f'Player {self.id}: Invalid move direction {direction} catched.'
            )
        self.cast_remain = None

    def validate_offer(self, sell_offer):
        item, num = sell_offer
        if num <= self.backpack.get_item(item).num:
            return True
        else:
            return False

    def accepct(self, sell_offer, buy_offer):
        if self.validate_offer(sell_offer):
            sell_item, sell_num = sell_offer
            buy_item, buy_num = buy_offer
            self.backpack.get_item(sell_item).num -= sell_num
            self.backpack.get_item(buy_item).num += min(
                buy_num, self.backpack.remain_volume)
        return True

    def execute(self, action, sell_offer, buy_offer):
        self.health = max(0, self.health - PlayerConfig.comsumption_per_step)
        if self.is_valid(action, sell_offer, buy_offer):
            primary_action, secondary_action = action
            if primary_action == 'move':
                self.move(secondary_action)
            elif primary_action == 'collect':
                self.collect()
            elif primary_action == 'consume':
                self.consume(secondary_action)
        else:
            print(
                f'Invalid Action: Player {self.id}: {action} buy: {buy_offer} sell: {sell_offer}'
            )