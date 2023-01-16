from ecoevo.render import dash_table, html, dcc, dbc, daq

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
plotlyjs = "https://cdn.plot.ly/plotly-2.12.1.min.js"
chartjs = "https://cdn.jsdelivr.net/npm/chart.js"

reset_button = dcc.ConfirmDialogProvider(children=html.Button('Reset game', className="btn btn-danger"),
                                         id='reset-danger-button',
                                         message='Reset game?')
step_button = html.Button('Step', id='step-button-state', className="btn btn-success")
write_button = html.Button('Write', id='write-button-state', className="btn btn-primary")
clear_button = html.Button('Clear', id='clear-button-state', className="btn btn-warning")

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

columns = [{"name": i, "id": i, "deletable": False, "selectable": False} for i in columns_name]

info_panel = html.Div([
    html.Div('Info Panel', className="card-header"),
    html.Label('Basic info'),
    html.Div(dbc.Table(
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
                    html.Td("null", id='basic-player-persona'),
                    html.Td("null", id='basic-player-id'),
                    html.Td("null", id='basic-player-pos'),
                    html.Td("null", id='basic-player-health'),
                    html.Td("null", id='basic-player-collect-remain'),
                    html.Td("null", id='basic-player-trade-result'),
                ])
            ])
        ],
        bordered=False,
        dark=True,
        hover=True,
        responsive=True,
        striped=True,
    ),
             id='basic-provider'),
    html.Label('Backpack & Stomach'),
    dbc.ListGroup([
        dbc.ListGroupItem(dbc.Progress([
            dbc.Progress(value=0, label=item_name.capitalize(), id=f'backpack-{item_name}-bar', bar=True)
            for item_name in all_item_list
        ]),
                          id='backpack-list-group-item'),
        dbc.Popover('Backpack', target='backpack-list-group-item', trigger='hover'),
        dbc.ListGroupItem(dbc.Progress([
            dbc.Progress(value=0, label=item_name.capitalize(), id=f'stomach-{item_name}-bar', bar=True)
            for item_name in all_item_list
        ]),
                          id='stomach-list-group-item'),
        dbc.Popover('Stomach', target='stomach-list-group-item', trigger='hover'),
    ]),
    html.Label('Last Action'),
    html.Div(
        dbc.Table(
            [
                html.Thead(
                    html.Tr([
                        html.Th("primary action"),
                        html.Th("secondary action"),
                        html.Th("sell offer"),
                        html.Th("buy offer"),
                    ])),
                html.Tbody([
                    html.Tr([
                        html.Td("null", id='primary-action-provider'),
                        html.Td("null", id='secondary-action-provider'),
                        html.Td("null", id='sell-offer-provider'),
                        html.Td("null", id='buy-offer-provider'),
                    ])
                ])
            ],
            bordered=False,
            dark=True,
            hover=True,
            responsive=True,
            striped=True,
        )),
    html.Label('Persona Details'),
    html.Div(html.Canvas(id='radar-chart'), style={
        'width': '300px',
        "padding": "25px",
        "boxSizing": "border-box"
    }),
    html.Label('Reward'),
    html.Div('NaN', id='reward-provider'),
    html.Label('Info'),
    html.Pre('', id='info-provider'),
],
                      className='card border-secondary mb-3',
                      style={
                          'padding': 10,
                          'flex': 1
                      })
all_primary_action = ['idle', 'move', 'collect', 'consume']
control_panel = html.Div([
    html.Div('Control Panel', className="card-header"),
    html.Label('Next Actions'),
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
        dbc.Col(dcc.Dropdown([], id='secondary-action-state', clearable=False)),
    ]),
    html.Label('Sell offer'),
    dcc.RadioItems(trade_options, 'None', id='sell-item-state', inline=True),
    daq.NumericInput(
        id='sell-num-state',
        value=0,
        min=0,
        max=1000,
    ),
    html.Label('Buy offer'),
    dcc.RadioItems(trade_options, 'None', id='buy-item-state', inline=True),
    daq.NumericInput(
        id='buy-num-state',
        value=0,
        min=0,
        max=1000,
    ),
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