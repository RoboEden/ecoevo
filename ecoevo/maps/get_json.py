
import os
import json

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as pch


""" generate block types """

dict_type_idx = {
    'empty': 0, 'gold': 1, 'hazelnut': 2, 'coral': 3, 'sand': 4, 'pineapple': 5, 'peanut': 6, 'stone': 7, 'pumpkin': 8
}
list_type = ['empty', 'gold', 'hazelnut', 'coral', 'sand', 'pineapple', 'peanut', 'stone', 'pumpkin']

map_size = 32
area_size = 8
dict_reserve = {
    'gold': 5000, 'hazelnut': 100, 'coral': 5000, 'sand': 15000, 
    'pineapple': 100, 'peanut': 100, 'stone': 15000, 'pumpkin': 100
}

# generate the distribution of blocks
np.random.seed(42)
mat_type_all = np.zeros(shape=(map_size, map_size))
num_block_resource = 32
for t in list_type:
    if t == 'empty':
        continue

    mat_type_area = np.zeros(shape=(area_size, area_size))
    for i in range(num_block_resource):
        x, y = np.random.randint(low=0, high=area_size), np.random.randint(low=0, high=area_size)
        while mat_type_area[x, y]:
            x, y = np.random.randint(low=0, high=area_size), np.random.randint(low=0, high=area_size)
        mat_type_area[x, y] = dict_type_idx[t]

    if t == 'gold':
        mat_type_all[0: 8, 0: 8] = mat_type_area
    elif t == 'pineapple':
        mat_type_all[0: 8, 12: 20] = mat_type_area
    elif t == 'sand':
        mat_type_all[0: 8, 24: 32] = mat_type_area
    elif t == 'pumpkin':
        mat_type_all[12: 20, 0: 8] = mat_type_area
    elif t == 'peanut':
        mat_type_all[12: 20, 24: 32] = mat_type_area
    elif t == 'stone':
        mat_type_all[24: 32, 0: 8] = mat_type_area
    elif t == 'hazelnut':
        mat_type_all[24: 32, 12: 20] = mat_type_area
    elif t == 'coral':
        mat_type_all[24: 32, 24: 32] = mat_type_area

mat_type_all = mat_type_all.astype('int').tolist()


""" visualise """

dict_type_colour = {
    'empty': 'white', 
    'gold': 'orange', 'hazelnut': 'brown', 'coral': 'pink', 'sand': 'grey', 
    'pineapple': 'lime', 'peanut': 'chocolate', 'stone': 'black', 'pumpkin': 'green'
}

fig, ax = plt.subplots()

# draw blocks
len_block = 1
for y in range(map_size):
    for x in range(map_size):
        rectangle = pch.Rectangle(
            xy=(x * len_block, (map_size - y - 1) * len_block), 
            width=len_block, height=len_block, color=dict_type_colour[list_type[mat_type_all[y][x]]])
        ax.add_patch(rectangle)
        # plt.text(x=x + len_block / 2, y=map_size - y - 1 + len_block / 2, s=str(mat_type_all[y][x]))

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


""" save picture """

path = os.path.dirname(__file__)
path_files = os.path.join(path, "data/")

# save picture
path_picture = os.path.join(path_files, "map.png")
plt.savefig(path_picture)


""" save json """

mat_type_all_ = [[list_type[mat_type_all[i][j]] for j in range(map_size)] for i in range(map_size)]

dict_json = {
    "width": map_size, 
    "height": map_size, 
    "tiles": mat_type_all_, 
    "amount": [[dict_reserve[
        mat_type_all_[i][j]] if mat_type_all[i][j] else 0 for j in range(map_size)] for i in range(map_size)]
}
json_map = json.dumps(dict_json)

# save
path_json = os.path.join(path_files, "base.json")
with open(path_json, 'w') as file:
    file.write(json_map)
