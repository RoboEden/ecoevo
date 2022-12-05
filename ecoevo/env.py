import random
import numpy as np
from typing import List, Tuple
from rich import print

from ecoevo.config import EnvConfig, MapSize
from ecoevo.entities.player import Player, Action, Direction
from ecoevo.maps import MapGenerator
from ecoevo.trader import Trader
from ecoevo.reward import RewardParser


class EcoEvo:

    def __init__(self, render_mode=None):
        self.render_mode = render_mode
        self.map_generator = MapGenerator()
        self.trader = Trader(EnvConfig.trade_radius)
        self.reward_parser = RewardParser()
        self.players: List[Player] = []

    @property
    def num_player(self):
        return len(self.players)

    def reset(self, seed=None):
        self.players = []
        self.curr_step = 0
        self.map = self.map_generator.gen_map()

        # Add player
        player_pos = np.random.choice(MapSize.width * MapSize.height,
                                      size=EnvConfig.player_num,
                                      replace=False)

        for id, persona in enumerate(EnvConfig.personae):
            player = Player(persona, id)
            x = player_pos[id] // MapSize.width
            y = player_pos[id] // MapSize.height
            player.pos = (x, y)
            self.players.append(player)

            # Allocate player
            if player.pos not in self.map:
                self.map[player.pos] = {'player': player}
            else:
                self.map[player.pos]['player'] = player
                player.item_to_collect = self.map[player.pos]['item']

        obs = {player.id: self.get_obs(player) for player in self.players}

        infos = {player.id: player.get_info() for player in self.players}
        return obs, infos

    def step(
        self,
        actions: List[Tuple[Tuple[str, str], Tuple[str, float], Tuple[str,
                                                                      float]]],
    ):
        # action = (('move', 'up'), ('sand', -5), ('gold', 10))
        # action = (('consume', 'peanut'), ('gold', -5), ('peanut', 20))
        # action = (('collect', None), None, None))

        # TODO trader
        list_order = []
        id_2_order = [None] * self.num_player
        is_valid_buffer = []
        for player in self.players:
            action, sell_offer, buy_offer = actions[player.id]
            player = self.players[player.id]
            if self.valid_action(player, action, sell_offer, buy_offer):
                is_valid_buffer.append(True)
                if sell_offer is None or buy_offer is None:
                    continue
                list_order.append((player.pos, sell_offer, buy_offer))
                id_2_order[player.id] = len(list_order) - 1
            else:
                is_valid_buffer.append(False)
        match_order_list = self.trader.parse(list_order)

        # execute
        shuffled_player_ids = list(range(self.num_player))
        random.shuffle(shuffled_player_ids)
        for shuffled_player_id in shuffled_player_ids:
            player = self.players[shuffled_player_id]
            if is_valid_buffer[player.id]:
                self.map[player.pos]['player'] = None
                if id_2_order[player.id] is not None:
                    order_id = id_2_order[player.id]
                    sell_offer, buy_offer = match_order_list[order_id]
                else:
                    sell_offer, buy_offer = None, None
                player.execute(action, sell_offer, buy_offer)

                self.map[player.pos]['player'] = player
                player.item_to_collect = self.map[player.pos]['item']
            else:
                continue
        self.curr_step += 1

        obs = {player.id: self.get_obs(player) for player in self.players}
        rewards = {
            player.id: self.reward_parser.parse(player)
            for player in self.players
        }
        done = True if self.curr_step > EnvConfig.total_step else False
        infos = {player.id: player.get_info() for player in self.players}
        return obs, rewards, done, infos

    def get_obs(self, player: Player):
        player_x, player_y = player.pos
        x_min = max(player_x - EnvConfig.visual_radius, 0)
        x_max = min(player_x + EnvConfig.visual_radius, MapSize.width)
        y_min = max(player_y - EnvConfig.visual_radius, 0)
        y_max = min(player_y + EnvConfig.visual_radius, MapSize.height)

        local_obs = {}
        for i, x in enumerate(range(x_min, x_max)):
            for j, y in enumerate(range(y_min, y_max)):
                if (x, y) in self.map:
                    local_obs[(i, j)] = self.map[(x, y)]

        return local_obs

    def valid_action(
        self,
        player: Player,
        action: Tuple[str, str],
        sell_offer: Tuple[str, int],
        buy_offer: Tuple[str, int],
    ):
        # action = (('move', 'up'), ('sand', -5), ('gold', 10))
        # action = (('consume', 'peanut'), ('gold', -5), ('peanut', 20))

        is_action_valid = True
        primary_action, secondary_action = action

        # check offer
        if sell_offer != None and buy_offer != None:
            item_to_sell, sell_amount = sell_offer
            if player.backpack.get_item(item_to_sell).num < abs(sell_amount):
                is_action_valid = False
        else:
            item_to_sell = None

        # check move
        if primary_action == Action.move:
            direction = secondary_action
            x, y = player.pos
            if direction == Direction.up:
                y = min(y + 1, MapSize.height - 1)
            if direction == Direction.down:
                y = max(y - 1, 0)
            if direction == Direction.left:
                x = min(x + 1, MapSize.height - 1)
            if direction == Direction.right:
                x = max(x - 1, 0)

            if (x, y) in self.map.keys():
                if self.map[(x, y)]['player'] != None:
                    is_action_valid = False

        # check collect
        if primary_action == Action.collect:
            if player.backpack.remain_volume == 0:
                is_action_valid = False

        # check consume
        if primary_action == Action.consume:
            item_to_consume = secondary_action
            if item_to_consume == item_to_sell:
                least_amount = sell_amount + 1
            else:
                least_amount = 1

            if player.backpack.get_item(item_to_consume).num < least_amount:
                is_action_valid = False

        if not is_action_valid:
            print(
                f'Skip Invalid Action of Player {player.id}: {action} sell: {sell_offer} buy: {buy_offer}'
            )
        return is_action_valid