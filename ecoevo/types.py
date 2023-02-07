from typing import Tuple, Optional


class Move:
    up = "up"
    down = "down"
    left = "left"
    right = "right"


class Action:
    idle = "idle"
    move = "move"
    collect = "collect"
    consume = "consume"
    wipeout = "wipeout"


class TradeResult:
    absent = "absent"
    illegal = "illegal"
    failed = "failed"
    success = "success"


IdType = int
PosType = Tuple[int, int]
OfferType = Tuple[str, int]
MainActionType = Tuple[str, Optional[str]]

DealType = Tuple[PosType, OfferType, OfferType]

ActionType = Tuple[MainActionType, OfferType, OfferType]

from pydantic import BaseModel, Field


class SellOffer(BaseModel):
    sell_item: Optional[str]
    sell_num: Optional[int]


class BuyOffer(BaseModel):
    buy_item: Optional[str]
    buy_num: Optional[int]


class MainAction(BaseModel):
    primary: str = Field(default="idle")
    secondary: Optional[str]


class xAction(BaseModel):
    main_action: MainAction = Field(default_factory=MainAction)
    sell_offer: SellOffer = Field(default_factory=SellOffer)
    buy_offer: BuyOffer = Field(default_factory=BuyOffer)
