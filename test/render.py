import ecoevo
from ecoevo.render import WebApp


class MyRollOut(ecoevo.RollOut):

    def __init__(self):
        super().__init__()
        self.env = ecoevo.EcoEvo()

    def get_actions(self):
        obs = self.get_current_obs()
        return [(('idle', None), None, None)
                for i in range(self.env.num_player)]


my_rollout = MyRollOut()
web_app = WebApp(my_rollout)

if __name__ == '__main__':
    web_app.run_server()