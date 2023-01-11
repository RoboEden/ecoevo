import argparse
from copy import deepcopy

from rich import print

from ecoevo import EcoEvo

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    # Init test
    env = EcoEvo(logging_level="DEBUG")

    # Reset test
    obs, infos = env.reset()
    print('num_player:', env.num_player)  # 7

    # Step teset
    actions = [(('consume', 'peanut'), ('gold', -5), ('peanut', 20))] * env.num_player
    for _ in range(env.cfg.total_step):
        obs, reward, done, infos = env.step(deepcopy(actions))
        if args.verbose:
            if input('show obs? y/n\n') == 'y':
                print(obs)
            if input('show reward? y/n\n') == 'y':
                print(reward)
            if input('show done? y/n\n') == 'y':
                print(done)
            if input('show info? y/n\n') == 'y':
                print(infos)
