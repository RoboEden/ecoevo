import yaml
from yaml.loader import SafeLoader

with open('ecoevo/entities/items.yaml') as file:
    items = yaml.load(file, Loader=SafeLoader)


class Item:
    name: str
    supply: int
    grow_rate: float
    collect_time: int
    capacity: float
    collect_amount: int
    reserve: int
    expiry: int
    disposable: bool

    def __init__(self, amount) -> None:
        self.amount = amount
