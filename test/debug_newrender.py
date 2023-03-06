from ecoevo import EcoEvo
from test_random_actions import sample_main_action
from ecoevo.config import EnvConfig


class TestConfig(EnvConfig):
    total_step = 100


env = EcoEvo(render_mode=True, config=TestConfig)
done = False
obs, info = env.reset()
num_player = len(obs)
while not done:
    actions1 = [(sample_main_action(), ('gold', -1), ('pineapple', 1)) for _ in range(num_player // 2)]
    actions2 = [(sample_main_action(), ('pineapple', -1), ('gold', 1)) for _ in range(num_player - num_player // 2)]
    actions = [*actions1, *actions2]
    obs, reward, done, info = env.step(actions)