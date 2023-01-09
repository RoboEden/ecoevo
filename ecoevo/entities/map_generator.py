import json
import random

import numpy as np
import yaml
from yaml.loader import SafeLoader

from ecoevo.config import DataPath


class MapGenerator:

    @staticmethod
    def gen_rand_map(width: int = 32,
                     height: int = 32,
                     num_per_item_type: int = 32,
                     save_path: str = "map.json",
                     seed: int = 1):
        with open(DataPath.item_yaml) as fp:
            item_attrs = dict(yaml.load(fp, Loader=SafeLoader))

            assert width > 0 and height > 0 and num_per_item_type > 0
            assert width * height >= len(item_attrs) * num_per_item_type

            # Seeding
            if seed:
                random.seed(seed)
                np.random.seed(seed=seed)

            # Init
            data = {
                "width": width,
                "height": height,
                "tiles": [["empty" for _ in range(width)] for _ in range(height)],
                "amount": [[0 for _ in range(width)] for _ in range(height)]
            }

            # Random allocation
            num_items = num_per_item_type * len(item_attrs)
            idxs = np.random.choice(np.arange(width * height), num_items, replace=False)
            item_names = []
            for item_name in item_attrs:
                item_names += [item_name] * num_per_item_type
            assert len(item_names) == len(idxs)

            for idx, item_name in zip(idxs, item_names):
                row = idx // width
                col = idx % width

                assert data["tiles"][row][col] == "empty"
                assert data["amount"][row][col] == 0

                data["tiles"][row][col] = item_name
                data["amount"][row][col] = item_attrs[item_name]["reserve_num"]

            # Serialization
            with open(save_path, "w") as map_fp:
                json.dump(data, map_fp)
