import json
from typing import Optional
from ecoevo import EcoEvo
from ecoevo.config import MapConfig, PlayerConfig
from ecoevo.render.game_screen import GameScreen
from ecoevo.render import Dash, dash_table, html, dcc, Output, Input, State
from ecoevo.render import graph_objects as go
from ecoevo.render import dash_bootstrap_components as dbc

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc_css])
env = EcoEvo(logging_level='CRITICAL')

gs_render = GameScreen(MapConfig.width, MapConfig.height)
obs_render = GameScreen(2 * env.cfg.visual_radius + 1,
                        2 * env.cfg.visual_radius + 1)
obs, infos = env.reset()
gs_render.update(env.entity_manager.map)

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
item_to_color = {
    'gold': '#f9c23c',
    'hazelnut': '#6d4534',
    'coral': '#029ee1',
    'sand': '#f14f4c',
    'pineapple': '#86d72f',
    'peanut': '#f3ad61',
    'stone': '#9b9b9b',
    'pumpkin': '#ff8257',
}

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

info_panel = html.Div([
    html.Div('Info Panel', className="card-header"),
    html.Label('Basic info'),
    html.Div('', id='basic-provider'),
    html.Label('Backpack & Stomach'),
    html.Div('', id='backpack-stomach-provider'),
    html.Label('Persona Details'),
    html.Div('', id='preference-provider'),
    html.Label('Obs'),
    html.Div('', id='obs-provider'),
    html.Label('Reward'),
    html.Div('', id='reward-provider'),
    html.Label('Info'),
    html.Div('', id='info-provider'),
],
                      className='card border-secondary mb-3',
                      style={
                          'padding': 10,
                          'flex': 1
                      })
all_primary_action = ['idle', 'move', 'collect', 'consume']
control_panel = html.Div([
    html.Div('Control Panel', className="card-header"),
    html.Label('Selected players'),
    html.Div([
        dash_table.DataTable(
            columns=columns,
            id='datatable-interactivity',
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
                'height': 400,
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
    dbc.Row([
        dbc.Col(
            dcc.Dropdown(
                [{
                    'label': primary_action.capitalize(),
                    'value': primary_action,
                    'title': 'primary action'
                } for primary_action in all_primary_action],
                id='primary-action-state',
                value='idle',
                clearable=False,
            )),
        dbc.Col(dcc.Dropdown([], id='secondary-action-state',
                             clearable=False)),
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
    dcc.Graph(
        id='game-screen', figure=gs_render.fig, config={'displaylogo': False}),
    html.Br(),
    html.Div(id='output-provider'),
    html.Br(),
],
                          className="dbc")


def update_info(id: int):
    player = env.players[id]
    # basic
    basic = dbc.Table(
        [
            html.Thead(
                html.Tr([
                    html.Th("persona"),
                    html.Th("id"),
                    html.Th("pos"),
                    html.Th("health"),
                    html.Th("collect remain"),
                    html.Th("trade result"),
                ])),
            html.Tbody([
                html.Tr([
                    html.Td(' '.join(player.persona.split('_'))),
                    html.Td(player.id),
                    html.Td(str(player.pos)),
                    html.Td(player.health),
                    html.Td(player.collect_remain),
                    html.Td(player.trade_result),
                ])
            ])
        ],
        bordered=False,
        dark=True,
        hover=True,
        responsive=True,
        striped=True,
    )

    # plot radar
    categories = list(player.preference.keys())
    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(r=list(player.ability.values()),
                        theta=categories,
                        fill='toself',
                        name='ability'))
    fig.add_trace(
        go.Scatterpolar(r=[v * 1e2 for v in player.preference.values()],
                        theta=categories,
                        fill='toself',
                        name='preference'))
    fig.update_layout(
        width=400,
        height=300,
        font_color="white",
        paper_bgcolor="#303030",
        plot_bgcolor="#e9e9e9",
        polar=dict(radialaxis=dict(visible=False, range=[0, 10])),
        showlegend=True)

    preference = dcc.Graph(figure=fig, config={'displaylogo': False})

    def get_progress(is_backpack: bool = True):
        if is_backpack:
            where = 'backpack'
            item_list = player.backpack.dict().values()
        else:
            where = 'stomach'
            item_list = player.stomach.dict().values()
        return dbc.ListGroupItem([
            dbc.Progress([
                dbc.Progress(value=item.num * item.capacity,
                             color=item_to_color[item.name],
                             label=item.name.capitalize(),
                             id=f'{item.name}-{where}-bar',
                             max=PlayerConfig.bag_volume,
                             bar=True) for item in item_list
            ]),
            html.Div([
                dbc.Popover(
                    [
                        dbc.PopoverHeader(item.name.capitalize()),
                        dbc.PopoverBody([
                            html.Div(f'num: {item.num}'),
                            html.Div(f'capacity: {item.capacity}'),
                        ])
                    ],
                    target=f'{item.name}-{where}-bar',
                    trigger="hover",
                ) for item in item_list
            ])
        ],
                                 id=f'{where}-list-group-item')

    progress = dbc.ListGroup([
        get_progress(is_backpack=True),
        dbc.Popover([
            dbc.PopoverHeader('Backpack'),
        ],
                    target=f'backpack-list-group-item',
                    trigger="hover"),
        get_progress(is_backpack=False),
        dbc.Popover([
            dbc.PopoverHeader('Stomach'),
        ],
                    target=f'stomach-list-group-item',
                    trigger="hover"),
    ])
    # obs_render.update(obs[id])
    # local_obs = dcc.Graph(obs_render.fig)
    myreward = rewards[id]
    myinfo = html.Pre(json.dumps(info[id], indent=2))

    return basic, preference, progress, myreward, myinfo


app.layout = html.Div(
    dbc.Row([
        dbc.Col(info_panel),
        dbc.Col(dbc.Row([
            game_screen,
            dbc.Col(reset_button),
            dbc.Col(step_button),
        ]),
                width={
                    "size": "auto",
                    "order": 'first',
                }),
        dbc.Col(control_panel),
    ]))

# @app.callback(Output('datatable-interactivity', 'style_data_conditional'),
#               Input('datatable-interactivity', 'selected_columns'))
# def update_styles(selected_columns):
#     return [{
#         'if': {
#             'column_id': i
#         },
#         'background_color': '#D2F3FF'
#     } for i in selected_columns]


@app.callback(
    Output('secondary-action-state', 'options'),
    Output('secondary-action-state', 'value'),
    Input('primary-action-state', 'value'),
)
def bind_action(primary_action):
    if primary_action in ['idle', 'collect']:
        return [{
            'label': 'None',
            'value': 'none',
            'title': 'secondary action'
        }], 'none'
    elif primary_action == 'move':
        all_directions = ['up', 'down', 'left', 'right']
        return [{
            'label': direction.capitalize(),
            'value': direction,
            'title': 'secondary action'
        } for direction in all_directions], 'up'
    elif primary_action == 'consume':
        return [{
            'label': item_name.capitalize(),
            'value': item_name,
            'title': 'secondary action'
        } for item_name in env.all_item_names], env.all_item_names[0]


default_actions = [(('idle', None), None, None) for i in range(128)]
obs = [None] * env.num_player
rewards = [0.0] * env.num_player
info = [{}] * env.num_player


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
    _data = json.loads(json.dumps(selectedData))
    if _data is not None:
        _data = _data['points']
        for d in _data:
            custom_data = d['customdata']
            if custom_data[0] in gs_render.player_to_emoji.keys():
                id = custom_data[1]
                ids.append(id)

        if write_n_clicks:  # 0 or 1
            # parse main action
            if secondary_action == 'none': secondary_action = None
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
                'secondary action': secondary_action,
                'sell offer': sell_offer,
                'buy offer': buy_offer,
            })

    return selected_actions, 0


@app.callback(
    Output('basic-provider', 'children'),
    Output('preference-provider', 'children'),
    Output('backpack-stomach-provider', 'children'),
    # Output('obs-provider', 'children'),
    Output('reward-provider', 'children'),
    Output('info-provider', 'children'),
    Input('game-screen', 'clickData'),
    Input('step-button-state', 'n_clicks'),
    Input('reset-danger-button', 'submit_n_clicks'),
)
def info_panel_logic(clickData, step_n_clicks, reset_n_clicks):
    # update clickData
    if reset_n_clicks:
        return None, None, None, None, None
    id = None
    basic, preference, bac_sto_fig, myreward, myinfo = None, None, None, None, None
    _data = json.loads(json.dumps(clickData, indent=2))
    if _data is not None and len(_data['points']):
        custom_data = _data['points'][0]['customdata']
        if custom_data[0] in gs_render.player_to_emoji.keys():
            id = custom_data[1]
    if step_n_clicks and id is not None:  # update upon step or clickData change
        basic, preference, bac_sto_fig, myreward, myinfo = update_info(id)
    elif id is not None:
        basic, preference, bac_sto_fig, myreward, myinfo = update_info(id)
    return basic, preference, bac_sto_fig, myreward, myinfo


@app.callback(
    Output('game-screen', 'figure'),
    Output('output-provider', 'children'),
    Output('reset-danger-button', 'submit_n_clicks'),
    Input('step-button-state', 'n_clicks'),
    Input('reset-danger-button', 'submit_n_clicks'),
)
def game_screen_logic(step_n_clicks, reset_n_clicks):
    global obs, rewards, infos
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
    gs_render.update(env.entity_manager.map)
    return gs_render.fig, msg, 0


if __name__ == '__main__':
    app.run_server(debug=True)
