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

    @staticmethod
    def init_data(width: int, height: int):
        data = {
            "width": width,
            "height": height,
            "tiles": [["empty" for _ in range(width)] for _ in range(height)],
            "amount": [[0 for _ in range(width)] for _ in range(height)]
        }
        return data

    @staticmethod
    def gen_regular_map(width: int = 32,
                        height: int = 32,
                        num_per_item_type: int = 16,
                        save_path: str = "regular_map.json",
                        seed: int = 1):
        # Seeding
        if seed:
            random.seed(seed)
            np.random.seed(seed=seed)

        # Init
        data = MapGenerator.init_data(width=width, height=height)

        # Block
        with open(DataPath.item_yaml) as fp:
            item_attrs = dict(yaml.load(fp, Loader=SafeLoader))
            num_blocks = len(item_attrs) + 1
            num_tiles_per_block = width * height // num_blocks
            # block_width * block_height = num_tiles_per_block
            # block_width / block_height = width / height
            # width / height * block_height * block_height = num_tiles_per_block
            block_height = np.sqrt(num_tiles_per_block * height / width)
            block_width = num_tiles_per_block / block_height
            block_height = int(block_height)
            block_width = int(block_width)
            assert block_height > 0 and block_width > 0 and block_width * block_height * num_blocks <= width * height

            # Scatter items in block
            item_types = list(item_attrs.keys())
            for block_x in range(width // block_width):
                for block_y in range(height // block_height):
                    block_idx = block_x + block_y * width // block_width
                    if block_idx >= len(item_types):
                        continue
                    item_type = item_types[block_idx]
                    top_left_pos = (block_x * block_width, block_y * block_height)
                    cnt = num_per_item_type
                    for w in range(block_width):
                        for h in range(block_height):
                            if cnt <= 0:
                                break
                            row = top_left_pos[0] + w
                            col = top_left_pos[1] + h
                            cnt = cnt - 1
                            data["tiles"][row][col] = item_type
                            data["amount"][row][col] = item_attrs[item_type]["reserve_num"]

            # Serialization
            with open(save_path, "w") as map_fp:
                json.dump(data, map_fp)
