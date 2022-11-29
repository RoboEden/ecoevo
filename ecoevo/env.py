import functools

from gymnasium.spaces import Discrete

from pettingzoo import ParallelEnv
from ecoevo.entities.agent import Action, Agent



class EcoEvo(ParallelEnv):
    metadata = {"render_modes": ["human"], "name": "ecoevo_v0"}

    def __init__(self, config, render_mode=None):
        """
        The init method takes in environment arguments and should define the following attributes:
        - agent_ids
        - action_spaces
        - observation_spaces
        These attributes should not be changed after initialization.
        """
        # self.possible_agents = ["player_" + str(r) for r in range(2)]
        # self.agent_name_mapping = dict(
        #     zip(self.possible_agents, list(range(len(self.possible_agents))))
        # )
        self.render_mode = render_mode
        self.config = config
        self.agents = config.agents

    # this cache ensures that same space object is returned for the same agent
    # allows action space seeding to work as expected
    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent):
        # gymnasium spaces are defined and documented here: https://gymnasium.farama.org/api/spaces/
        return Discrete(4)

    @functools.lru_cache(maxsize=None)
    def action_space(self, agent):
        return Discrete(3)



    # def close(self):
    #     """
    #     Close should release any graphical displays, subprocesses, network connections
    #     or any other environment data which should not be kept around after the
    #     user is no longer using the environment.
    #     """
    #     pass

    def reset(self, seed=None, return_info=False, options=None):
        """
        Reset needs to initialize the `agents` attribute and must set up the
        environment so that render(), and step() can be called without issues.
        Here it initializes the `num_moves` variable which counts the number of
        hands that are played.
        Returns the observations for each agent
        """
        self.agent_dict = {id: Agent(get_cfg(id)) for id in self.agent_ids}
        self.map = self.init_map()
        self.step = 0

        obs = {agent_id: self.get_obs(agent_id) for agent_id in self.agents}

        if not return_info:
            return obs
        else:
            infos = {agent_id: {} for agent_id in self.agents}
            return obs, infos

    def step(self, actions):
        """
        step(action) takes in an action for each agent and should return the
        - observations
        - rewards
        - terminations
        - truncations
        - infos
        dicts where each dict looks like {agent_1: item_1, agent_2: item_2}
        """        
        for agent_id in self.agents:
            agent = self.agent_dict[agent_id]
            action = actions[self.agents]
            if action in [Action.MOVE, Action.COLLECT, Action.CONSUME]:
                self.map = agent.execute(action)
            if action is [Action.TRADE]:
                own_offer = action[OFFER]
                nearby_offers = get_nearby_offer(agent)
                matched_offer = trader(own_offer, nearby_offers)
        
        # current observation is just the other player's most recent action
        obs = {agent: self.get_obs(id) for agent in self.agents}

        self.step += 1

        rewards = {agent_id: reward_parser(agent_id) for agent_id in self.agents}

        # typically there won't be any information in the infos, but there must
        # still be an entry for each agent
        done = True
        if done > self.config.max_len:
            done = True
        
        infos = {agent: {} for agent in self.agents}

        # if self.render_mode == "human":
        #     self.render()
        return obs, rewards, done, infos