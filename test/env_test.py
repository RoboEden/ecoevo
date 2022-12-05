from ecoevo import EcoEvo
from rich import print

env = EcoEvo()
obs, infos = env.reset()
print('num_player:', env.num_player)  # 7

actions = [
    (('move', 'right'), None, None),
    (('consume', 'coral'), None, None),
    (('collect', None), None, None),
    (('move', 'up'), ('sand', -5), ('gold', 10)),
    (('consume', 'peanut'), ('gold', -5), ('peanut', 20)),
    (('move', 'left'), None, None),
    (('consume', 'peanut'), None, None),
]
env.players[1].backpack.coral.num = 1
env.players[4].backpack.gold.num = 5
obs, reward, done, infos = env.step(actions)
if input('show info? y/n\n') == 'y':
    print(infos)
if input('show obs? y/n\n') == 'y':
    print(obs)