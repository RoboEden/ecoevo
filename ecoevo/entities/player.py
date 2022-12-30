import yaml
from typing import Optional

from pydantic import BaseModel, Field
from yaml.loader import SafeLoader
from typing import Optional

from ecoevo.config import MapConfig, PlayerConfig, DataPath
from ecoevo.entities.items import Bag, Item
from ecoevo.types import IdType, PosType, OfferType, Move, TradeResult

with open(DataPath.player_yaml) as file:
    ALL_PERSONAE = yaml.load(file, Loader=SafeLoader)


class Player(BaseModel):
    persona:str
    id: IdType
    pos: PosType
    backpack:Bag=Field(default_factory=Bag)
    stomach:Bag=Field(default_factory=Bag)
    health:int = Field(default=PlayerConfig.max_health)
    collect_remain:Optional[str]
    trade_result:str = Field(default=TradeResult.absent)

    @property
    def preference(self)->dict:
        return dict(ALL_PERSONAE[self.persona]['preference'])
    @property
    def ability(self)->dict:
        return dict(ALL_PERSONAE[self.persona]['ability'])

    def collect(self, item:Item):
        # Init
        if self.collect_remain is None:
            collect_time = self.ability[item.name]
            self.collect_remain = collect_time - 1

        # Process collect
        elif self.collect_remain > 0:
            self.collect_remain -= 1

        # Succeed collect
        elif self.collect_remain == 0:
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
            item_in_stomach.num += item_in_bag.num
        self.health = min(self.health + item_in_stomach.supply * item_in_stomach.num,
                          PlayerConfig.max_health)

    def next_pos(
        self,
        direction: str,
    ):
        x, y = self.pos
        if direction == Move.up:
            y = min(y + 1, MapConfig.height - 1)
        elif direction == Move.down:
            y = max(y - 1, 0)
        elif direction == Move.right:
            x = min(x + 1, MapConfig.width - 1)
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
        self.trade_result = TradeResult.success