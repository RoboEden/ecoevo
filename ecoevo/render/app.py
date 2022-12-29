import json
import ecoevo.render.components as erc
from ecoevo import EcoEvo
from typing import Optional
from ecoevo.config import MapConfig
from ecoevo.render.game_screen import GameScreen
from ecoevo.render import Dash, html, Output, Input, State
from ecoevo.render import dash_bootstrap_components as dbc


class WebApp:

    def __init__(self, env: EcoEvo):
        self.env = env
        self.env.reset()
        self.gs_render = GameScreen(MapConfig.width, MapConfig.height)
        self.gs_render.update(self.env.entity_manager.map)

        self.current_actions = [(('idle', None), None, None)
                                for i in range(self.env.num_player)]

        dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"

        self.app = Dash(__name__,
                        external_stylesheets=[dbc.themes.DARKLY, dbc_css])

        self.app.layout = html.Div(
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
            ]))
        self.app.callback(
            Output('secondary-action-state', 'options'),
            Output('secondary-action-state', 'value'),
            Input('primary-action-state', 'value'),
        )(self._callback_bind_action)

        self.app.callback(
            Output('datatable-interactivity', 'data'),
            Output('write-button-state', 'n_clicks'),
            Input('game-screen', 'selectedData'),
            Input('write-button-state', 'n_clicks'),
            State('primary-action-state', 'value'),
            State('secondary-action-state', 'value'),
        )(self._callback_control_panel)

        self.app.callback(
            Output('basic-provider', 'children'),
            Output('preference-provider', 'children'),
            Output('backpack-stomach-provider', 'children'),
            # Output('obs-provider', 'children'),
            Output('reward-provider', 'children'),
            Output('info-provider', 'children'),
            Input('game-screen', 'clickData'),
            Input('step-button-state', 'n_clicks'),
            Input('reset-danger-button', 'submit_n_clicks'),
        )(self._callback_info_panel)
        self.app.callback(
            Output('game-screen', 'figure'),
            Output('output-provider', 'children'),
            Output('reset-danger-button', 'submit_n_clicks'),
            Input('step-button-state', 'n_clicks'),
            Input('reset-danger-button', 'submit_n_clicks'),
        )(self._callback_game_screen)

    def run_server(self):
        self.app.run_server(debug=True)

    def _callback_bind_action(self, primary_action):
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

    def _callback_control_panel(self, selectedData, write_n_clicks,
                                primary_action: Optional[str],
                                secondary_action: Optional[str]):
        ids = []
        selected_actions = []
        _data = json.loads(json.dumps(selectedData))
        if _data is not None:
            _data = _data['points']
            for d in _data:
                custom_data = d['customdata']
                if custom_data[0] in self.gs_render.player_to_emoji.keys():
                    id = custom_data[1]
                    ids.append(id)

            if write_n_clicks:  # 0 or 1
                # parse main action
                if secondary_action == 'none': secondary_action = None
                action_to_write = ((primary_action, secondary_action), None,
                                   None)
                for id in ids:
                    self.current_actions[id] = action_to_write
            # display from self.current_actions

            for id in ids:
                _action = self.current_actions[id]
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

    def _callback_info_panel(self, clickData, step_n_clicks, reset_n_clicks):
        # update clickData
        if reset_n_clicks:
            return None, None, None, None, None
        player = None
        basic, preference, bac_sto_fig, myreward, myinfo = None, None, None, None, None
        _data = json.loads(json.dumps(clickData, indent=2))
        if _data is not None and len(_data['points']):
            custom_data = _data['points'][0]['customdata']
            if custom_data[0] in self.gs_render.player_to_emoji.keys():
                id = custom_data[1]
                player = self.env.players[id]
        if step_n_clicks and player is not None:  # update upon step or clickData change
            basic, preference, bac_sto_fig, myreward, myinfo = erc.update_player_info(
                player)
        elif player is not None:
            basic, preference, bac_sto_fig, myreward, myinfo = erc.update_player_info(
                player)
        return basic, preference, bac_sto_fig, myreward, myinfo

    def _callback_game_screen(self, step_n_clicks, reset_n_clicks):
        global obs, rewards, infos
        reset_msg = u'Ready to play!'
        step_msg = u'Current Step {}'.format(step_n_clicks)
        if reset_n_clicks:  # 0 or 1
            obs, infos = self.env.reset()
            msg = reset_msg
        elif step_n_clicks:  # 0 or 1,2,3...
            # parse main action
            self.current_actions = self.env.get_actions()
            obs, rewards, done, infos = self.env.step(self.current_actions)
            msg = step_msg if not done else u'Game Over!'
        else:
            msg = reset_msg
        self.gs_render.update(self.env.entity_manager.map)
        return self.gs_render.fig, msg, 0