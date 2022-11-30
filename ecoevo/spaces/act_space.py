from gymnasium.spaces import Discrete
import gymnasium as gym


class Action(gym.Space):
    MOVE = 0
    COLLECT = 1
    CONSUME = 2
    TRADE = 3