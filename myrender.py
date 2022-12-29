import ecoevo
from ecoevo.config import EnvConfig


class MyWrapper(ecoevo.EcoEvo):

    def __init__(self,
                 render_mode=None,
                 config=EnvConfig,
                 logging_level="WARNING",
                 logging_path="out.log"):
        super().__init__(render_mode, config, logging_level, logging_path)

    def get_action(self):
        return [(('idle', None), None, None) for i in range(self.num_player)]


wrapped_env = MyWrapper()
web_app = ecoevo.WebApp(wrapped_env)

if __name__ == '__main__':
    web_app.run_server()