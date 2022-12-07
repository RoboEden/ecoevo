from ecoevo.config import EnvConfig
from ecoevo import EcoEvo
from rich import print

if __name__ == "__main__":
    # Init test
    env = EcoEvo(logging_level="DEBUG")

    # Reset test
    obs, infos = env.reset()
    print('num_player:', env.num_player)  # 7

    # Step teset
    actions = [(('consume', 'peanut'), ('gold', -5),
                ('peanut', 20))] * EnvConfig.player_num
    for _ in range(EnvConfig.total_step):
        obs, reward, done, infos = env.step(actions)
        # Show info
        if input('show info? y/n\n') == 'y':
            print(infos)
        if input('show obs? y/n\n') == 'y':
            print(obs)