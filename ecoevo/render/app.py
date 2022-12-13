import streamlit as st

from ecoevo.config import EnvConfig, MapSize
from ecoevo import EcoEvo
from ecoevo.render.web_render import WebRender

st.set_page_config(layout='wide')
# Init test
env = EcoEvo()
render = WebRender(MapSize.width, MapSize.height)

# Reset test
wr = WebRender(MapSize.width, MapSize.height)
obs, infos = env.reset()

done = False
while not done:
    wr.render(env.map)
    actions = [(('move', 'right'), None, None) for i in range(128)]
    # actions = my_policy(obs, infos) # your policy goes here
    obs, rewards, done, infos = env.step(actions)
    input()

if False:
    # Step teset
    actions = [
        (('move', 'right'), None, None),
        (('move', 'up'), ('sand', -5), ('gold', 10)),
        (('move', 'left'), ('gold', -10), ('sand', 5)),
        (('consume', 'coral'), None, None),
        (('collect', None), None, None),
    ] * 20
    for _ in range(EnvConfig.total_step):
        obs, reward, done, infos = env.step(actions)
        render.render(env.map)
        # Show info
        if input('show info? y/n\n') == 'y':
            print(infos)
        if input('show obs? y/n\n') == 'y':
            print(obs)
