import os
import json

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as pch

from ecoevo.data.items import ALL_ITEM_DATA

dict_type_idx = {key: ALL_ITEM_DATA[key]['id'] for key in ALL_ITEM_DATA.keys()}
dict_idx_type = {dict_type_idx[key]: key for key in dict_type_idx.keys()}
dict_idx_type[0] = 'empty'


def get_random_distribution(mat_type_area: np.ndarray, num_block_resource: int, type_item: str):
    """
    get random resource distribution of an area

    :param mat_type_area:  matrix of block types
    :param num_block_resource:  the number of resource blocks
    """

    ub_x, ub_y = mat_type_area.shape
    arr_pos = np.random.choice(a=ub_x * ub_y, size=num_block_resource, replace=False)
    for pos in arr_pos:
        x, y = pos // ub_y, pos % ub_y
        mat_type_area[x, y] = dict_type_idx[type_item]


# generate the distribution of blocks
np.random.seed(42)
map_size = 32
area_size = 10
empty_width = 1
num_block_resource = 32
mat_type_all = np.zeros(shape=(map_size, map_size))
for t in dict_type_idx.keys():
    if t == 'empty':
        continue

    elif t == 'gold':
        mat_type_area = np.zeros(shape=mat_type_all[:area_size, :area_size].shape)
        get_random_distribution(mat_type_area=mat_type_area, num_block_resource=num_block_resource, type_item=t)
        mat_type_all[:area_size, :area_size] = mat_type_area
    elif t == 'pineapple':
        mat_type_area = np.zeros(shape=mat_type_all[:area_size,
                                                    area_size + empty_width:-(area_size + empty_width)].shape)
        get_random_distribution(mat_type_area=mat_type_area, num_block_resource=num_block_resource, type_item=t)
        mat_type_all[:area_size, area_size + empty_width:-(area_size + empty_width)] = mat_type_area
    elif t == 'sand':
        mat_type_area = np.zeros(shape=mat_type_all[:area_size, -area_size:].shape)
        get_random_distribution(mat_type_area=mat_type_area, num_block_resource=num_block_resource, type_item=t)
        mat_type_all[:area_size, -area_size:] = mat_type_area
    elif t == 'pumpkin':
        mat_type_area = np.zeros(shape=mat_type_all[area_size +
                                                    empty_width:-(area_size + empty_width), :area_size].shape)
        get_random_distribution(mat_type_area=mat_type_area, num_block_resource=num_block_resource, type_item=t)
        mat_type_all[area_size + empty_width:-(area_size + empty_width), :area_size] = mat_type_area
    elif t == 'peanut':
        mat_type_area = np.zeros(shape=mat_type_all[area_size + empty_width:-(area_size + empty_width),
                                                    -area_size:].shape)
        get_random_distribution(mat_type_area=mat_type_area, num_block_resource=num_block_resource, type_item=t)
        mat_type_all[area_size + empty_width:-(area_size + empty_width), -area_size:] = mat_type_area
    elif t == 'stone':
        mat_type_area = np.zeros(shape=mat_type_all[-area_size:, :area_size].shape)
        get_random_distribution(mat_type_area=mat_type_area, num_block_resource=num_block_resource, type_item=t)
        mat_type_all[-area_size:, :area_size] = mat_type_area
    elif t == 'hazelnut':
        mat_type_area = np.zeros(shape=mat_type_all[-area_size:,
                                                    area_size + empty_width:-(area_size + empty_width)].shape)
        get_random_distribution(mat_type_area=mat_type_area, num_block_resource=num_block_resource, type_item=t)
        mat_type_all[-area_size:, area_size + empty_width:-(area_size + empty_width)] = mat_type_area
    elif t == 'coral':
        mat_type_area = np.zeros(shape=mat_type_all[-area_size:, -area_size:].shape)
        get_random_distribution(mat_type_area=mat_type_area, num_block_resource=num_block_resource, type_item=t)
        mat_type_all[-area_size:, -area_size:] = mat_type_area

mat_type_all = mat_type_all.astype('int').tolist()

# visualise
fig, ax = plt.subplots()

# draw blocks
len_block = 1
dict_type_colour = {
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
for x in range(map_size):
    for y in range(map_size):
        rectangle = pch.Rectangle(xy=(x * len_block, y * len_block),
                                  width=len_block,
                                  height=len_block,
                                  color=dict_type_colour[dict_idx_type[mat_type_all[x][y]]])
        ax.add_patch(rectangle)

# let the length of an x ax==unit be equal with y axis
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
mat_type_all_ = [[dict_idx_type[mat_type_all[i][j]] for j in range(map_size)] for i in range(map_size)]
dict_reserve = {key: ALL_ITEM_DATA[key]['reserve_num'] for key in ALL_ITEM_DATA.keys()}
dict_json = {
    "width":
    map_size,
    "height":
    map_size,
    "tiles":
    mat_type_all_,
    "amount":
    [[dict_reserve[mat_type_all_[i][j]] if mat_type_all[i][j] else 0 for j in range(map_size)] for i in range(map_size)]
}
json_map = json.dumps(dict_json)

# save json
path_json = os.path.join(path, "standard.json")
with open(path_json, 'w') as file:
    file.write(json_map)
