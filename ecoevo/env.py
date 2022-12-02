import numpy as np
from ecoevo.entities.player import Player
from ecoevo.maps import MapGenerator
from ecoevo.config import EnvConfig, MapSize
from ecoevo.config import PlayerConfig
from ecoevo.reward import RewardParser


class EcoEvo:

    def __init__(self, render_mode=None):
        self.render_mode = render_mode
        # self.players = [Player(name) for name in EnvConfig.name]
        self.map_generator = MapGenerator()
        self.players = []
        self.reward_parser = RewardParser()

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
        player_pos = np.random.choice(MapSize.width * MapSize.height, size=EnvConfig.player_num, replace=False)

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

    def step(self, actions):
        """
        step(action) takes in an action for each player and should return the
        - observations
        - rewards
        - terminations
        - truncations
        - infos
        dicts where each dict looks like {player_1: item_1, player_2: item_2}
        """
        for player in self.players:
            print(player)
            player.expend_energy(PlayerConfig.comsumption_per_step)
            # player = self.player_dict[player]
            # action = actions[self.players]
            # if action in [Action.MOVE, Action.COLLECT, Action.CONSUME]:
            #     self.map = player.execute(action)
            # if action is [Action.TRADE]:
            #     own_offer = action[OFFER]
            #     nearby_offers = get_nearby_offer(player)
            #     matched_offer = trader(own_offer, nearby_offers)

        # current observation is just the other player's most recent action
        obs = {player: self.get_obs(player) for player in self.players}

        self.curr_step += 1
        rewards = {player: RewardParser.parse(player) for player in self.players}

        # typically there won't be any information in the infos, but there must
        # still be an entry for each player
        done = True
        if self.curr_step > EnvConfig.total_step:
            done = True

        infos = {player: {} for player in self.players}

        # if self.render_mode == "human":
        #     self.render()
        return obs, rewards, done, infos

    def get_obs(self, player: Player):
        return self.map[player.pos]