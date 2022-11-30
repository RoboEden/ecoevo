
import os
import json

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as pch


""" generate block types """

dict_type_idx = {
    'empty': 0, 'gold': 1, 'pepper': 2, 'coral': 3, 'sand': 4, 'pineapple': 5, 'peanut': 6, 'stone': 7, 'pumpkin': 8
}
list_type = ['empty', 'gold', 'pepper', 'coral', 'sand', 'pineapple', 'peanut', 'stone', 'pumpkin']

# mat_type_area = [
#     [['coffee'], ['apple'], ['banana'], ['tea']], 
#     [['banana'], ['tea', 'coral'], ['coffee', 'coral'], ['apple']], 
#     [['coffee'], ['apple', 'coral'], ['banana', 'coral'], ['tea']], 
#     [['banana'], ['tea'], ['coffee'], ['apple']]]
# list_type_common = ['diamond', 'gold', 'platinum', 'wood', 'stone', 'coal', 'iron']

map_size = 64
area_size = 8
dict_if_rare = {
    'gold': True, 'pepper': True, 'coral': True, 'sand': False, 
    'pineapple': True, 'peanut': False, 'stone': False, 'pumpkin': False
}
num_block_rare, num_block_adequate = 2, 8

# generate the distribution of blocks
np.random.seed(42)
num_area_side = round(map_size / area_size)
mat_type_block = np.zeros(shape=(num_area_side * area_size, num_area_side * area_size))
for i in range(num_area_side):
    for j in range(num_area_side):
        mat_type_ = np.zeros(shape=(area_size, area_size))
        for t in list_type:
            if t == 'empty':
                continue

            num_block_ = num_block_rare if dict_if_rare[t] else num_block_adequate
            for k in range(num_block_):
                x, y = np.random.randint(low=0, high=area_size), np.random.randint(low=0, high=area_size)
                while mat_type_[x, y]:
                    x, y = np.random.randint(low=0, high=area_size), np.random.randint(low=0, high=area_size)
                mat_type_[x, y] = dict_type_idx[t]
        mat_type_block[area_size * i: area_size * (i + 1), area_size * j: area_size * (j + 1)] = mat_type_
mat_type_block = mat_type_block.astype('int').tolist()


""" visualise """

dict_type_colour = {
    'empty': 'white', 
    'gold': 'orange', 'pepper': 'brown', 'coral': 'pink', 'sand': 'grey', 
    'pineapple': 'lime', 'peanut': 'chocolate', 'stone': 'black', 'pumpkin': 'green'
}

fig, ax = plt.subplots()

shape_height, shape_width = len(mat_type_block), len(mat_type_block[0])
len_block = 1
for y in range(shape_height):
    for x in range(shape_width):
        rectangle = pch.Rectangle(
            xy=(x * len_block, (shape_height - y - 1) * len_block), 
            width=len_block, height=len_block, color=dict_type_colour[list_type[mat_type_block[y][x]]])
        ax.add_patch(rectangle)
        # plt.text(x=x + len_block / 2, y=shape_height - y - 1 + len_block / 2, s=str(mat_type_block[y][x]))

ax.set_aspect(1)
x_major_locator = plt.MultipleLocator(8)
y_major_locator = plt.MultipleLocator(8)
ax.xaxis.set_major_locator(x_major_locator)
ax.yaxis.set_major_locator(y_major_locator)

plt.xlim(xmin=0, xmax=shape_width * len_block)
plt.ylim(ymin=0, ymax=shape_height * len_block)
plt.grid(linestyle='dashed', linewidth=1)


""" save picture """

path = os.path.dirname(__file__)
path_files = os.path.join(path, "files/")

# save picture
path_picture = os.path.join(path_files, "map.png")
plt.savefig(path_picture)


""" save json """

mat_type = [[list_type[mat_type_block[i][j]] for j in range(map_size)] for i in range(map_size)]

amount = 10
dict_json = {
    "width": map_size, 
    "height": map_size, 
    "tiles": mat_type, 
    "amount": [[amount if mat_type_block[i][j] else 0 for j in range(map_size)] for i in range(map_size)]
}
json_map = json.dumps(dict_json)

# save
path_json = os.path.join(path_files, "base.json")
with open(path_json, 'w') as file:
    file.write(json_map)
