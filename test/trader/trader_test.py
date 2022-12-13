import os
import random
from rich import print

import matplotlib.pyplot as plt
import matplotlib.patches as pch

from ecoevo.trader.trader import Trader
""" generate data: random """

map_size = 32
num_deal = 128
ub_amount = 10

# deals
random.seed(42)
mat_player = [[False for _ in range(map_size)] for _ in range(map_size)]
list_deal = []
for i in range(num_deal):
    # position
    x, y = random.randint(0, map_size - 1), random.randint(0, map_size - 1)
    while mat_player[x][y]:
        x, y = random.randint(0, map_size - 1), random.randint(0, map_size - 1)
    mat_player[x][y] = True

    # good amount
    amount = random.randint(1, ub_amount)

    # full case
    deal = ((x, y), ('gold', -amount), ('gold', amount))
    # couple case
    # deal = ((x, y), ('peanut', -amount), ('gold', amount)) if not i % 2 else (
    #     (x, y), ('gold', -amount), ('peanut', amount))

    list_deal.append(deal)
""" generate data: edge case """

# map_size = 16

# list_deal = [
#     ((0, 0), ('peanut', -3), ('gold', 3)),
#     ((4, 0), ('gold', -10), ('peanut', 10)),
#     ((6, 4), ('peanut', -5), ('gold', 5)),
#     ((10, 4), ('gold', -4), ('peanut', 4))
# ]
""" model """

trade_radius = 4
trader = Trader(trade_radius=trade_radius)

dict_deal = {i: list_deal[i] for i in range(len(list_deal))}
_ = trader.parse(legal_deals=dict_deal)

print("get {} trades".format(len(trader.list_match)))
""" visualise """

fig, ax = plt.subplots()

# draw blocks and deals
len_block = 1
dict_deal = {deal[0]: min(abs(deal[1][1]), deal[2][1]) for deal in list_deal}
for y in range(map_size):
    for x in range(map_size):
        colour = 'red' if (x, y) in dict_deal.keys() else 'white'
        rectangle = pch.Rectangle(xy=(x * len_block, y * len_block),
                                  width=len_block,
                                  height=len_block,
                                  color=colour)
        ax.add_patch(rectangle)

        if (x, y) in dict_deal.keys():
            plt.text(x=x * len_block + len_block / 2,
                     y=y * len_block + len_block / 2,
                     s=str(dict_deal[x, y]))

# draw trades as lines
list_match, mat_volume = trader.list_match, trader.mat_volume
for t in list_match:
    pos_1 = (list_deal[t[0]][0][0] + len_block / 2,
             list_deal[t[0]][0][1] + len_block / 2)
    pos_2 = (list_deal[t[1]][0][0] + len_block / 2,
             list_deal[t[1]][0][1] + len_block / 2)
    plt.arrow(x=pos_1[0],
              y=pos_1[1],
              dx=pos_2[0] - pos_1[0],
              dy=pos_2[1] - pos_1[1],
              linestyle='-')

    plt.text(x=(pos_2[0] + pos_1[0]) / 2,
             y=(pos_2[1] + pos_1[1]) / 2,
             s=str(mat_volume[t[0]][t[1]]),
             color='green')

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
