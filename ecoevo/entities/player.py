import yaml
from rich import print
from yaml.loader import SafeLoader
from ecoevo.config import MapSize, PlayerConfig
from ecoevo.entities.items import ScoreForEachItem, Bag, Item
from ecoevo.entities.types import *

with open('ecoevo/entities/player.yaml') as file:
    ALL_PERSONAE = yaml.load(file, Loader=SafeLoader)


class Player:

    def __init__(self, persona: str, id: int, pos: PosType):
        self.persona = persona
        self.id = id
        self.pos = pos
        self.preference = ScoreForEachItem(
            **ALL_PERSONAE[persona]['preference'])
        self.ability = ScoreForEachItem(**ALL_PERSONAE[persona]['ability'])
        self.backpack = Bag()
        self.stomach = Bag()
        self.health = PlayerConfig.max_health
        self.item_under_feet: Item = None
        self.collect_remain: int = None

    def get_info(self) -> dict:
        return {
            'persona': self.persona,
            'preference': self.preference.dict(),
            'ability': self.ability.dict(),
            'backpack': self.backpack.dict(),
            'stomach': self.stomach.dict(),
            'pos': self.pos,
            'id': self.id,
            'health': self.health,
            'collect_remain': self.collect_remain,
        }

    def collect(self):
        item = self.item_under_feet
        if item is not None and item.num > 0:
            progress_per_step = getattr(self.ability, item.name)
            if self.collect_remain == None:
                self.collect_remain = item.collect_time - 1
                self.collect_remain -= progress_per_step
            elif self.collect_remain > 0:
                self.collect_remain -= min(progress_per_step,
                                           self.collect_remain)
            elif self.collect_remain == 0:
                self.collect_remain = None
                self.backpack.get_item(item.name).num += item.harvest
                item.num -= item.harvest
            else:
                raise ValueError(
                    f'Player {self.id} collect_remain: {self.collect_remain}.')
        else:
            print(f'Player {self.id} cannot collect {item} at {self.pos}')

    def consume(self, item_name: str):
        item_in_bag = self.backpack.get_item(item_name)
        item_in_stomach = self.stomach.get_item(item_name)
        if item_in_bag.num > 0:
            if item_in_bag.disposable:
                item_in_bag.num -= 1
                item_in_stomach.num += 1
            else:
                item_in_stomach.num = item_in_bag.num
            self.health = min(self.health + item_in_stomach.supply,
                              PlayerConfig.max_health)
        else:
            print(
                f'Player {self.id} cannot consume "{item_name}" since no such item left.'
            )

    def move(
        self,
        direction: str,
    ):
        x, y = self.pos
        if direction == Move.up:
            y = min(y + 1, MapSize.height)
        elif direction == Move.down:
            y = max(y - 1, 0)
        elif direction == Move.right:
            x = min(x + 1, MapSize.width)
        elif direction == Move.left:
            x = max(x - 1, 0)
        else:
            print(
                f'Player {self.id}: Invalid move direction "{direction}" catched.'
            )

        self.pos = (x, y)
        self.collect_remain = None

    def trade(self, sell_offer: OfferType, buy_offer: OfferType):
        if sell_offer == None:
            return

        sell_item_name, sell_num = sell_offer
        sell_num = abs(sell_num)
        buy_item_name, buy_num = buy_offer
        sell_item_in_bag = self.backpack.get_item(sell_item_name)
        if sell_item_in_bag.num >= sell_num and sell_num > 0 and buy_num > 0:
            sell_item_in_bag.num -= sell_num
            self.backpack.get_item(buy_item_name).num += min(
                buy_num, self.backpack.remain_volume)
        else:
            print(
                f'''Player {self.id}: Invalid sell offer "{sell_offer}". Only {sell_item_in_bag.num} "{sell_item_name}"  left in bag.'''
            )

    def execute(
        self,
        action: ActionType,
    ):
        main_action, sell_offer, buy_offer = action
        primary_action, secondary_action = main_action

        self.health = max(0, self.health - PlayerConfig.comsumption_per_step)
        self.trade(sell_offer, buy_offer)
        if primary_action == Action.move:
            self.move(secondary_action)
        elif primary_action == Action.collect:
            self.collect()
        elif primary_action == Action.consume:
            self.consume(secondary_action)
        else:
            print(
                f'Invalid Action: Player {self.id}: {main_action} buy: {buy_offer} sell: {sell_offer}'
            )