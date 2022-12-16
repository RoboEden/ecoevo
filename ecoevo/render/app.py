from ecoevo import EcoEvo
from ecoevo.config import MapConfig
from ecoevo.render.web_render import WebRender
from ecoevo.render import Dash, html, dcc, dbc, Output, Input


dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = Dash(__name__,external_stylesheets=[dbc.themes.DARKLY, dbc_css])

web_render = WebRender(MapConfig.width, MapConfig.height)
fig = web_render.fig

env = EcoEvo(logging_level='CRITICAL')
obs, infos = env.reset()
web_render.update(env.entity_manager.map)


control_panel = html.Div([
    html.Div(children=[
        html.Label('Main action'),
        dcc.Dropdown(['Idle', 'Move', 'Collect', 'Consume'], 'Idle'),
        html.Br(),
        html.Label('Sell offer'),
        dcc.Slider(
            min=0,
            max=len(env.all_item_names),
            marks={i: item_name for i, item_name in enumerate(env.all_item_names)},
            value=3,
            step=1,
        ),
        html.Br(),
        html.Label('Buy offer'),
        html.Br(),
        dcc.Slider(
            min=0,
            max=len(env.all_item_names),
            marks={i: item_name for i, item_name in enumerate(env.all_item_names)},
            value=3,
            step=1,
        )
    ], style={'padding': 10, 'flex': 1}, className="dbc"),

    # html.Div(children=[
    #     html.Label('Checkboxes'),
    #     dcc.Checklist(['New York City', 'Montréal', 'San Francisco'],
    #                   ['Montréal', 'San Francisco']
    #     ),

    #     html.Br(),
    #     html.Label('Text Input'),
    #     dcc.Input(value='MTL', type='text'),
    # ], style={'padding': 10, 'flex': 1})
], style={'display': 'flex', 'flex-direction': 'row'})

game_screen = html.Center([
        dcc.Graph(id='game-screen', figure=fig, config={'displaylogo': False}),
        html.Br(),
        html.Div(id='output-provider'),
        html.Br(),
        html.Button('Step', id='step-button-state', className="btn btn-primary")
    ])

reset_button = dcc.ConfirmDialogProvider(
        children=html.Button('Reset game', className="btn btn-secondary"),
        id='reset-danger-button',
        message='Reset game?'
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
