from ecoevo.config import EnvConfig, MapSize
from ecoevo import EcoEvo
from ecoevo.render.terminal_render import TerminalRender
from rich import print

if __name__ == "__main__":
    # Init test
    env = EcoEvo()
    render = TerminalRender(MapSize.width, MapSize.height)

    # Reset test
    obs, infos = env.reset()
    print('num_player:', env.num_player)  # 7

    # Step teset
    actions = [(('move', 'right'), None, None)] * len(EnvConfig.personae)
    for _ in range(EnvConfig.total_step):
        obs, reward, done, infos = env.step(actions)
        render.render(env.map)
        # Show info
        if input('show info? y/n\n') == 'y':
            print(infos)
        if input('show obs? y/n\n') == 'y':
            print(obs)