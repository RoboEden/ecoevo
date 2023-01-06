import json
import os

import matplotlib.patches as pch
import matplotlib.pyplot as plt


class MapVisualizer:

    @staticmethod
    def plot(data_path: str, save_path: str):
        with open(data_path, "r") as fp:
            map_data = json.load(fp)
            height = map_data["height"]
            width = map_data["width"]

            fig, ax = plt.subplots()

            # draw blocks
            block_size = 1
            tile_colors = {
                'empty': 'white',
                'gold': 'orange',
                'hazelnut': 'brown',
                'coral': 'pink',
                'sand': 'grey',
                'pineapple': 'lime',
                'peanut': 'chocolate',
                'stone': 'black',
                'pumpkin': 'green'
            }
            for y in range(height):
                for x in range(width):
                    item_type = map_data["tiles"][y][x]
                    color = tile_colors[item_type]
                    rectangle = pch.Rectangle(xy=(x * block_size, (height - y - 1) * block_size),
                                              width=block_size,
                                              height=block_size,
                                              color=color)
                    ax.add_patch(rectangle)

            # let the length of an x axis unit be equal with y axis
            ax.set_aspect(1)

            # 8 blocks an area
            dash_interval = 4
            x_major_locator = plt.MultipleLocator(dash_interval)
            y_major_locator = plt.MultipleLocator(dash_interval)
            ax.xaxis.set_major_locator(x_major_locator)
            ax.yaxis.set_major_locator(y_major_locator)

            plt.xlim(xmin=0, xmax=width * block_size)
            plt.ylim(ymin=0, ymax=height * block_size)
            plt.grid(linestyle='dashed', linewidth=1)

            # save picture
            plt.savefig(save_path)


if __name__ == "__main__":
    dir = os.path.dirname(__file__)
    data_path = os.path.join(dir, "map.json")
    save_path = os.path.join(dir, "map.jpg")
    MapVisualizer.plot(data_path, save_path)
