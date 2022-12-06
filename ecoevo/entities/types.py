from typing import Tuple
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


PosType = Tuple[int, int]
OfferType = Tuple[str, int]

OrderType = Tuple[PosType, OfferType, OfferType]

MainActionType = Tuple[str, str]
ActionType = Tuple[MainActionType, OfferType, OfferType]