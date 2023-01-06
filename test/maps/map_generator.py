import json
import random

import numpy as np
import yaml
from yaml.loader import SafeLoader

from ecoevo.config import DataPath


class MapGenerator:

    @staticmethod
    def gen_rand_map(seed: int = 1,
                     width: int = 32,
                     height: int = 32,
                     num_per_item_type: int = 32,
                     save_path: str = "map.json"):
        with open(DataPath.item_yaml) as file:
            item_attrs = dict(yaml.load(file, Loader=SafeLoader))
            assert width * height >= len(item_attrs) * num_per_item_type

            random.seed(seed)
            np.random.seed(seed=seed)

            data = {
                "width": width,
                "height": height,
                "tiles": [["empty" for _ in range(width)] for _ in range(height)],
                "amount": [[0 for _ in range(width)] for _ in range(height)],
            }

            num_item_tiles = num_per_item_type * len(item_attrs)
            idxs = np.random.choice(np.arange(width * height), num_item_tiles, replace=False)
            item_names = []
            for item_type in item_attrs:
                item_names += [item_type] * num_per_item_type
            assert len(item_names) == len(idxs)

            for idx, item_name in zip(idxs, item_names):
                row = idx // width
                col = idx % width
                data["tiles"][row][col] = item_name
                data["amount"][row][col] = item_attrs[item_name]["reserve_num"]

            with open(save_path, "w") as map_fp:
                json.dump(data, map_fp)


if __name__ == "__main__":
    MapGenerator.gen_rand_map()
