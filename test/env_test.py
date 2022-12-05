from ecoevo import EcoEvo
from rich import print

env = EcoEvo()
obs, infos = env.reset()
print(env.num_player)
action = (('move', 'up'), ('sand', -5), ('gold', 10))
actions = [action] * env.num_player
obs, reward, infos, done = env.step(actions)
print(infos)
print(obs)