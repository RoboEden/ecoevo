import yaml
from yaml.loader import SafeLoader


class Item:
    name: str
    supply: int
    grow_rate: float
    collect_time: int
    capacity: float
    harvest: int
    expiry: int
    disposable: bool

    def __init__(self, amount) -> None:
        self.amount = amount

    def __str__(self) -> str:
        return type(self).__name__


def get_item(name, amount) -> Item:
    with open('ecoevo/entities/items.yaml') as file:
        data = dict(yaml.load(file, Loader=SafeLoader))
    subclass = type(name, (Item, ), data[name])
    return subclass(amount)