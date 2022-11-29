from dataclasses import dataclass
from enum import Enum


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
    NULL_UTILITY = 0
    NECESSITY = 1
    LUXURY = 2
    

@dataclass
class ItemConfig:
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
    

@dataclass
class EnvConfig:
    NUM_AGENTS: int
    TRAJ_LEN: int
    