import argparse
import pathlib

from ecoevo.entities.map_generator import MapGenerator

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Generate map json")
    parser.add_argument("--type", type=str, default="rand")
    args = parser.parse_args()

    save_path = pathlib.Path(__file__).parent / "map.json"

    if args.type == "rand":
        MapGenerator.gen_rand_map(save_path=save_path)
