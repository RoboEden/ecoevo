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
    alpha = config.alpha.gold
    grow_rate = 0
    collect_time = 100
    capacity = 0.01
    collect_amount = 1
    reserve = 1000
    expiry = INF
    reusable = True

class Pepper(Item):
    name = 'gold'
    supply = 0
    alpha = config.alpha.gold
    grow_rate = 0
    collect_time = 100
    capacity = 0.01
    collect_amount = 1
    reserve = 1000
    expiry = INF
    reusable = True

class Ivory(Item):
    name = 'gold'
    supply = 0
    alpha = config.alpha.gold
    grow_rate = 0
    collect_time = 100
    capacity = 0.01
    collect_amount = 1
    reserve = 1000
    expiry = INF
    reusable = True


class Shell(Item):
    name = 'gold'
    supply = 0
    alpha = config.alpha.gold
    grow_rate = 0
    collect_time = 100
    capacity = 0.01
    collect_amount = 1
    reserve = 1000
    expiry = INF
    reusable = True


class Pineapple(Item):
    name = 'gold'
    supply = 0
    alpha = config.alpha.gold
    grow_rate = 0
    collect_time = 100
    capacity = 0.01
    collect_amount = 1
    reserve = 1000
    expiry = INF
    reusable = True

class Peanut(Item):
    name = 'gold'
    supply = 0
    alpha = config.alpha.gold
    grow_rate = 0
    collect_time = 100
    capacity = 0.01
    collect_amount = 1
    reserve = 1000
    expiry = INF
    reusable = True

class Stone(Item):
    name = 'gold'
    supply = 0
    alpha = config.alpha.gold
    grow_rate = 0
    collect_time = 100
    capacity = 0.01
    collect_amount = 1
    reserve = 1000
    expiry = INF
    reusable = True

class Pumpkin(Item):
    name = 'gold'
    supply = 0
    alpha = config.alpha.gold
    grow_rate = 0
    collect_time = 100
    capacity = 0.01
    collect_amount = 1
    reserve = 1000
    expiry = INF
    reusable = True