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
        # self.trader = Trader()
        self.reward_parser = RewardParser()
        self.players: List[Player] = []

        # allocate persona to player_id
        self.id_to_persona = {}
        curr_idx = 0
        for persona in EnvConfig.personae:
            persona_num = EnvConfig.persona_num(persona)
            for _ in range(persona_num):
                curr_id = EnvConfig.player_ids[curr_idx]
                self.id_to_persona[curr_id] = persona
                curr_idx += 1
        assert len(self.id_to_persona) == EnvConfig.player_num

    @property
    def num_player(self):
        return len(self.players)

    def reset(self, seed=None):
        self.curr_step = 0
        self.map = self.map_generator.gen_map()

        # Add agent
        player_pos = np.random.choice(MapSize.width * MapSize.height,
                                      size=EnvConfig.player_num,
                                      replace=False)

        for id in EnvConfig.player_ids:
            persona = self.id_to_persona(id)
            player = Player(persona, id)
            x = player_pos[id] % MapSize.width
            y = player_pos[id] // MapSize.width
            player.pos = (x, y)
            self.players.append(player)
            if player.pos not in self.map:
                self.map[player.pos] = {'agent': player}
            else:
                self.map[player.pos]['agent'] = player

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

        # TODO trader
        player_ids = list(range(self.num_player))
        random.shuffle(player_ids)
        for player_id in player_ids:
            action, sell_offer, buy_offer = actions[player_id]
            player = self.players[player_id]
            if self.valid_action(player, action, sell_offer, buy_offer):
                player.execute(action, sell_offer, buy_offer)
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
        # TODO
        is_action_valid = True
        primary_action, secondary_action = action
        item_to_sell, sell_amount = sell_offer
        if player.backpack.get_item(item_to_sell).num < sell_amount:
            is_action_valid = False

        if primary_action == Action.move:
            direction = secondary_action
            x, y = player.pos
            if direction == Direction.up:
                next_y = min(y + 1, MapSize.height - 1)
            if direction == Direction.down:
                next_y = max(y - 1, 0)
            if direction == Direction.left:
                next_x = min(x + 1, MapSize.height - 1)
            if direction == Direction.right:
                next_x = max(x - 1, 0)

            if self.map[(next_x, next_y)]['agent'] != None:
                is_action_valid = False

        if primary_action == Action.collect:
            if player.backpack.remain_volume == 0:
                is_action_valid = False

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
                f'Invalid Action: Player {player.id}: {action} buy: {buy_offer} sell: {sell_offer}'
            )
        return is_action_valid