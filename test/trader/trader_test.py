import os
import random
from rich import print

import matplotlib.pyplot as plt
import matplotlib.patches as pch

from ecoevo.trader.trader import Trader
from ecoevo.entities.player import Player


case_index = 0

# general case
if case_index == 0:
    random.seed(42)
    map_size = 32
    num_deal = 128
    ub_amount = 10
    legal_deals = {}
    mat_player = [[False for _ in range(map_size)] for _ in range(map_size)]
    for i in range(num_deal):
        # position
        x, y = random.randint(0, map_size - 1), random.randint(0, map_size - 1)
        while mat_player[x][y]:
            x, y = random.randint(0, map_size - 1), random.randint(0, map_size - 1)
        mat_player[x][y] = True
        
        # good amount
        amount = random.randint(1, ub_amount)
        deal = ((x, y), ('gold', -amount), ('gold', amount)) if not i % 2 else (
            (x, y), ('gold', -amount), ('gold', amount))
        legal_deals[i] = deal

# an edge case
else:
    map_size = 16
    legal_deals = {
        0: ((0, 0), ('gold', -3), ('gold', 3)), 
        1: ((4, 0), ('gold', -10), ('gold', 10)), 
        2: ((6, 4), ('gold', -5), ('gold', 5)), 
        3: ((10, 4), ('gold', -4), ('gold', 4))
    }


# initialise trader
trade_radius = 4
trader = Trader(trade_radius=trade_radius)
trader.legal_deals = legal_deals
# trader.mode = 'ip'
trader.mode = 'heu'

if trader.mode == 'ip':
    # run model
    list_deal = list(legal_deals.values())
    mat_if_match, mat_volume = trader._ip_process(list_deal=list_deal)
    list_match = trader._ip_model(list_deal=list_deal, mat_if_match=mat_if_match, mat_volume=mat_volume)
    print("get {} trades".format(len(list_match)), '\n')

    fig, ax = plt.subplots()

    # draw blocks and deals
    len_block = 1
    dict_deal = {deal[0]: min(abs(deal[1][1]), deal[2][1]) for deal in list_deal}
    for y in range(map_size):
        for x in range(map_size):
            colour = 'red' if (x, y) in dict_deal else 'white'
            rectangle = pch.Rectangle(xy=(
                x * len_block, y * len_block), width=len_block, height=len_block, color=colour)
            ax.add_patch(rectangle)
            
            if (x, y) in dict_deal:
                plt.text(x=x * len_block + len_block / 2, y=y * len_block + len_block / 2, s=str(dict_deal[x, y]))
                
    # draw trades as lines
    idx_pos = 0
    for (i, j) in list_match:
        pos_1 = (list_deal[i][idx_pos][0] + len_block / 2, list_deal[i][idx_pos][1] + len_block / 2)
        pos_2 = (list_deal[j][idx_pos][0] + len_block / 2, list_deal[j][idx_pos][1] + len_block / 2)
        plt.arrow(x=pos_1[0], y=pos_1[1], dx=pos_2[0] - pos_1[0], dy=pos_2[1] - pos_1[1], linestyle='-')
        plt.text(x=(pos_2[0] + pos_1[0]) / 2, y=(pos_2[1] + pos_1[1]) / 2, s=str(mat_volume[i][j]), color='green')
            
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
    
    # save picture
    path = os.path.dirname(__file__)
    path_output = os.path.join(path, "output/")
    path_trade = os.path.join(path_output, 'trade.png')
    plt.savefig(path_trade)

else:
    # add player info
    for i in legal_deals:
        player = Player(persona='', id=i, pos=legal_deals[i][0])
        trader.players.append(player)

    # run algorithm
    match_deals, dict_flow = trader._heuristic()
    print("{} deals matched".format(len(match_deals)), '\n')
    
    # total trade amount
    idx_item_num = 1
    total_trade_amount = sum(min(abs(item[idx_item_num]) for item in dict_flow[t]) for t in dict_flow)
    print("total trade amount: {}".format(total_trade_amount), '\n')

    fig, ax = plt.subplots()

    # draw blocks and deals
    len_block = 1
    idx_sell, idx_buy = 1, 2
    dict_deal = {trader.legal_deals[i][0]: (trader.legal_deals[i][idx_sell][idx_item_num], trader.legal_deals[
        i][idx_buy][idx_item_num]) for i in trader.legal_deals}
    for y in range(map_size):
        for x in range(map_size):
            colour = 'red' if (x, y) in dict_deal else 'white'
            rectangle = pch.Rectangle(xy=(
                x * len_block, y * len_block), width=len_block, height=len_block, color=colour)
            ax.add_patch(rectangle)
            
            if (x, y) in dict_deal:
                plt.text(x=x * len_block + len_block / 2, y=y * len_block + len_block / 2, s=str(dict_deal[x, y]))
                
    # draw trades as lines
    idx_pos = 0
    for (i, j) in dict_flow:
        deal_1, deal_2 = trader.legal_deals[i], trader.legal_deals[j]
        pos_1 = (deal_1[idx_pos][0] + len_block / 2, deal_1[idx_pos][1] + len_block / 2)
        pos_2 = (deal_2[idx_pos][0] + len_block / 2, deal_2[idx_pos][1] + len_block / 2)
        plt.arrow(x=pos_1[0], y=pos_1[1], dx=pos_2[0] - pos_1[0], dy=pos_2[1] - pos_1[1], linestyle='-')

        idx_sell, idx_buy = 0, 1
        trade_amount = (dict_flow[i, j][idx_sell][idx_item_num], dict_flow[i, j][idx_buy][idx_item_num])
        plt.text(x=(pos_2[0] * 2 + pos_1[0]) / 3, y=(pos_2[1] * 2 + pos_1[1]) / 3, s=str(trade_amount), color='green')
            
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
    
    # save picture
    path = os.path.dirname(__file__)
    path_output = os.path.join(path, "output/")
    path_trade = os.path.join(path_output, 'trade.png')
    plt.savefig(path_trade)
