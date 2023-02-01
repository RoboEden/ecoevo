import matplotlib.pyplot as plt
import numpy as np

from ecoevo.entities.items import ALL_ITEM_DATA
from ecoevo.reward import cal_utility_log

MAX_VOLUME = 1000


def utility(item: str, volumn: float) -> float:
    volumes = {key: 0 for key in ALL_ITEM_DATA.keys()}
    volumes[item] = volumn
    u, _ = cal_utility_log(volumes, coef_disposable=3, coef_luxury=3, den=10)
    return u


def us(item, xs):
    return [utility(item, x) for x in xs]


# fig = plt.figure(figsize=(18, 6), dpi=800)
fig = plt.figure(figsize=(30, 30), dpi=100)

xs = np.linspace(0, MAX_VOLUME, 100)

for i, main_item in enumerate(ALL_ITEM_DATA.keys()):
    plt.subplot(3, 3, i + 1)
    plt.title(main_item)
    for item in ALL_ITEM_DATA.keys():
        plt.plot(xs, us(item, xs), '--', color='gray')
    plt.plot(xs, us(main_item, xs), color='red', label=item)

plt.savefig('reward_plot.png', dpi=100)
