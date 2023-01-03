from ecoevo.entities import Player
from ecoevo.render import dash_table, html, dcc
from ecoevo.render import graph_objects as go
from ecoevo.render import dash_bootstrap_components as dbc

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
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
clear_button = html.Button('Clear',
                           id='clear-button-state',
                           className="btn btn-warning")

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
all_item_list = list(item_to_color.keys())
trade_options = ['None'] + all_item_list

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
    dcc.Slider(
        min=0,
        max=len(trade_options),
        marks={i: item_name
               for i, item_name in enumerate(trade_options)},
        value=0,
        step=1,
        id='sell-item-state'),
    html.Label('Buy offer'),
    dcc.Slider(
        min=0,
        max=len(trade_options),
        marks={i: item_name
               for i, item_name in enumerate(trade_options)},
        value=0,
        step=1,
        id='sell-num-state'),
    dbc.Row([
        dbc.Col(write_button),
        dbc.Col(clear_button),
    ])
],
                         className='dbc card border-dark mb-3',
                         style={
                             'padding': 10,
                             'flex': 1
                         })
game_screen = html.Center([
    dcc.Graph(id='game-screen', config={'displaylogo': False}),
    html.Br(),
    html.Div(id='output-provider'),
    html.Br(),
],
                          className="dbc")


def update_player_info(player: Player):
    # player = env.players[id]
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
        go.Scatterpolar(
            r=[v * 1e2 for v in player.preference.values()],
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
            items_in_bag = player.backpack.dict().values()
        else:
            where = 'stomach'
            items_in_bag = player.stomach.dict().values()
        return dbc.ListGroupItem([
            dbc.Progress([
                dbc.Progress(value=item.num * item.capacity,
                             color=item_to_color[item.name],
                             label=item.name.capitalize(),
                             id=f'{item.name}-{where}-bar',
                             bar=True) for item in items_in_bag
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
                ) for item in items_in_bag
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
    myreward = None  #rewards[id]
    myinfo = None  #html.Pre(json.dumps(info[id], indent=2))

    return basic, preference, progress, myreward, myinfo