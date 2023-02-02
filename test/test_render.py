import random
from ecoevo import EcoEvo

env = EcoEvo(render_mode=True)
obs, info = env.reset()
i = 0
print('Reset!', i, info['curr_step'])
print(info)
done = False
while not done:
    actions = [(random.choice([
        ('idle', None),
        ('move', 'up'),
        ('move', 'down'),
        ('move', 'left'),
        ('move', 'right'),
    ]), None, None) for i in range(len(obs))]
    obs, rewards, done, info = env.step(actions)
    i += 1
    print(i, info['curr_step'])
    print(info)