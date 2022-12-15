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
    html.Center([
        dcc.Graph(id='game-screen', figure=fig),
        html.Br(),
        html.Div(id='output-provider'),
        html.Br(),
        html.Button('Step', id='step-button-state', className="btn btn-primary")
    ]),
    dcc.ConfirmDialogProvider(
        children=html.Button('Reset', className="btn btn-secondary"),
        id='reset-danger-provider',
        message='Are you sure you want to reset?')
    ])



@app.callback(Output('game-screen', 'figure'),
              Output('output-provider', 'children'),
              Output('reset-danger-provider', 'submit_n_clicks'),
              Input('step-button-state', 'n_clicks'),
              Input('reset-danger-provider', 'submit_n_clicks')
              )
def game_step(n_clicks, submit_n_clicks):
    if submit_n_clicks:
        obs, infos = env.reset()
        web_render.update(env.entity_manager.map)
        text = u'Game Reset!'
    else:
        actions = [(('move', 'right'), None, None) for i in range(128)]
        obs, rewards, done, infos = env.step(actions)
        text = u'Current Step {}'.format(n_clicks) if not done else u'Game Over!'
    web_render.update(env.entity_manager.map)
    return web_render.fig, text, 0
    
if __name__ == '__main__':
    app.run_server(debug=True)
