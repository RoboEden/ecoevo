from typing import Optional, List

from loguru import logger
from pydantic import BaseModel, Field

from ecoevo.config import MapConfig, PlayerConfig, EnvConfig
from ecoevo.data.player import ALL_PERSONAE
from ecoevo.entities.items import Bag, Item
from ecoevo.types import IdType, Move, ActionType, OfferType, PosType, TradeResult, xAction


class Player(BaseModel):
    persona: str
    id: IdType
    pos: PosType
    backpack: Bag = Field(default_factory=Bag)
    stomach: Bag = Field(default_factory=Bag)
    collect_cnt: Bag = Field(default_factory=Bag)
    buy_cnt: Bag = Field(default_factory=Bag)
    x_stomach: Bag = Field(default_factory=Bag)
    health: int = Field(default=PlayerConfig.max_health)
    offers: List[OfferType] = Field(default_factory=lambda: [None] * PlayerConfig.max_offer)
    collect_remain: int = 0
    last_action: xAction = Field(default_factory=xAction)
    trade_result: str = Field(default=TradeResult.absent)

    @property
    def preference(self) -> dict:
        return dict(ALL_PERSONAE[self.persona]["preference"])

    @property
    def ability(self) -> dict:
        return dict(ALL_PERSONAE[self.persona]["ability"])

    def collect(self, item: Item) -> bool:
        if item.num < item.harvest_num:
            logger.warning(f"Player {self.id} collect {item} at {self.pos} but no enough resource")
            return False

        if item.harvest_num * item.capacity > self.backpack.remain_volume:
            logger.warning(f"Player {self.id} collect {item} at {self.pos} but bag full")
            return False

        self.collect_remain = (self.collect_remain or self.ability[item.name]) - 1
        if not self.collect_remain:
            item.num -= item.harvest_num
            self.backpack[item.name].num += item.harvest_num
            self.collect_cnt[item.name].num += item.harvest_num

        return True

    def consume(self, item_name: str, curr_step: int) -> bool:
        item = self.backpack[item_name]

        if item.disposable:
            consumed_num = min(item.free_num, item.consume_num)
            item.num -= consumed_num
        else:
            assert 100 % item.capacity == 0
            consumed_num = min(item.free_num, 100 // item.capacity)

        self.stomach[item_name].num += consumed_num
        self.health += consumed_num * item.supply
        self.health = min(self.health, PlayerConfig.max_health)

        x_item = self.x_stomach[item_name]
        if (curr_step - x_item.last_consume_step) >= PlayerConfig.consume_cooldown:
            self.x_stomach[item_name].num += consumed_num
            x_item.last_consume_step = curr_step

        return True

    def wipeout(self, item_name: str) -> bool:
        item = self.backpack[item_name]
        item.num -= item.free_num
        return True

    def try_accept_offer(self, opponent_offer: OfferType) -> bool:
        (sell_name, sell_num), (buy_name, buy_num) = opponent_offer
        # convert to offer relative to player
        (sell_name, sell_num), (buy_name, buy_num) = (buy_name, -buy_num), (sell_name, -sell_num)
        sell_item, buy_item = self.backpack[sell_name], self.backpack[buy_name]

        if sell_item.free_num < abs(sell_num):
            logger.warning(f'Item {sell_name} free num not enough {sell_item.free_num}/{abs(sell_num)}')
            return False

        delta_volume = sell_item.capacity * sell_num + buy_item.capacity * buy_num
        if delta_volume > 0 and delta_volume > self.backpack.remain_volume:
            logger.warning(f'Player remain volume not enough {self.backpack.remain_volume}/{delta_volume}')
            return False

        sell_item.num -= abs(sell_num)
        buy_item.num += buy_num
        self.buy_cnt[buy_item.name].num += buy_num
        return True

    def offer_accepted(self, index: int):
        (sell_name, sell_num), (buy_name, buy_num) = self.offers[index]
        sell_item, buy_item = self.backpack[sell_name], self.backpack[buy_name]

        self.offer_cancel(index)

        sell_item.num -= abs(sell_num)
        buy_item.num += buy_num
        self.buy_cnt[buy_item.name].num += buy_num

    def offer_try_add(self, offer: OfferType) -> bool:
        (sell_name, sell_num), (buy_name, buy_num) = offer
        if not (sell_name != buy_num and sell_num < 0 and buy_num > 0):
            return False
        sell_item, buy_item = self.backpack[sell_name], self.backpack[buy_name]

        if sell_item.free_num < abs(sell_num):
            return False

        delta_volume = sell_item.capacity * sell_num + buy_item.capacity * buy_num
        if delta_volume > 0 and delta_volume > self.backpack.remain_volume:
            return False

        try:
            index = self.offers.index(None)
        except ValueError:
            logger.warning(f'Player {self.id} try add offer but exceed max offer')
            return False

        sell_item.locked_num += abs(sell_num)
        if delta_volume > 0:
            self.backpack.locked_volume += delta_volume

        self.offers[index] = offer
        return True

    def offer_cancel(self, index: int):
        offer = self.offers[index]
        if not offer:
            logger.info(f'Player {self.id} try cancel empty offer')
            return
        (sell_name, sell_num), (buy_name, buy_num) = offer
        sell_item, buy_item = self.backpack[sell_name], self.backpack[buy_name]

        sell_item.locked_num -= abs(sell_num)

        delta_volume = sell_item.capacity * sell_num + buy_item.capacity * buy_num
        if delta_volume > 0:
            self.backpack.locked_volume -= delta_volume

        self.offers[index] = None

    def memorize_action(self, action: ActionType):
        main_action, offer, _, _ = action
        self.last_action.main_action.primary = main_action[0]
        self.last_action.main_action.secondary = main_action[1]
        self.last_action.sell_offer.sell_item = offer[0][0] if offer else None
        self.last_action.sell_offer.sell_num = offer[0][1] if offer else None
        self.last_action.buy_offer.buy_item = offer[1][0] if offer else None
        self.last_action.buy_offer.buy_num = offer[1][1] if offer else None
