from ecoevo.config import EnvConfig, MapConfig
from ecoevo import EcoEvo
from ecoevo.render.terminal_render import TerminalRender
from rich import print

if __name__ == "__main__":
    # Init test
    env = EcoEvo()
    render = TerminalRender(MapConfig.width, MapConfig.height)

    # Reset test
    obs, infos = env.reset()
    print('num_player:', env.num_player)  # 7

    # Step teset
    actions = [
        (('move', 'right'), None, None),
        (('move', 'up'), ('sand', -5), ('gold', 10)),
        (('move', 'left'), ('gold', -10), ('sand', 5)),
        (('consume', 'coral'), None, None),
        (('collect', None), None, None),
    ] * 128
    for _ in range(EnvConfig.total_step):
        obs, reward, done, infos = env.step(actions)
        render.render(env.entity_manager.map)
        # Show info
        if input('show info? y/n\n') == 'y':
            print(infos)
        if input('show obs? y/n\n') == 'y':
            print(obs)