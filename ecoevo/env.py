import random
import numpy as np
from typing import List, Tuple
from ecoevo.entities.player import Player
from ecoevo.maps import MapGenerator
from ecoevo.config import EnvConfig, MapSize


class EcoEvo:

    def __init__(self, render_mode=None):
        self.render_mode = render_mode
        # self.players = [Player(name) for name in EnvConfig.name]
        self.map_generator = MapGenerator()
        self.players: List[Player] = []

    def reset(self, seed=None):
        """
        Reset needs to initialize the `players` attribute and must set up the
        environment so that render(), and step() can be called without issues.
        Here it initializes the `num_moves` variable which counts the number of
        hands that are played.
        Returns the observations for each player
        """
        self.curr_step = 0
        self.map = self.map_generator.gen_map()

        # Add agent
        player_pos = np.random.choice(MapSize.width * MapSize.height,
                                      size=EnvConfig.player_num,
                                      replace=False)

        for i, name in enumerate(EnvConfig.name):
            player = Player(name)
            x = player_pos[i] // MapSize.width
            y = player_pos[i] // MapSize.height
            player.pos = (x, y)
            self.players.append(player)
            if player.pos not in self.map:
                self.map[player.pos] = {'agent': player}
            else:
                self.map[player.pos]['agent'] = player

        obs = {player: self.get_obs(player) for player in self.players}

        infos = {player: {} for player in self.players}
        return obs, infos

    def step(self, actions: Tuple[str, Tuple[str, float], Tuple[str, float],
                                  Tuple[str, float]]):
        """
        step(action) takes in an action for each player and should return the
        - observations
        - rewards
        - terminations
        - truncations
        - infos
        dicts where each dict looks like {player_1: item_1, player_2: item_2}
        """

        # action = (('move', 'up'), ('sand', -5), ('gold', 10))
        # action = (('collect', None), ('pumpkin', -5), ('coral', 10))
        # action = (('consume', 'peanut'), ('peanut', -5), ('gold', 1))

        # all_offers = self.get_all_offer(actions)
        # matched_offers = self.trader(all_offers)
        # for offer in matched_offers:
        #     self.trader.trade(dict_match)

        player_ids = random.shuffle(list(range(len(self.players))))
        for player_id in player_ids:
            action, sell_offer, buy_offer = actions[player_id]
            player = self.players[player_id]
            if self.is_valid(action, sell_offer, buy_offer):
                primary_action, secondary_action = action
                if primary_action == 'move':
                    player.move(secondary_action)
                elif primary_action == 'collect':
                    player.collect()
                elif primary_action == 'consume':
                    player.consume(secondary_action)
            else:
                print(
                    f'Invalid Action: Player {player_id}: {action} buy: {buy_offer} sell: {sell_offer}'
                )
                continue

        obs = {player: self.get_obs(player) for player in self.players}

        self.curr_step += 1
        reward_parser = lambda x: 1
        rewards = {player: reward_parser(player) for player in self.players}
        done = True
        if self.curr_step > EnvConfig.total_step:
            done = True

        infos = {player: {} for player in self.players}
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

    def get_all_valid_offer(self, actions: Tuple[str, Tuple[str, float],
                                                 Tuple[str, float],
                                                 Tuple[str, float]]):
        """
        step(action) takes in an action for each player and should return the
        - observations
        - rewards
        - terminations
        - truncations
        - infos
        dicts where each dict looks like {player_1: item_1, player_2: item_2}
        """

        # action = ('move_up', ('pumpkin', -1), ('sand', -5), ('gold', 10))

        all_offers = []
        for player_id in range(len(actions)):
            action, sell_offer, buy_offer = actions[player_id]
            player = self.players[player_id]
            name, num = sell_offer
            item = player.backpack.get_item(name)
            if num >= item.num:
                all_offers.append((player.pos, buy_offer, sell_offer))
            else:
                continue
        return all_offers