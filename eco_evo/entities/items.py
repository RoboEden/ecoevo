import numpy as np
from enum import Enum
from dataclasses import dataclass


class ItemName(Enum):
    GOLD = 0
    PEPPER = 1
    IVORY = 2
    SHELL = 3
    PINEAPPLE = 4
    APPLE = 5
    STONE = 6
    PUMPKIN = 7


class Granularity(Enum):
    SMALL = 0
    LARGE = 1


class ReserveType(Enum):
    RARE = 0
    ADEQUATE = 1
    

class ObtainGrade(Enum):
    EASY = 0
    HARD = 1


class GoodsType(Enum):
    NO_UTILITY = 0
    NECESSITY = 1
    LUXURY = 2
    

@dataclass
class ItemAttrs:
    item_name: ItemName
    disposable: bool
    granularity: Granularity
    reserve_type: ReserveType
    obtain_grade: ObtainGrade
    renewable: bool
    general_accept: bool
    storage_time: int
    is_supplement: bool
    alpha: float
    beta: float
    collect_duration: int
    total_amount: int
    goods_type: GoodsType
    

class Item:
    def __init__(self, amount: int, **kwargs) -> None:
        self._amount = amount