import numpy as np

INF = 999999


class Item:
    name: str
    supply: int
    alpha: float
    grow_rate: float
    collect_time: int
    capacity: float
    collect_amount: int
    reserve: int
    expiry: int
    reusable: bool

    def __init__(self, reserve) -> None:
        self.reserve = reserve


class Gold(Item):
    name = 'gold'
    supply = 0
    alpha = None
    grow_rate = 0
    collect_time = 100
    capacity = 0.01
    collect_amount = 1
    reserve = 1000
    expiry = INF
    reusable = True


class Pepper(Item):
    name = 'pepper'
    supply = 0
    alpha = None
    grow_rate = 0
    collect_time = 100
    capacity = 0.01
    collect_amount = 1
    reserve = 1000
    expiry = INF
    reusable = True


class Coral(Item):
    name = 'coral'
    supply = 0
    alpha = None
    grow_rate = 0
    collect_time = 100
    capacity = 0.01
    collect_amount = 1
    reserve = 1000
    expiry = INF
    reusable = True


class Sand(Item):
    name = 'sand'
    supply = 0
    alpha = None
    grow_rate = 0
    collect_time = 100
    capacity = 0.01
    collect_amount = 1
    reserve = 1000
    expiry = INF
    reusable = True


class Pineapple(Item):
    name = 'pineapple'
    supply = 0
    alpha = None
    grow_rate = 0
    collect_time = 100
    capacity = 0.01
    collect_amount = 1
    reserve = 1000
    expiry = INF
    reusable = True


class Peanut(Item):
    name = 'peanut'
    supply = 0
    alpha = None
    grow_rate = 0
    collect_time = 100
    capacity = 0.01
    collect_amount = 1
    reserve = 1000
    expiry = INF
    reusable = True


class Stone(Item):
    name = 'stone'
    supply = 0
    alpha = None
    grow_rate = 0
    collect_time = 100
    capacity = 0.01
    collect_amount = 1
    reserve = 1000
    expiry = INF
    reusable = True


class Pumpkin(Item):
    name = 'pumpkin'
    supply = 0
    alpha = None
    grow_rate = 0
    collect_time = 100
    capacity = 0.01
    collect_amount = 1
    reserve = 1000
    expiry = INF
    reusable = True