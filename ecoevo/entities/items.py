import yaml
from yaml.loader import SafeLoader
from pydantic import BaseModel

with open('ecoevo/entities/items.yaml') as file:
    data = dict(yaml.load(file, Loader=SafeLoader))


class Item(BaseModel):
    name: str
    num: int
    supply: int
    grow_rate: float
    collect_time: int
    capacity: float
    harvest: int
    expiry: int
    disposable: bool


def load_item(name, num=0) -> Item:
    return Item(**{
        'name': name,
        'num': num,
        **data[name],
    })
