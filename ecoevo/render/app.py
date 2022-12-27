import json
from typing import Optional
from ecoevo import EcoEvo
from ecoevo.config import MapConfig
from ecoevo.render.web_render import WebRender
from ecoevo.render import Dash, dash_table, html, dcc, Output, Input, State
from ecoevo.render import dash_bootstrap_components as dbc

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc_css])

web_render = WebRender(MapConfig.width, MapConfig.height)
fig = web_render.fig

env = EcoEvo(logging_level='CRITICAL')
obs, infos = env.reset()
web_render.update(env.entity_manager.map)


def column_container(components: list):
    res = html.Div([
        html.Div([component], style={
            'padding': 10,
            'flex': 1
        }) for component in components
    ],
                   style={
                       'display': 'flex',
                       'flex-direction': 'row'
                   })
    return res


reset_button = dcc.ConfirmDialogProvider(children=html.Button(
    'Reset game', className="btn btn-danger"),
                                         id='reset-danger-button',
                                         message='Reset game?')
step_button = html.Button('Step',
                          id='step-button-state',
                          className="btn btn-success")
write_button = html.Button('Write',
                           id='write-button-state',
                           className="btn btn-primary")

item_list = ['None'] + env.all_item_names
columns_name = [
    'id',
    'primary action',
    'secondary action',
    'sell offer',
    'buy offer',
]

columns = [{
    "name": i,
    "id": i,
    "deletable": False,
    "selectable": False
} for i in columns_name]

control_panel = html.Div([
    html.Div('Control Panel', className="card-header"),
    html.Label('Selected players'),
    html.Div([
        dash_table.DataTable(
            columns=columns,
            id='datatable-interactivity',
            virtualization=True,
            editable=True,
            sort_action="native",
            sort_mode="multi",
            column_selectable="single",
            row_selectable=False,
            row_deletable=True,
            selected_columns=[],
            selected_rows=[],
            style_header={
                'backgroundColor': 'rgb(30, 30, 30)',
                'color': 'white'
            },
            style_data={
                'backgroundColor': 'rgb(50, 50, 50)',
                'color': 'white'
            },
            page_action='none',
            style_table={
                'height': '300px',
                'overflowY': 'auto'
            },
        )
    ],
             className='card border-secondary mb-3',
             style={
                 'padding': 10,
                 'flex': 1
             }),
    html.Label('Main action'),
    column_container([
        dcc.Dropdown(
            [
                {
                    'label': 'Idle',
                    'value': 'idle',
                    'title': 'primary action'
                },
                {
                    'label': 'Move',
                    'value': 'move',
                    'title': 'primary action'
                },
                {
                    'label': 'Collect',
                    'value': 'collect',
                    'title': 'primary action'
                },
                {
                    'label': 'Consume',
                    'value': 'consume',
                    'title': 'primary action'
                },
            ],
            id='primary-action-state',
            value='idle',
        ),
        dcc.Dropdown([], id='secondary-action-state'),
    ]),
    html.Label('Sell offer'),
    dcc.Slider(min=0,
               max=len(item_list) - 1,
               marks={i: item_name
                      for i, item_name in enumerate(item_list)},
               value=0,
               step=1,
               id='sell-item-state'),
    html.Label('Buy offer'),
    dcc.Slider(min=0,
               max=len(item_list) - 1,
               marks={i: item_name
                      for i, item_name in enumerate(item_list)},
               value=0,
               step=1,
               id='sell-num-state'),
    write_button,
],
                         className='dbc card border-dark mb-3',
                         style={
                             'padding': 10,
                             'flex': 1
                         })

game_screen = html.Center([
    dcc.Graph(id='game-screen', figure=fig, config={'displaylogo': False}),
    html.Br(),
    html.Div(id='output-provider'),
    html.Br(),
],
                          className="dbc")

app.layout = column_container([
    html.Div(),
    html.Div([
        game_screen,
        column_container([reset_button, step_button]),
    ]),
    control_panel,
    html.Div(),
])

# @app.callback(Output('datatable-interactivity', 'style_data_conditional'),
#               Input('datatable-interactivity', 'selected_columns'))
# def update_styles(selected_columns):
#     return [{
#         'if': {
#             'column_id': i
#         },
#         'background_color': '#D2F3FF'
#     } for i in selected_columns]

default_actions = [(('idle', None), None, None) for i in range(128)]


@app.callback(
    Output('datatable-interactivity', 'data'),
    Output('write-button-state', 'n_clicks'),
    Input('game-screen', 'selectedData'),
    Input('write-button-state', 'n_clicks'),
    State('primary-action-state', 'value'),
    State('secondary-action-state', 'value'),
)
def control_panel_logic(selectedData, write_n_clicks,
                        primary_action: Optional[str],
                        secondary_action: Optional[str]):
    global default_actions
    ids = []
    selected_actions = []
    _data = json.loads(json.dumps(selectedData, indent=2))
    if _data is not None:
        _data = _data['points']
        for d in _data:
            custom_data = d['customdata']
            if custom_data[0] in web_render.player_to_emoji.keys():
                id = custom_data[1]
                ids.append(id)

        if write_n_clicks:  # 0 or 1
            # parse main action
            if primary_action: primary_action = primary_action.lower()
            if secondary_action: secondary_action = secondary_action.lower()
            action_to_write = ((primary_action, secondary_action), None, None)
            for id in ids:
                default_actions[id] = action_to_write
        # display from default_actions

        for id in ids:
            _action = default_actions[id]
            main_action, sell_offer, buy_offer = _action
            primary_action, secondary_action = main_action
            selected_actions.append({
                'id': id,
                'primary action': primary_action,
                'secondary_action': secondary_action,
                'sell offer': sell_offer,
                'buy offer': buy_offer,
            })

    return selected_actions, 0


@app.callback(
    Output('secondary-action-state', 'options'),
    Input('primary-action-state', 'value'),
)
def bind_action(primary_action):
    if primary_action == 'move':
        return [
            {
                'label': 'Up',
                'value': 'up',
                'title': 'secondary action'
            },
            {
                'label': 'Down',
                'value': 'down',
                'title': 'secondary action'
            },
            {
                'label': 'Left',
                'value': 'left',
                'title': 'secondary action'
            },
            {
                'label': 'Right',
                'value': 'right',
                'title': 'secondary action'
            },
        ]
    else:
        return []


@app.callback(
    Output('game-screen', 'figure'),
    Output('output-provider', 'children'),
    Output('reset-danger-button', 'submit_n_clicks'),
    Input('step-button-state', 'n_clicks'),
    Input('reset-danger-button', 'submit_n_clicks'),
)
def game_step(step_n_clicks, reset_n_clicks):
    reset_msg = u'Ready to play!'
    step_msg = u'Current Step {}'.format(step_n_clicks)
    if reset_n_clicks:  # 0 or 1
        obs, infos = env.reset()
        msg = reset_msg
    elif step_n_clicks:  # 0 or 1,2,3...
        # parse main action
        actions = default_actions
        obs, rewards, done, infos = env.step(actions)
        msg = step_msg if not done else u'Game Over!'
    else:
        msg = reset_msg
    web_render.update(env.entity_manager.map)
    return web_render.fig, msg, 0


if __name__ == '__main__':
    app.run_server(debug=True)
