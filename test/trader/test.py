
import os
import random

import matplotlib.pyplot as plt
import matplotlib.patches as pch

from ecoevo.trader.trader import trade


""" generate data: random """

map_size = 64
num_offer = 100
ub_amount = 10

# offers
random.seed(42)
mat_agent = [[False for _ in range(map_size)] for _ in range(map_size)]
list_offer = []
for i in range(num_offer):
    # position
    x, y = random.randint(0, map_size - 1), random.randint(0, map_size - 1)
    while mat_agent[x][y]:
        x, y = random.randint(0, map_size - 1), random.randint(0, map_size - 1)
    mat_agent[x][y] = True

    # good amount
    amount = random.randint(1, ub_amount)

    list_offer.append({'position': (x, y), 'amount': amount})

distance_match = 4

# validation and volume
mat_if_match = [[False for _ in range(num_offer)] for _ in range(num_offer)]
mat_volume = [[0 for _ in range(num_offer)] for _ in range(num_offer)]
for i in range(num_offer):
    for j in range(num_offer):
        if i != j:
            pos_i, pos_j = list_offer[i]['position'], list_offer[j]['position']
            if abs(pos_i[0] - pos_j[0]) <= distance_match and abs(pos_i[1] - pos_j[1]) <= distance_match:
                mat_if_match[i][j] = True
                mat_volume[i][j] = min(list_offer[i]['amount'], list_offer[j]['amount'])


""" generate data: edge case """

# map_size = 4
# num_offer = 4

# list_offer = [
#     {'position': (0, 2), 'amount': 3}, 
#     {'position': (1, 1), 'amount': 10}, 
#     {'position': (2, 2), 'amount': 5}, 
#     {'position': (3, 1), 'amount': 4}
# ]

# mat_if_match = [[True if j != i else False for j in range(num_offer)] for i in range(num_offer)]
# mat_if_match[0][3], mat_if_match[3][0] = False, False

# mat_volume = [[min(
#     list_offer[i]['amount'], list_offer[j]['amount']) for j in range(num_offer)] for i in range(num_offer)]
# mat_volume[0][3], mat_volume[3][0] = 0, 0


""" model """

dict_match = trade(num_offer=num_offer, mat_if_match=mat_if_match, mat_volume=mat_volume)

print("get {} trades".format(len(dict_match)))


""" visualise """

fig, ax = plt.subplots()

# draw blocks and offers
len_block = 1
dict_offer = {offer['position']: offer['amount'] for offer in list_offer}
for y in range(map_size):
    for x in range(map_size):
        colour = 'red' if (x, y) in dict_offer.keys() else 'white'
        rectangle = pch.Rectangle(xy=(x * len_block, y * len_block), width=len_block, height=len_block, color=colour)
        ax.add_patch(rectangle)

        if (x, y) in dict_offer.keys():
            plt.text(x=x * len_block + len_block / 2, y=y * len_block + len_block / 2, s=str(dict_offer[x, y]))

# draw trades as lines
for t in dict_match.keys():
    pos_1 = (list_offer[t[0]]['position'][0] + len_block / 2, list_offer[t[0]]['position'][1] + len_block / 2)
    pos_2 = (list_offer[t[1]]['position'][0] + len_block / 2, list_offer[t[1]]['position'][1] + len_block / 2)
    plt.arrow(x=pos_1[0], y=pos_1[1], dx=pos_2[0] - pos_1[0], dy=pos_2[1] - pos_1[1], linestyle='-')

    plt.text(x=(pos_2[0] + pos_1[0]) / 2, y=(pos_2[1] + pos_1[1]) / 2, s=str(dict_match[t]), color='green')

# let the length of an x axis unit be equal with y axis
ax.set_aspect(1)

# 8 units an area
x_major_locator = plt.MultipleLocator(8)
y_major_locator = plt.MultipleLocator(8)
ax.xaxis.set_major_locator(x_major_locator)
ax.yaxis.set_major_locator(y_major_locator)

plt.xlim(xmin=0, xmax=map_size * len_block)
plt.ylim(ymin=0, ymax=map_size * len_block)
plt.grid(linestyle='dashed', linewidth=1)


""" save picture """

path = os.path.dirname(__file__)
path_output = os.path.join(path, "output/")

path_trade = os.path.join(path_output, 'trade.png')
# path_trade = os.path.join(path_output, 'trade_edge.png')
plt.savefig(path_trade)

