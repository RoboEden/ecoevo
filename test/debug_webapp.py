import json
import logging
import threading
import copy
from ecoevo.webapp import WebApp
from ecoevo.gamecore import GameCore
from test_random_actions import sample_action, sample_main_action
from ecoevo.webapp.app import DataQueue
from ecoevo.config import EnvConfig, MapConfig

log = logging.getLogger(__name__)

class TestConfig(EnvConfig):
    total_step = 1000

gc = GameCore(config=TestConfig, logging_level='CRITICAL')
data_queue = DataQueue()

def json_info(info):
    _info = copy.deepcopy(info)
    if 'transaction_graph' in _info:
        _info['transaction_graph'] = {str(k): list(v) for k, v in info['transaction_graph'].items()}
    return _info

def reset_callback():
    obs, info = gc.reset()
    done = False
    # data_queue.clear()
    data_queue.put({
        'map': {str(k): json.loads(v.json())
                for k, v in gc.entity_manager.map.items()},
        'info': json_info({
            **info, 'curr_step': 0
        }),
        'reward': {player.id: 0.0
                    for player in gc.players},
        'done': done,
    })
    return done

def step_callback():
    actions1 = [(sample_main_action(), ('gold', -1), ('pineapple', 1)) for _ in range(gc.num_player // 2)]
    actions2 = [(sample_main_action(), ('pineapple', -1), ('gold', 1))
                for _ in range(gc.num_player - gc.num_player // 2)]
    actions = [*actions1, *actions2]
    # actions = [(('idle', None), None, None) for _ in range(len(obs))]
    obs, reward, done, info = gc.step(actions)
    data_queue.put({
        'map': {str(k): json.loads(v.json())
                for k, v in gc.entity_manager.map.items()},
        'info': json_info(info),
        'reward': reward,
        'done': done,
    })
    return done

init_message = {'totalStep': gc.cfg.total_step, 'mapSize': MapConfig.width}

webapp = WebApp(data_queue, reset_callback, step_callback, init_message)
t = threading.Thread(target=webapp.run)
t.start()

# i = 0
# done = reset_callback()
# time.sleep(0.5)
# while not done:
#     i += 1
#     done = step_callback()