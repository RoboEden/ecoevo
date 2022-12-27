import json
from typing import Optional
from ecoevo import EcoEvo
from ecoevo.config import MapConfig
from ecoevo.render.web_render import WebRender
from ecoevo.render import Dash, dash_table, html, dcc, Output, Input, State
from ecoevo.render import dash_bootstrap_components as dbc
from ecoevo.render import print

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
    'Reset game', className="btn btn-secondary"),
                                         id='reset-danger-button',
                                         message='Reset game?')
step_button = html.Button('Step',
                          id='step-button-state',
                          className="btn btn-primary")
item_list = ['None'] + env.all_item_names
control_panel = html.Div([
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
    html.Br(),
    html.Label('Sell offer'),
    dcc.Slider(min=0,
               max=len(item_list) - 1,
               marks={i: item_name
                      for i, item_name in enumerate(item_list)},
               value=0,
               step=1,
               id='sell-item-state'),
    html.Br(),
    html.Label('Buy offer'),
    html.Br(),
    dcc.Slider(min=0,
               max=len(item_list) - 1,
               marks={i: item_name
                      for i, item_name in enumerate(item_list)},
               value=0,
               step=1,
               id='sell-num-state'),
],
                         className="dbc")

game_screen = html.Center([
    dcc.Graph(id='game-screen', figure=fig, config={'displaylogo': False}),
    html.Br(),
    html.Div(id='output-provider'),
    html.Br(),
],
                          className="dbc")

selected_data = html.Div([
    dcc.Markdown("""
                **Selection Data**

                Choose the lasso or rectangle tool in the graph's menu
                bar and then select points in the graph.

                Note that if `layout.clickmode = 'event+select'`, selection data also
                accumulates (or un-accumulates) selected data if you hold down the shift
                button while clicking.
            """),
    html.Pre(id='selected-data'),
])

import pandas as pd

df = pd.read_csv(
    'https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv'
)

table = html.Div([
    dash_table.DataTable(
        id='datatable-interactivity',
        editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        column_selectable="single",
        row_selectable=False,
        row_deletable=True,
        selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current=0,
        page_size=10,
        style_header={
            'backgroundColor': 'rgb(30, 30, 30)',
            'color': 'white'
        },
        style_data={
            'backgroundColor': 'rgb(50, 50, 50)',
            'color': 'white'
        },
    ),
])

app.layout = html.Div([
    game_screen,
    control_panel,
    column_container([
        step_button,
        reset_button,
    ]),
    selected_data,
    table,
])


@app.callback(Output('datatable-interactivity', 'style_data_conditional'),
              Input('datatable-interactivity', 'selected_columns'))
def update_styles(selected_columns):
    return [{
        'if': {
            'column_id': i
        },
        'background_color': '#D2F3FF'
    } for i in selected_columns]


@app.callback(Output('datatable-interactivity', 'data'),
              Output('datatable-interactivity', 'columns'),
              Input('game-screen', 'selectedData'))
def display_selected_data(selectedData):
    columns_name = [
        'persona',
        'id',
        'pos',
        'health',
        'trade_result',
    ]

    columns = [{
        "name": i,
        "id": i,
        "deletable": False,
        "selectable": False
    } for i in columns_name]

    _data = json.dumps(selectedData, indent=2)
    _data = json.loads(_data)
    if _data is None:
        return _data, columns
    _data = _data['points']
    selected_players = []
    for d in _data:
        custom_data = d['customdata']
        if custom_data[0] in web_render.player_to_emoji.keys():
            id = custom_data[1]
            player = env.players[id]
            assert player.id == id
            player_dict = player.dict()
            del player_dict['backpack']
            del player_dict['stomach']
            del player_dict['collect_remain']
            selected_players.append(player_dict)

    df = pd.DataFrame(selected_players)
    data = df.to_dict('records')
    print(data)
    return data, columns


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
    State('primary-action-state', 'value'),
    State('secondary-action-state', 'value'),
)
def game_step(step_n_clicks, reset_n_clicks, primary_action: Optional[str],
              secondary_action: Optional[str]):
    reset_msg = u'Ready to play!'
    step_msg = u'Current Step {}'.format(step_n_clicks)
    if reset_n_clicks:  # 0 or 1
        obs, infos = env.reset()
        msg = reset_msg
    elif step_n_clicks:  # 0 or 1,2,3...
        # parse main action
        if primary_action: primary_action = primary_action.lower()
        if secondary_action: secondary_action = secondary_action.lower()
        actions = [((primary_action, secondary_action), None, None)
                   for i in range(128)]

        obs, rewards, done, infos = env.step(actions)
        msg = step_msg if not done else u'Game Over!'
    else:
        msg = reset_msg
    web_render.update(env.entity_manager.map)
    return web_render.fig, msg, 0


if __name__ == '__main__':
    app.run_server(debug=True)
