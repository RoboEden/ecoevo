from ecoevo.config import MapConfig
from ecoevo import EcoEvo
from ecoevo.render.web_render import WebRender
try:
    from dash import Dash, dcc, html, Input, Output
    from dash_bootstrap_components import themes
except:
    raise ImportError("Try pip install ecoevo[render]!")

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = Dash(__name__,external_stylesheets=[themes.DARKLY, dbc_css])

web_render = WebRender(MapConfig.width, MapConfig.height)
fig = web_render.fig

env = EcoEvo(logging_level='CRITICAL')
obs, infos = env.reset()
web_render.update(env.entity_manager.map)


control_panel = html.Div([
    html.Div(children=[
        html.Label('Main action'),
        dcc.RadioItems(['Idle', 'Move', 'Collect', 'Consume'], 'Idle'),
        html.Br(),
        html.Label('Sell offer'),
        dcc.Dropdown(env.all_item_names, env.all_item_names[0]),
        html.Br(),
        html.Label('Buy offer'),
        dcc.Dropdown(env.all_item_names, env.all_item_names[0]),
    ], style={'padding': 100, 'flex': 1}, className="dbc"),

    html.Div(children=[
        html.Label('Checkboxes'),
        dcc.Checklist(['New York City', 'Montréal', 'San Francisco'],
                      ['Montréal', 'San Francisco']
        ),

        html.Br(),
        html.Label('Text Input'),
        dcc.Input(value='MTL', type='text'),

        html.Br(),
        html.Label('Slider'),
        dcc.Slider(
            min=0,
            max=env.curr_step,
            marks={i: f'Label {i}' if i == 1 else str(i) for i in range(1, 6)},
            value=5,
        ),
    ], style={'padding': 10, 'flex': 1})
], style={'display': 'flex', 'flex-direction': 'row'})

game_screen = html.Center([
        dcc.Graph(id='game-screen', figure=fig, config={'displaylogo': False}),
        html.Br(),
        html.Div(id='output-provider'),
        html.Br(),
        html.Button('Step', id='step-button-state', className="btn btn-primary")
    ])

reset_button = dcc.ConfirmDialogProvider(
        children=html.Button('Restart', className="btn btn-secondary"),
        id='reset-danger-button',
        message='Restart game?'
    )


app.layout = html.Div([
    html.Div([    
        html.Div([game_screen],className='col'),
        html.Div([
            control_panel,
            reset_button,
        ],className='col'),
    ], className='row align-items-start'),
], className='container')


@app.callback(Output('game-screen', 'figure'),
              Output('output-provider', 'children'),
              Output('reset-danger-button', 'submit_n_clicks'),
              Input('step-button-state', 'n_clicks'),
              Input('reset-danger-button', 'submit_n_clicks')
              )
def game_step(n_clicks, submit_n_clicks):
    reset_msg = u'Ready to play!'
    step_msg = u'Current Step {}'.format(n_clicks)
    if submit_n_clicks:
        obs, infos = env.reset()
        web_render.update(env.entity_manager.map)
        msg = reset_msg
    else:
        actions = [(('move', 'right'), None, None) for i in range(128)]
        obs, rewards, done, infos = env.step(actions)
        if done:
            msg = u'Game Over!'
        else:
            msg = step_msg if n_clicks else reset_msg
    web_render.update(env.entity_manager.map)
    return web_render.fig, msg, 0
    
if __name__ == '__main__':
    app.run_server(debug=True)
