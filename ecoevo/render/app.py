import json
import ecoevo.render.components as erc

from ecoevo.rollout import RollOut
from ecoevo.config import MapConfig
from ecoevo.entities import ALL_ITEM_DATA, ALL_PERSONAE

from ecoevo.render import Dash, Input, Output, State, ClientsideFunction
from ecoevo.render import dcc, dbc, html, ctx
from ecoevo.render.game_screen import GameScreen


class WebApp:

    def __init__(self, rollout: RollOut):
        self.rollout = rollout
        self.env = rollout.env
        self.gs_render = GameScreen(MapConfig.width, MapConfig.height)
        self.ctrl_policy = {}
        self.app = Dash(
            __name__,
            external_scripts=[erc.plotlyjs, erc.chartjs],
            external_stylesheets=[dbc.themes.DARKLY, erc.dbc_css],
        )
        self.app.layout = html.Div([
            dbc.Row([
                dbc.Col(erc.info_panel),
                dbc.Col(dbc.Row([
                    erc.game_screen,
                    dbc.Col(erc.reset_button),
                    dbc.Col(erc.step_button),
                ])),
                dbc.Col(erc.control_panel),
            ]),
            dcc.Store(id='selected-ids'),
            dcc.Store(id='raw-next-actions'),
            dcc.Store(id='ctrl-next-actions'),
            dcc.Store(id='written-actions'),
            dcc.Store(id='env-output-data'),
            dcc.Store(id='curr-step'),
            dcc.Store(id='all-item-data', data=json.dumps(ALL_ITEM_DATA)),
            dcc.Store(id='all-persona', data=json.dumps(ALL_PERSONAE)),
        ])

    def run_server(self):
        self.app.clientside_callback(
            ClientsideFunction('clientside', 'actionBinding'),
            Output('secondary-action-state', 'options'),
            Output('secondary-action-state', 'value'),
            Input('primary-action-state', 'value'),
            State('all-item-data', 'data'),
        )
        self.app.clientside_callback(
            ClientsideFunction('clientside', 'updateSelectedIds'),
            Output('selected-ids', 'data'),
            Input('game-screen', 'selectedData'),
            State('all-persona', 'data'),
        )
        self.app.clientside_callback(
            ClientsideFunction('clientside', 'displaySelectedActions'),
            Output('datatable-interactivity', 'data'),
            Input('selected-ids', 'data'),
            Input('ctrl-next-actions', 'data'),
        )
        self.app.clientside_callback(
            ClientsideFunction('clientside', 'displaySelectedPlayer'),
            Output('info-provider', 'children'),
            Input('selected-ids', 'data'),
            Input('env-output-data', 'data'),
            State('all-item-data', 'data'),
            State('all-persona', 'data'),
        )
        self.app.clientside_callback(
            ClientsideFunction('clientside', 'controlActions'),
            Output('ctrl-next-actions', 'data'),
            Output('written-actions', 'data'),
            Input('write-button-state', 'n_clicks'),
            Input('clear-button-state', 'n_clicks'),
            Input('raw-next-actions', 'data'),
            Input('selected-ids', 'data'),
            State('written-actions', 'data'),
            State('primary-action-state', 'value'),
            State('secondary-action-state', 'value'),
            State('sell-item-state', 'value'),
            State('sell-num-state', 'value'),
            State('buy-item-state', 'value'),
            State('buy-num-state', 'value'),
        )

        @self.app.callback(
            Output('game-screen', 'figure'),
            Output('output-provider', 'children'),
            Output('env-output-data', 'data'),
            Output('raw-next-actions', 'data'),
            Input('step-button-state', 'n_clicks'),
            Input('reset-danger-button', 'submit_n_clicks'),
            State('ctrl-next-actions', 'data'),
        )
        def serverside_callback(
            step_n_clicks,
            reset_n_clicks,
            jsonified_ctrl_next_actions,
        ):
            if ctx.triggered_id == 'step-button-state':
                ctrl_next_actions = json.loads(jsonified_ctrl_next_actions)
                obs, rewards, done, info = self.env.step(ctrl_next_actions)
                if done:
                    msg = u'Game Over!'
                else:
                    msg = u'Current Step {}'.format(self.env.curr_step)
            else:
                obs, info = self.env.reset()
                rewards = [0.0] * self.env.num_player
                msg = u'Ready to play!'

            # costy
            self.gs_render.update(
                self.env.entity_manager.map,
                self.env.trader.dict_flow,
                self.env.players,
            )
            if 'transaction_graph' in info:
                info.pop['transaction_graph']
            env_output_data = {
                'obs': None,
                'rewards': rewards,
                'info': info,
                'players': [player.json() for player in self.env.players]
            }
            raw_next_actions = self.rollout.get_actions()
            return self.gs_render.fig, msg, json.dumps(env_output_data), json.dumps(raw_next_actions)

        self.app.run_server(debug=True)
