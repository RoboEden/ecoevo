import argparse
import json
import pathlib

from ecoevo.entities.map_generator import MapGenerator
from ecoevo.render.map_visualizer import MapVisualizer

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Generate map json")
    parser.add_argument("--type", type=str, default="rand")
    parser.add_argument("--width", type=int, default=32)
    parser.add_argument("--height", type=int, default=32)
    parser.add_argument("--num_per_item_type", type=int, default=32)
    parser.add_argument("--empty_width", type=int, default=2)
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()

    print(args)

    dir = pathlib.Path(__file__).parent

    if args.type == "rand":
        save_path = dir / "rand_map.json"
        MapGenerator.gen_rand_map(width=args.width,
                                  height=args.height,
                                  num_per_item_type=args.num_per_item_type,
                                  seed=args.seed,
                                  save_path=save_path)
    elif args.type == "regular":
        save_path = dir / "regular_map.json"
        MapGenerator.gen_regular_map(width=args.width,
                                     height=args.height,
                                     num_per_item_type=args.num_per_item_type,
                                     seed=args.seed,
                                     empty_width=args.empty_width,
                                     save_path=save_path)
    elif args.type == "fixed":
        save_path = dir / "fixed_map.json"
        data = MapGenerator.fixed_map()
        with open(save_path, "w") as fp:
            json.dump(data, fp)

    pic_path = dir / "map.jpg"
    MapVisualizer.plot(save_path, pic_path)
