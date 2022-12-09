from typing import Tuple, Optional

# action = (('move', 'up'), ('sand', -5), ('gold', 10))
# action = (('consume', 'peanut'), ('gold', -5), ('peanut', 20))
# action = (('collect', None), None, None))


class Move:
    up = 'up'
    down = 'down'
    left = 'left'
    right = 'right'


class Action:
    move = 'move'
    collect = 'collect'
    consume = 'consume'


IdType = int
PosType = Tuple[int, int]
OfferType = Tuple[str, int]
MainActionType = Tuple[str, Optional[str]]

OrderType = Tuple[PosType, OfferType, OfferType]

ActionType = Tuple[MainActionType, OfferType, OfferType]