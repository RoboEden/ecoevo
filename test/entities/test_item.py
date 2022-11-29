from ecoevo.entities.items import ItemUtils
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv_path", type=str, help="csv path of item attr")
    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = parse_args()    
    item_attrs = ItemUtils.read_csv(args.csv_path, sep=",")
    print(item_attrs)