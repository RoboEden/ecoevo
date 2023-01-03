import json
import copy
import ecoevo.render.components as erc

from typing import Optional
from ecoevo.rollout import RollOut
from ecoevo.config import MapConfig

from ecoevo.render import Dash, Input, Output, State
from ecoevo.render import dcc, html, ctx, exceptions
from ecoevo.render import dash_bootstrap_components as dbc
from ecoevo.render.game_screen import GameScreen


class WebApp:

    def __init__(self, rollout: RollOut):
        self.rollout = rollout
        self.env = rollout.env
        self.gs_render = GameScreen(MapConfig.width, MapConfig.height)
        self.ctrl_policy = {}

        self.app = Dash(
            __name__, external_stylesheets=[dbc.themes.DARKLY, erc.dbc_css])

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
            dcc.Store(id='obs-rewards-info'),
        ])
        self.register_output_callbacks()
        self.register_input_callbacks()

    def run_server(self):
        self.app.run_server(debug=True)

    def register_output_callbacks(self):

        @self.app.callback(
            Output('secondary-action-state', 'options'),
            Output('secondary-action-state', 'value'),
            Input('primary-action-state', 'value'),
        )
        def _output_action_binding(primary_action):
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
                } for item_name in erc.all_item_list], erc.all_item_list[0]

        @self.app.callback(
            Output('datatable-interactivity', 'data'),
            Input('selected-ids', 'data'),
            Input('ctrl-next-actions', 'data'),
        )
        def _output_control_panel(
            jsonified_selected_ids,
            jsonified_next_actions,
        ):
            if jsonified_selected_ids is None or jsonified_next_actions is None:
                raise exceptions.PreventUpdate

            selected_ids = json.loads(jsonified_selected_ids)
            next_actions = json.loads(jsonified_next_actions)

            data_table = []
            for id in selected_ids:
                _action = next_actions[id]
                main_action, sell_offer, buy_offer = _action
                primary_action, secondary_action = main_action
                data_table.append({
                    'id': id,
                    'primary action': primary_action,
                    'secondary action': secondary_action,
                    'sell offer': str(sell_offer),
                    'buy offer': str(buy_offer),
                })

            return data_table

        @self.app.callback(
            Output('basic-provider', 'children'),
            Output('preference-provider', 'children'),
            Output('backpack-stomach-provider', 'children'),
            # Output('obs-provider', 'children'),
            Output('reward-provider', 'children'),
            Output('info-provider', 'children'),
            Input('selected-ids', 'data'),
        )
        def _output_info_panel(jsonified_selected_ids):
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

    def register_input_callbacks(self):

        @self.app.callback(
            Output('selected-ids', 'data'),
            Input('game-screen', 'selectedData'),
        )
        def _input_select_players(selectedData):
            _data = json.loads(json.dumps(selectedData))
            if _data is None:
                raise exceptions.PreventUpdate
            else:
                ids = []
                _data = _data['points']
                for d in _data:
                    custom_data = d['customdata']
                    if custom_data[0] in self.gs_render.player_to_emoji.keys():
                        id = custom_data[1]
                        ids.append(id)
                return json.dumps(ids)

        @self.app.callback(
            Output('game-screen', 'figure'),
            Output('output-provider', 'children'),
            Output('obs-rewards-info', 'data'),
            Output('raw-next-actions', 'data'),
            Input('step-button-state', 'n_clicks'),
            Input('reset-danger-button', 'submit_n_clicks'),
            State('ctrl-next-actions', 'data'),
        )
        def _input_game_screen(
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

        @self.app.callback(
            Output('ctrl-next-actions', 'data'),
            Input('write-button-state', 'n_clicks'),
            Input('clear-button-state', 'n_clicks'),
            Input('raw-next-actions', 'data'),
            State('selected-ids', 'data'),
            State('primary-action-state', 'value'),
            State('secondary-action-state', 'value'),
        )
        def _input_game_screen(
            write_n_clicks,
            clear_n_clicks,
            jsonified_raw_next_actions,
            jsonified_selected_ids,
            primary_action: Optional[str],
            secondary_action: Optional[str],
        ):

            if ctx.triggered_id == 'write-button-state':
                if jsonified_selected_ids is None:
                    pass
                else:
                    selected_ids = json.loads(jsonified_selected_ids)
                    if secondary_action == 'none': secondary_action = None
                    for id in selected_ids:
                        self.ctrl_policy[id] = ((primary_action,
                                                 secondary_action), None, None)
            elif ctx.triggered_id == 'clear-button-state':
                self.ctrl_policy = {}

            ctrl_next_actions = json.loads(jsonified_raw_next_actions)
            for id, action in self.ctrl_policy.items():
                ctrl_next_actions[id] = action

            return json.dumps(ctrl_next_actions)
