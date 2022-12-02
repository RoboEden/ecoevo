class Action:
    MOVE_UP = 0
    MOVE_RIGHT = 1
    MOVE_DOWN = 2
    MOVE_LEFT = 3
    COLLECT = 4
    CONSUME = 5


class Trade:
    gold: 0
    pepper: 1
    coral: 2
    sand: 3
    pineapple: 4
    peanut: 5
    stone: 6
    pumpkin: 7


class ActionType:
    action: Action
    trade: Trade