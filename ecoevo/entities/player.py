import yaml
from rich import print as rprint
from yaml.loader import SafeLoader

from ecoevo.config import MapSize, PlayerConfig
from ecoevo.entities.items import Item, ItemRatio, Bag
from ecoevo.entities.act_type import Action, Direction, Trade

with open('ecoevo/entities/player.yaml') as file:
    ALL_PLAYER_TYPES = yaml.load(file, Loader=SafeLoader)


class Player:

    def __init__(self, name: str, id: int):
        self.name = name
        self.preference = ItemRatio(**ALL_PLAYER_TYPES[name]['preference'])
        self.ability = ItemRatio(**ALL_PLAYER_TYPES[name]['ability'])
        self.backpack = Bag()
        self.stomach = Bag()
        self.pos = (None, None)
        self.id = id
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
        if direction == Direction.up:
            y = min(y + 1, MapSize.height)
        elif direction == Direction.down:
            y = max(y - 1, 0)
        elif direction == Direction.right:
            x = min(x + 1, MapSize.width)
        elif direction == Direction.left:
            x = max(x - 1, 0)
        else:
            rprint(
                f'Player {self.id}: Invalid move direction {direction} catched.'
            )
        self.cast_remain = None

    def trade(self, sell_offer, buy_offer):
        sell_item, sell_num = sell_offer
        buy_item, buy_num = buy_offer
        self.backpack.get_item(sell_item).num -= sell_num
        self.backpack.get_item(buy_item).num += min(
            buy_num, self.backpack.remain_volume)
        return True

    def execute(self, action, sell_offer, buy_offer):
        self.health = max(0, self.health - PlayerConfig.comsumption_per_step)
        primary_action, secondary_action = action
        if primary_action == Action.move:
            self.move(secondary_action)
        elif primary_action == Action.collect:
            self.collect()
        elif primary_action == Action.consume:
            self.consume(secondary_action)
        elif primary_action == Action.trade:
            self.trade(sell_offer, buy_offer)
        else:
            print(
                f'Invalid Action: Player {self.id}: {action} buy: {buy_offer} sell: {sell_offer}'
            )