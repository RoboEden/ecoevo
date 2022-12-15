from ecoevo.config import MapConfig
from ecoevo import EcoEvo
from ecoevo.render.web_render import WebRender
from dash import Dash, dcc, html, Input, Output
from dash_bootstrap_components import themes

app = Dash(__name__,external_stylesheets=[themes.DARKLY])

web_render = WebRender(MapConfig.width, MapConfig.height)
fig = web_render.fig

# Reset test
env = EcoEvo(logging_level='CRITICAL')
obs, infos = env.reset()
web_render.update(env.entity_manager.map)

app.layout = html.Div([
    dcc.Graph(id='game-screen', figure=fig),
    html.Br(),
    html.Button('Step', id='step-button-state', n_clicks=0, className="btn btn-primary"),
    html.Div(id='step-text-state'),
])


@app.callback(
              Output('step-text-state', 'children'),
              Output('game-screen', 'figure'),
              Input('step-button-state', 'n_clicks'),
              )
def step(n_clicks):
    actions = [(('move', 'right'), None, None) for i in range(128)]
    obs, rewards, done, infos = env.step(actions)
    web_render.update(env.entity_manager.map)
    text = u'Current Step {}'.format(n_clicks) if not done else u'Game Over!'
    return text, web_render.fig
    
if __name__ == '__main__':
    app.run_server(debug=True)
