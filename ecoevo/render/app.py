from typing import Optional
from ecoevo import EcoEvo
from ecoevo.config import MapConfig
from ecoevo.render.web_render import WebRender
from ecoevo.render import Dash, html, dcc, dbc, Output, Input, State


dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = Dash(__name__,external_stylesheets=[dbc.themes.DARKLY, dbc_css])

web_render = WebRender(MapConfig.width, MapConfig.height)
fig = web_render.fig

env = EcoEvo(logging_level='CRITICAL')
obs, infos = env.reset()
web_render.update(env.entity_manager.map)

def column_container(components:list):
    res =  html.Div([
        html.Div([component], style={'padding': 10, 'flex': 1}) for component in components
        ], style={'display': 'flex', 'flex-direction': 'row'})
    return res

reset_button = dcc.ConfirmDialogProvider(
        children=html.Button('Reset game', className="btn btn-secondary"),
        id='reset-danger-button',
        message='Reset game?'
    )
step_button = html.Button('Step', id='step-button-state', className="btn btn-primary")
item_list = ['None'] + env.all_item_names
control_panel = html.Div([
        html.Label('Main action'),
        column_container([
            dcc.Dropdown([
                {'label':'Idle', 'value':'idle', 'title':'primary action'},
                {'label':'Move', 'value':'move', 'title':'primary action'},
                {'label':'Collect', 'value':'collect', 'title':'primary action'},
                {'label':'Consume', 'value':'consume', 'title':'primary action'},
                ], 
            id='primary-action-state',
            value='idle',
            ),
            dcc.Dropdown([], id='secondary-action-state'),
        ]),
        html.Br(),
        html.Label('Sell offer'),
        dcc.Slider(min=0, 
            max=len(item_list)-1,
            marks={i: item_name for i, item_name in enumerate(item_list)},
            value=0,
            step=1,
            id='sell-item-state'
        ),
        html.Br(),
        html.Label('Buy offer'),
        html.Br(),
        dcc.Slider(
            min=0,
            max=len(item_list)-1,
            marks={i: item_name for i, item_name in enumerate(item_list)},
            value=0,
            step=1,
            id='sell-num-state'
        ),
    ], style={'padding': 10, 'flex': 1}, className="dbc")


game_screen = html.Center([
        dcc.Graph(id='game-screen', figure=fig, config={'displaylogo': False}),
        html.Br(),
        html.Div(id='output-provider'),
        html.Br(),
    ], style={'padding': 10, 'flex': 1}, className="dbc")
app.layout = html.Div([
    game_screen, 
    control_panel,
    column_container([
        step_button,
        reset_button,
    ]),
    ])

@app.callback(Output('secondary-action-state', 'options'),
              Input('primary-action-state', 'value'),)
def bind_action(primary_action):
    if primary_action == 'move':
        return [
                {'label':'Up', 'value':'up', 'title':'secondary action'},
                {'label':'Down', 'value':'down', 'title':'secondary action'},
                {'label':'Left', 'value':'left', 'title':'secondary action'},
                {'label':'Right', 'value':'right', 'title':'secondary action'},
                ]
    else:
        return []


@app.callback(Output('game-screen', 'figure'),
              Output('output-provider', 'children'),
              Output('reset-danger-button', 'submit_n_clicks'),
              Input('step-button-state', 'n_clicks'),
              Input('reset-danger-button', 'submit_n_clicks'),
              State('primary-action-state', 'value'),
              State('secondary-action-state', 'value'),
              )
def game_step(step_n_clicks, reset_n_clicks, primary_action:Optional[str], secondary_action:Optional[str]):
    reset_msg = u'Ready to play!'
    step_msg = u'Current Step {}'.format(step_n_clicks)
    if reset_n_clicks: # 0 or 1
        obs, infos = env.reset()
        msg = reset_msg
    elif step_n_clicks: # 0 or 1,2,3...
        # parse main action
        if primary_action: primary_action = primary_action.lower()
        if secondary_action: secondary_action = secondary_action.lower()
        actions = [((primary_action, secondary_action), None, None) for i in range(128)]

        obs, rewards, done, infos = env.step(actions)
        msg = step_msg if not done else u'Game Over!'
    else:
        msg = reset_msg
    web_render.update(env.entity_manager.map)
    return web_render.fig, msg, 0
    
if __name__ == '__main__':
    app.run_server(debug=True)
