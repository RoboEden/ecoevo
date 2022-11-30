from ecoevo.entities.items import Item, get_item
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv_path", type=str, help="csv path of item attr")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    gold = get_item('gold', 100)
    print(gold.amount)
    print(gold.expiry)
    print(gold.capacity)
    print(gold.grow_rate)
    print(gold.harvest)
    print(gold.collect_time)