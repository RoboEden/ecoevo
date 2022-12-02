import random
import numpy as np
from typing import List, Tuple

from ecoevo.config import EnvConfig, MapSize, PlayerConfig
from ecoevo.entities.player import Player
from ecoevo.maps import MapGenerator
from ecoevo.reward import RewardParser


class EcoEvo:

    def __init__(self, render_mode=None):
        self.render_mode = render_mode
        # self.players = [Player(name) for name in EnvConfig.name]
        self.map_generator = MapGenerator()
        self.reward_parser = RewardParser()
        self.players: List[Player] = []

    def reset(self, seed=None):
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
        for player in self.players:
            print(player)
            player.expend_energy(PlayerConfig.comsumption_per_step)

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
        rewards = {
            player: RewardParser.parse(player)
            for player in self.players
        }

        # typically there won't be any information in the infos, but there must
        # still be an entry for each player
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

    def valid_action(self, actions: Tuple[str, Tuple[str, float],
                                          Tuple[str, float], Tuple[str,
                                                                   float]]):
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
        self.health = max(0, self.health - PlayerConfig.comsumption_per_step)
        if self.is_valid(action, sell_offer, buy_offer):
            primary_action, secondary_action = action
            if primary_action == 'move':
                self.move(secondary_action)
            elif primary_action == 'collect':
                self.collect()
            elif primary_action == 'consume':
                self.consume(secondary_action)
        else:
            print(
                f'Invalid Action: Player {self.id}: {action} buy: {buy_offer} sell: {sell_offer}'
            )

        return all_offers