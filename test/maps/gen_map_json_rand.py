import os
import json
import yaml
import random

import matplotlib.pyplot as plt
import matplotlib.patches as pch

from ecoevo.config import DataPath


# item info for tile types
with open(DataPath.item_yaml) as file:
    dict_item = dict(yaml.load(file, Loader=yaml.loader.SafeLoader))
dict_type_idx = {key: dict_item[key]['id'] for key in dict_item.keys()}
dict_idx_type = {dict_type_idx[key]: key for key in dict_type_idx.keys()}
dict_idx_type[0] = 'empty'


# generate the distribution of blocks
random.seed(42)
map_size = 32
num_block_resource = 32
mat_type = [[0 for _ in range(map_size)] for _ in range(map_size)]
for t in dict_type_idx.keys():
    if t != 'empty':
        for _ in range(num_block_resource):
            x, y = random.randint(0, map_size - 1), random.randint(0, map_size - 1)
            while mat_type[x][y]:
                x, y = random.randint(0, map_size - 1), random.randint(0, map_size - 1)
            mat_type[x][y] = dict_type_idx[t]


# visualise
fig, ax = plt.subplots()

# draw blocks
len_block = 1
dict_type_colour = {
    'empty': 'white', 
    'gold': 'orange', 'hazelnut': 'brown', 'coral': 'pink', 'sand': 'grey', 
    'pineapple': 'lime', 'peanut': 'chocolate', 'stone': 'black', 'pumpkin': 'green'
}
for y in range(map_size):
    for x in range(map_size):
        rectangle = pch.Rectangle(
            xy=(x * len_block, (map_size - y - 1) * len_block), 
            width=len_block, height=len_block, color=dict_type_colour[dict_idx_type[mat_type[y][x]]])
        ax.add_patch(rectangle)
        # plt.text(x=x + len_block / 2, y=map_size - y - 1 + len_block / 2, s=str(mat_type[y][x]))

# let the length of an x axis unit be equal with y axis
ax.set_aspect(1)

# 8 blocks an area
dash_interval = 4
x_major_locator = plt.MultipleLocator(dash_interval)
y_major_locator = plt.MultipleLocator(dash_interval)
ax.xaxis.set_major_locator(x_major_locator)
ax.yaxis.set_major_locator(y_major_locator)

plt.xlim(xmin=0, xmax=map_size * len_block)
plt.ylim(ymin=0, ymax=map_size * len_block)
plt.grid(linestyle='dashed', linewidth=1)


# save picture
path = os.path.dirname(__file__)
path_picture = os.path.join(path, "map.png")
plt.savefig(path_picture)


# get json
mat_type_ = [[dict_idx_type[mat_type[i][j]] for j in range(map_size)] for i in range(map_size)]
dict_reserve = {key: dict_item[key]['reserve_num'] for key in dict_item.keys()}
dict_json = {
    "width": map_size, 
    "height": map_size, 
    "tiles": mat_type_, 
    "amount": [[dict_reserve[
        mat_type_[i][j]] if mat_type[i][j] else 0 for j in range(map_size)] for i in range(map_size)]
}
json_map = json.dumps(dict_json)

# save json
path_json = os.path.join(path, "base.json")
with open(path_json, 'w') as file:
    file.write(json_map)
