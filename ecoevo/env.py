import functools
from ecoevo.entities.player import Player
from ecoevo.maps.map import MapGenerator


class EcoEvo:
    metadata = {"render_modes": ["human"], "name": "ecoevo_v0"}

    def __init__(self, config, render_mode=None):
        """
        The init method takes in environment arguments and should define the following attributes:
        - player_ids
        - action_spaces
        - observation_spaces
        These attributes should not be changed after initialization.
        """
        # self.possible_players = ["player_" + str(r) for r in range(2)]
        # self.player_name_mapping = dict(
        #     zip(self.possible_players, list(range(len(self.possible_players))))
        # )
        self.render_mode = render_mode
        self.config = config
        self.players = [Player(name) for name in config.name]
        self.map_generator = MapGenerator()

    # this cache ensures that same space object is returned for the same player
    # allows action space seeding to work as expected
    # def close(self):
    #     """
    #     Close should release any graphical displays, subprocesses, network connections
    #     or any other environment data which should not be kept around after the
    #     user is no longer using the environment.
    #     """
    #     pass

    def reset(self, seed=None, return_info=False, options=None):
        """
        Reset needs to initialize the `players` attribute and must set up the
        environment so that render(), and step() can be called without issues.
        Here it initializes the `num_moves` variable which counts the number of
        hands that are played.
        Returns the observations for each player
        """
        self.player_dict = {id: Player(get_cfg(id)) for id in self.player_ids}
        self.map = self.map_generator.gen_map()
        self.curr_step = 0

        obs = {
            player_id: self.get_obs(player_id)
            for player_id in self.players
        }

        if not return_info:
            return obs
        else:
            infos = {player_id: {} for player_id in self.players}
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
        for player_id in self.players:
            player = self.player_dict[player_id]
            action = actions[self.players]
            if action in [Action.MOVE, Action.COLLECT, Action.CONSUME]:
                self.map = player.execute(action)
            if action is [Action.TRADE]:
                own_offer = action[OFFER]
                nearby_offers = get_nearby_offer(player)
                matched_offer = trader(own_offer, nearby_offers)

        # current observation is just the other player's most recent action
        obs = {player: self.get_obs(id) for player in self.players}

        self.curr_step += 1

        rewards = {
            player_id: reward_parser(player_id)
            for player_id in self.players
        }

        # typically there won't be any information in the infos, but there must
        # still be an entry for each player
        done = True
        if self.curr_step > self.config.max_len:
            done = True

        infos = {player: {} for player in self.players}

        # if self.render_mode == "human":
        #     self.render()
        return obs, rewards, done, infos