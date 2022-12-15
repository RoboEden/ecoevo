from rich import print
from ecoevo.entities.items import Bag, load_item


if __name__ == "__main__":
    gold = load_item('gold', num=100)
    print(id(gold))
    print(gold)

    gold1 = load_item('gold', num=100)
    print(id(gold1))
    print(gold1)

    bag = Bag()
    print(bag)
    print(bag.coral)
    print(bag.coral.num)
    print('=====================')
    print(bag.used_volume)
    print(bag.remain_volume)