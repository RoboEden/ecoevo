import json
import random
from typing import Dict

import numpy as np

from ecoevo.config import MapConfig
from ecoevo.data.items import ALL_ITEM_DATA


class MapGenerator:

    @staticmethod
    def gen_rand_map(width: int = 32,
                     height: int = 32,
                     num_per_item_type: int = 32,
                     save_path: str = "map.json",
                     seed: int = 1):
        assert width > 0 and height > 0 and num_per_item_type > 0
        assert width * height >= len(ALL_ITEM_DATA) * num_per_item_type

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
        num_items = num_per_item_type * len(ALL_ITEM_DATA)
        idxs = np.random.choice(np.arange(width * height), num_items, replace=False)
        item_names = []
        for item_name in ALL_ITEM_DATA:
            item_names += [item_name] * num_per_item_type
        assert len(item_names) == len(idxs)

        for idx, item_name in zip(idxs, item_names):
            row = idx // width
            col = idx % width

            assert data["tiles"][row][col] == "empty"
            assert data["amount"][row][col] == 0

            data["tiles"][row][col] = item_name
            data["amount"][row][col] = ALL_ITEM_DATA[item_name]["reserve_num"]

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
                        empty_width: int = 2,
                        save_path: str = "regular_map.json",
                        seed: int = 1):
        # Seeding
        if seed:
            random.seed(seed)
            np.random.seed(seed=seed)

        # Init
        data = MapGenerator.init_data(width=width, height=height)

        # Block
        num_blocks = len(ALL_ITEM_DATA) + 1
        num_tiles_per_block = width * height // num_blocks
        # block_width * block_height = num_tiles_per_block
        # block_width / block_height = width / height
        # width / height * block_height * block_height = num_tiles_per_block
        block_height = np.sqrt(num_tiles_per_block * height / width)
        block_width = num_tiles_per_block / block_height
        block_height = int(block_height)
        block_width = int(block_width)
        assert block_height > 0 \
                and block_width > 0 \
                and block_width * block_height * num_blocks <= width * height \
                and block_width * block_height >= num_per_item_type + empty_width*(block_height+block_width)*2 - 4*empty_width*empty_width

        # Scatter items in block
        item_types = list(ALL_ITEM_DATA.keys())
        for block_x in range(width // block_width):
            for block_y in range(height // block_height):
                block_idx = block_x + block_y * width // block_width
                if block_idx >= len(item_types):
                    continue
                item_type = item_types[block_idx]
                top_left_pos = (block_x * block_width, block_y * block_height)
                cnt = num_per_item_type
                for w in range(empty_width, block_width - empty_width):
                    for h in range(empty_width, block_height - empty_width):
                        if cnt <= 0:
                            break
                        col = top_left_pos[0] + w
                        row = top_left_pos[1] + h
                        cnt = cnt - 1
                        data["tiles"][row][col] = item_type
                        data["amount"][row][col] = ALL_ITEM_DATA[item_type]["reserve_num"]

            # Serialization
            with open(save_path, "w") as map_fp:
                json.dump(data, map_fp)

    @staticmethod
    def gen_food_map(width: int = MapConfig.width,
                     height: int = MapConfig.height,
                     num_block_item: int = MapConfig.generate_num_block_resource,
                     size_area: int = 10) -> Dict:
        """
        generate map with only foods
        
        :param width:  map width
        :param height:  map height
        :param num_block_item:  number of blocks of each item
        :param size_area:  size of each item area
        
        :return: data:  map tiles data
        """

        data = MapGenerator.init_data(width=width, height=height)

        # list_item = [item for item in ALL_ITEM_DATA.keys() if ALL_ITEM_DATA[item]['disposable']]
        list_item = ['peanut', 'pineapple', 'pumpkin', 'hazelnut']

        # check items and size
        assert len(list_item) == 4
        assert width == height
        assert size_area <= int(width / 3)

        # area range
        range_top = ((int(width / 2 - size_area / 2), int(width / 2 - size_area / 2) + size_area - 1),
                     (height - size_area, height - 1))
        range_left = ((0, size_area - 1), (int(height / 2 - size_area / 2),
                                           int(height / 2 - size_area / 2) + size_area - 1))
        range_right = ((width - size_area, width - 1), (int(height / 2 - size_area / 2),
                                                        int(height / 2 - size_area / 2) + size_area - 1))
        range_down = ((int(width / 2 - size_area / 2), int(width / 2 - size_area / 2) + size_area - 1), (0,
                                                                                                         size_area - 1))
        list_range = [range_top, range_right, range_down, range_left]

        # get item tiles
        np.random.seed(42)
        for i in range(len(list_item)):
            range_area = list_range[i]
            num_block_area = (range_area[0][1] - range_area[0][0] + 1) * (range_area[1][1] - range_area[1][0] + 1)
            list_choice = np.random.choice(a=num_block_area, size=num_block_item, replace=False)
            list_tile_item = [(range_area[0][0] + idx // size_area, range_area[1][0] + idx % size_area)
                              for idx in list_choice]

            for pos in list_tile_item:
                data["tiles"][pos[0]][pos[1]] = list_item[i]
                data["amount"][pos[0]][pos[1]] = ALL_ITEM_DATA[list_item[i]]["reserve_num"]

        return data

    @staticmethod
    def gen_food_durable_mix_map(width: int = MapConfig.width,
                                 height: int = MapConfig.height,
                                 num_block_item: int = MapConfig.generate_num_block_resource,
                                 size_area: int = 10) -> Dict:
        """
        generate map with only foods
        
        :param width:  map width
        :param height:  map height
        :param num_block_item:  number of blocks of each item
        :param size_area:  size of each item area
        
        :return: data:  map tiles data
        """

        data = MapGenerator.init_data(width=width, height=height)

        list_item = [['peanut', 'coral'], ['pineapple', 'sand'], ['pumpkin', 'gold'], ['hazelnut', 'stone']]

        # check items and size
        assert len(list_item) == 4
        assert width == height
        assert size_area <= int(width / 3)

        # area range
        range_top = ((int(width / 2 - size_area / 2), int(width / 2 - size_area / 2) + size_area - 1),
                     (height - size_area, height - 1))
        range_left = ((0, size_area - 1), (int(height / 2 - size_area / 2),
                                           int(height / 2 - size_area / 2) + size_area - 1))
        range_right = ((width - size_area, width - 1), (int(height / 2 - size_area / 2),
                                                        int(height / 2 - size_area / 2) + size_area - 1))
        range_down = ((int(width / 2 - size_area / 2), int(width / 2 - size_area / 2) + size_area - 1), (0,
                                                                                                         size_area - 1))
        list_range = [range_top, range_right, range_down, range_left]

        # get item tiles
        np.random.seed(42)
        for i in range(len(list_item)):
            range_area = list_range[i]
            num_block_area = (range_area[0][1] - range_area[0][0] + 1) * (range_area[1][1] - range_area[1][0] + 1)
            list_choice = np.random.choice(a=num_block_area, size=num_block_item * 2, replace=False)
            list_tile_item = [(range_area[0][0] + idx // size_area, range_area[1][0] + idx % size_area)
                              for idx in list_choice]

            for j in range(len(list_tile_item)):
                pos = list_tile_item[j]
                item = list_item[i][0] if not j % 2 else list_item[i][1]
                data["tiles"][pos[0]][pos[1]] = item
                data["amount"][pos[0]][pos[1]] = ALL_ITEM_DATA[item]["reserve_num"]

        return data

    @staticmethod
    def fixed_map(width=32, height=32, block_size=10, outer=1, inner_gap=2, num_per_item_type=9) -> Dict:
        data = MapGenerator.init_data(width=width, height=height)

        item_names = list(ALL_ITEM_DATA.keys())
        item_names.insert(4, "empty")
        for block_x in range((width - outer * 2) // block_size):
            for block_y in range((height - outer * 2) // block_size):
                if block_x == 1 and block_y == 1:
                    continue
                block_idx = block_x + block_y * (width - outer * 2) // block_size
                item_name = item_names[block_idx]

                top_left = (outer + 1 + block_x * block_size, outer + 1 + block_y * block_size)
                cur_pos = list(top_left)
                for i in range(num_per_item_type):
                    col = cur_pos[0]
                    row = cur_pos[1]
                    data["tiles"][row][col] = item_name
                    data["amount"][row][col] = ALL_ITEM_DATA[item_name]["reserve_num"]
                    cur_pos[0] += 1 + inner_gap
                    if cur_pos[0] >= top_left[0] + block_size - 1:
                        cur_pos[0] = top_left[0]
                        cur_pos[1] += 1 + inner_gap

        return data
