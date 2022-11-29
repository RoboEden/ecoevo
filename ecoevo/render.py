from .env import EcoEvo

from pettingzoo.utils import parallel_to_aec, wrappers
def env(render_mode=None):
    """
    The env function often wraps the environment in wrappers by default.
    You can find full documentation for these methods
    elsewhere in the developer documentation.
    """
    internal_render_mode = render_mode if render_mode != "ansi" else "human"
    env = raw_env(render_mode=internal_render_mode)
    # This wrapper is only for environments which print results to the terminal
    if render_mode == "ansi":
        env = wrappers.CaptureStdoutWrapper(env)
    # this wrapper helps error handling for discrete action spaces
    env = wrappers.AssertOutOfBoundsWrapper(env)
    # Provides a wide vareity of helpful user errors
    # Strongly recommended
    env = wrappers.OrderEnforcingWrapper(env)
    return env


def raw_env(render_mode=None):
    """
    To support the AEC API, the raw_env() function just uses the from_parallel
    function to convert from a ParallelEnv to an AEC env
    """
    env = EcoEvo(render_mode=render_mode)
    env = parallel_to_aec(env)
    return env

def render(self):
    """
    Renders the environment. In human mode, it can print to terminal, open
    up a graphical window, or open up some other display that a human can see and understand.
    """
    if self.render_mode is None:
        gymnasium.logger.warn(
            "You are calling render method without specifying any render mode."
        )
        return

    if len(self.agents) == 2:
        string = "Current state: Agent1: {} , Agent2: {}".format(
            MOVES[self.state[self.agents[0]]], MOVES[self.state[self.agents[1]]]
        )
    else:
        string = "Game over"
    print(string)