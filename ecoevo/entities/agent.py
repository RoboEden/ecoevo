from enum import Enum

class Action(Enum):
    MOVE = 0
    COLLECT = 1
    CONSUME = 2
    TRADE = 3

class Agent:
    def __init__(self, type:str):
        self.preference = type.preference
        self.ability = type.ability

    def execute(action:Action):
        return action.value
