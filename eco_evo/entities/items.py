import functools
from enum import Enum
from dataclasses import dataclass
import numpy as np
import pandas as pd


class ItemType(Enum):
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
    item_name: ItemType
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
    

class ItemUtils:
    @staticmethod
    @functools.lru_cache(maxsize=None)
    def read_csv(csv_path: str, sep=",") -> pd.DataFrame:
        df = pd.read_csv(csv_path, sep=sep)
        return df
        

class Item:
    def __init__(self, item_type: ItemType, amount: int) -> None:
        self._item_type = item_type
        self._amount = amount
        
    @property
    def item_type(self) -> ItemType:
        return self._item_type
    
    @property
    def amount(self) -> int:
        return self._amount
    
    