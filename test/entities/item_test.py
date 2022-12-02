import argparse
from rich import print
from ecoevo.entities.items import Bag, load_item


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv_path", type=str, help="csv path of item attr")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
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
    print(bag.remain_volume)
