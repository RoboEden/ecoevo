from typing import Tuple, Optional


class Move:
    up = 'up'
    down = 'down'
    left = 'left'
    right = 'right'


class Action:
    idle = 'idle'
    move = 'move'
    collect = 'collect'
    consume = 'consume'

    
class TradeResult:
    absent  = 'absent'
    illegal = 'illegal'
    failed = 'failed'
    success = 'success'


IdType = int
PosType = Tuple[int, int]
OfferType = Tuple[str, int]
MainActionType = Tuple[str, Optional[str]]

DealType = Tuple[PosType, OfferType, OfferType]

ActionType = Tuple[MainActionType, OfferType, OfferType]