from typing import Optional

import yaml
from loguru import logger
from pydantic import BaseModel, Field
from yaml.loader import SafeLoader

from ecoevo.config import DataPath, MapConfig, PlayerConfig
from ecoevo.entities.items import Bag, Item
from ecoevo.types import IdType, Move, OfferType, PosType, TradeResult, xAction

with open(DataPath.player_yaml) as file:
    ALL_PERSONAE = yaml.load(file, Loader=SafeLoader)


class Player(BaseModel):
    persona: str
    id: IdType
    pos: PosType
    backpack: Bag = Field(default_factory=Bag)
    stomach: Bag = Field(default_factory=Bag)
    health: int = Field(default=PlayerConfig.max_health)
    collect_remain: Optional[str]
    last_action: xAction = Field(default_factory=xAction)
    trade_result: str = Field(default=TradeResult.absent)

    @property
    def preference(self) -> dict:
        return dict(ALL_PERSONAE[self.persona]["preference"])

    @property
    def ability(self) -> dict:
        return dict(ALL_PERSONAE[self.persona]["ability"])

    def collect(self, item: Item):
        if self.backpack.remain_volume >= item.harvest_num * item.capacity:
            # Init
            if self.collect_remain is None:
                collect_time = self.ability[item.name]
                self.collect_remain = collect_time - 1
            # Process collect
            elif self.collect_remain > 0:
                self.collect_remain -= 1

            # Succeed collect
            if self.collect_remain == 0:
                item.num -= item.harvest_num
                self.backpack[item.name].num += item.harvest_num
                self.collect_remain = None

        else:
            logger.critical(
                f"""Player {self.id} cannot collect {item.name} (harvest_num: {item.harvest_num})
            due to insuffient backpack remain {self.backpack.remain_volume}."""
            )

    def consume(self, item_name: str):
        item_in_bag = self.backpack[item_name]
        item_in_stomach = self.stomach[item_name]
        if item_in_bag.disposable:
            santity = item_in_bag.num >= item_in_bag.consume_num
        else:
            santity = item_in_bag.num > 0

        if santity:
            if item_in_bag.disposable:
                item_in_bag.num -= item_in_bag.consume_num
                item_in_stomach.num += item_in_bag.consume_num
            else:
                item_in_stomach.num += item_in_bag.num
            self.health = min(
                self.health + item_in_stomach.supply * item_in_stomach.num,
                PlayerConfig.max_health,
            )
        else:
            logger.critical(
                f"""Player {self.id} cannot consume {item_name} (num: {item_in_bag.num} disposable: {item_in_bag.disposable})
                due to insuffient amount."""
            )

    def wipeout(self, item_name: str):
        self.backpack[item_name].num = 0

    def next_pos(
        self,
        direction: str,
    ) -> PosType:
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
                f"Failed to parse direction. Player {self.id}: {direction}"
            )
        return (x, y)

    def trade(self, sell_offer: OfferType, buy_offer: OfferType):
        sell_item_name, sell_num = sell_offer
        buy_item_name, buy_num = buy_offer
        sell_num, buy_num = abs(sell_num), abs(buy_num)
        self.backpack[sell_item_name].num -= sell_num
        self.backpack[buy_item_name].num += buy_num
        if self.backpack.remain_volume < 0:
            for lost_num in range(self.backpack[buy_item_name].num):
                if self.backpack.remain_volume >= 0:
                    break
                self.backpack[buy_item_name].num -= 1
            logger.critical(
                f"""Player lost num {lost_num} with trade {sell_offer}, {buy_offer}
             due to insuffient backpack remain"""
            )
