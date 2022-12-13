import yaml
from yaml.loader import SafeLoader
from ecoevo.config import MapSize, PlayerConfig
from ecoevo.entities.items import ScoreForEachItem, Bag, Item
from ecoevo.entities.types import *

with open('ecoevo/entities/player.yaml') as file:
    ALL_PERSONAE = yaml.load(file, Loader=SafeLoader)


class Player:

    def __init__(self, persona: str, id: IdType, pos: PosType):
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
        self.last_action: str = None
        self.trade_result: str = 'Void'

    @property
    def info(self) -> dict:
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
            'last_action': self.last_action,
            'trade_result': self.trade_result,
        }

    def collect(self):
        # Collect requires consecutive execution to succeed
        if self.last_action != Action.collect:
            self.collect_remain = None

        # Init
        if self.collect_remain is None:
            collect_time = getattr(self.ability, item.name)
            self.collect_remain = collect_time - 1

        # Process collect
        elif self.collect_remain > 0:
            self.collect_remain -= 1

        # Succeed collect
        elif self.collect_remain == 0:
            item = self.item_under_feet
            item.num -= item.harvest_num
            self.backpack[item.name].num += item.harvest_num
            self.collect_remain = None

        else:
            raise ValueError(f'Player {self.id}: Negative collect remain.')

    def consume(self, item_name: str):
        item_in_bag = self.backpack[item_name]
        item_in_stomach = self.stomach[item_name]
        if item_in_bag.disposable:
            item_in_bag.num -= item_in_bag.consume_num
            item_in_stomach.num += item_in_bag.consume_num
        else:
            item_in_stomach.num = item_in_bag.num
        self.health = min(self.health + item_in_stomach.supply,
                          PlayerConfig.max_health)

    def next_pos(
        self,
        direction: str,
    ):
        x, y = self.pos
        if direction == Move.up:
            y = min(y + 1, MapSize.height - 1)
        elif direction == Move.down:
            y = max(y - 1, 0)
        elif direction == Move.right:
            x = min(x + 1, MapSize.width - 1)
        elif direction == Move.left:
            x = max(x - 1, 0)
        else:
            raise ValueError(
                f'Failed to parse direction. Player {self.id}: {direction}')
        return (x, y)

    def trade(self, sell_offer: OfferType, buy_offer: OfferType):
        sell_item_name, sell_num = sell_offer
        buy_item_name, buy_num = buy_offer
        sell_num, buy_num = abs(sell_num), abs(buy_num)
        self.backpack[sell_item_name].num -= sell_num
        self.backpack[buy_item_name].num += buy_num