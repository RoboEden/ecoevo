from ecoevo.entities import items
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv_path", type=str, help="csv path of item attr")
    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = parse_args()
    gold = items.Gold(reserve=10)
    print(gold)

    