import json
import copy
import ecoevo.render.components as erc

from typing import Optional
from ecoevo.rollout import RollOut
from ecoevo.config import MapConfig

from ecoevo.render import Dash, Input, Output, State, ClientsideFunction
from ecoevo.render import dcc, html, ctx, exceptions
from ecoevo.render import dash_bootstrap_components as dbc
from ecoevo.render.game_screen import GameScreen


class WebApp:

    def __init__(self, rollout: RollOut):
        self.rollout = rollout
        self.env = rollout.env
        self.gs_render = GameScreen(MapConfig.width, MapConfig.height)
        self.ctrl_policy = {}

        self.app = Dash(__name__,
                        external_stylesheets=[dbc.themes.DARKLY, erc.dbc_css])

        self.app.layout = html.Div([
            dbc.Row([
                dbc.Col(erc.info_panel),
                dbc.Col(dbc.Row([
                    erc.game_screen,
                    dbc.Col(erc.reset_button),
                    dbc.Col(erc.step_button),
                ]),
                        width={
                            "size": "auto",
                            "order": 'first',
                        }),
                dbc.Col(erc.control_panel),
            ]),
            dcc.Store(id='selected-ids'),
            dcc.Store(id='raw-next-actions'),
            dcc.Store(id='ctrl-next-actions'),
            dcc.Store(id='written-actions'),
            dcc.Store(id='obs-rewards-info'),
        ])
        self.app.clientside_callback(
            ClientsideFunction('clientside', 'actionBinding'),
            Output('secondary-action-state', 'options'),
            Output('secondary-action-state', 'value'),
            Input('primary-action-state', 'value'),
        )
        self.app.clientside_callback(
            ClientsideFunction('clientside', 'selectedPlayerActions'),
            Output('datatable-interactivity', 'data'),
            Input('selected-ids', 'data'), Input('ctrl-next-actions', 'data'))
        self.app.clientside_callback(
            ClientsideFunction('clientside', 'updateSelectedIds'),
            Output('selected-ids', 'data'),
            Input('game-screen', 'selectedData'),
        )
        self.app.clientside_callback(
            ClientsideFunction('clientside', 'controlActions'),
            Output('ctrl-next-actions', 'data'),
            Output('written-actions', 'data'),
            Input('write-button-state', 'n_clicks'),
            Input('clear-button-state', 'n_clicks'),
            Input('raw-next-actions', 'data'),
            State('selected-ids', 'data'),
            State('primary-action-state', 'value'),
            State('secondary-action-state', 'value'),
            State('written-actions', 'data'),
        )

        self.register_serverside_callbacks()

    def run_server(self):
        self.app.run_server(debug=True)

    def register_serverside_callbacks(self):

        @self.app.callback(
            Output('basic-provider', 'children'),
            Output('preference-provider', 'children'),
            Output('backpack-stomach-provider', 'children'),
            # Output('obs-provider', 'children'),
            Output('reward-provider', 'children'),
            Output('info-provider', 'children'),
            Input('selected-ids', 'data'),
        )
        def _callback_info_panel(jsonified_selected_ids):
            if jsonified_selected_ids is None:
                raise exceptions.PreventUpdate
            selected_ids = json.loads(jsonified_selected_ids)
            # update clickData
            basic, preference, bac_sto_fig, myreward, myinfo = None, None, None, None, None
            if len(selected_ids):
                id = selected_ids[0]
                player = self.env.players[id]
                basic, preference, bac_sto_fig, myreward, myinfo = erc.update_player_info(
                    player)
            return basic, preference, bac_sto_fig, myreward, myinfo

        @self.app.callback(
            Output('game-screen', 'figure'),
            Output('output-provider', 'children'),
            Output('obs-rewards-info', 'data'),
            Output('raw-next-actions', 'data'),
            Input('step-button-state', 'n_clicks'),
            Input('reset-danger-button', 'submit_n_clicks'),
            State('ctrl-next-actions', 'data'),
        )
        def _callback_game_screen(
            step_n_clicks,
            reset_n_clicks,
            jsonified_ctrl_next_actions,
        ):
            msg = u'Ready to play!'
            obs_rewards_info = {
                'obs': None,
                'rewards': [0.0] * self.env.num_player,
                'info': {}
            }

            if ctx.triggered_id in ['reset-danger-button', None]:
                obs, info = self.env.reset()
                raw_next_actions = self.rollout.get_actions()

            elif ctx.triggered_id == 'step-button-state':  # 0 or 1,2,3...
                ctrl_next_actions = json.loads(jsonified_ctrl_next_actions)
                obs, rewards, done, info = self.env.step(ctrl_next_actions)

                msg = u'Current Step {}'.format(
                    self.env.curr_step) if not done else u'Game Over!'
                raw_next_actions = self.rollout.get_actions()
                obs_rewards_info = {
                    'obs': None,
                    'rewards': rewards,
                    'info': info
                }

            self.gs_render.update(self.env.entity_manager.map)
            return self.gs_render.fig, msg, json.dumps(
                obs_rewards_info), json.dumps(raw_next_actions)