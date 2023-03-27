from ecoevo import EcoEvo
from test_random_actions import sample_main_action
from ecoevo.config import EnvConfig
from random import randrange

class TestConfig(EnvConfig):
    total_step = 100
    num_person_type = 2

env = EcoEvo(render_mode=True, config=TestConfig, logging_level='CRITICAL')
done = False
obs, info = env.reset()
num_player = len(obs)

def sample_accept():
    return (randrange(0, num_player), 0)

for player in env.players:
    player.backpack.gold.num = 2
    player.backpack.pineapple.num = 2

while not done:
    actions1 = [(sample_main_action(), (('gold', -1), ('pineapple', 1)), sample_accept(), None) for _ in range(num_player // 2)]
    actions2 = [(sample_main_action(), (('pineapple', -1), ('gold', 1)), sample_accept(), None)
                for _ in range(num_player - num_player // 2)]
    actions = [*actions1, *actions2]
    obs, reward, done, info = env.step(actions)