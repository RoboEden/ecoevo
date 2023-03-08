import asyncio
import os, signal
import copy, json, sys
import pathlib
import queue
import threading
from ecoevo.gamecore import GameCore
from tornado.web import Application, StaticFileHandler, URLSpec
from tornado.websocket import WebSocketHandler

from loguru import logger

logger.remove()
logger.add(sys.stderr, level='DEBUG')


class DataQueue:

    def __init__(self):
        self.cond = threading.Condition()
        self.items = []

    def put(self, item):
        with self.cond:
            self.items.append(item)
            self.cond.notify()  # Wake 1 thread waiting on cond (if any)

    def getall(self):
        with self.cond:
            while len(self.items) == 0:
                self.cond.wait()
            items, self.items = self.items, []
        return items

    def clear(self):
        with self.cond:
            self.items = []
            self.cond.notify()


class Websocket(WebSocketHandler):
    """ a websocket handler that broadcasts to all clients """

    def initialize(
        self,
        action_queue: queue.Queue,
        output_queue: queue.Queue,
        gc: GameCore,
        init_message: dict,
        thread: threading.Thread,
        **kwargs,
    ) -> None:
        self.action_queue = action_queue
        self.output_queue = output_queue
        self.gc = gc
        self.init_message = init_message
        self.thread = thread
        self.done = False
        super().initialize(**kwargs)

    def check_origin(self, origin):
        """ in development allow ws from anywhere """
        if self.settings.get('debug', False):
            return True
        return super().check_origin(origin)

    def open(self, *args, **kwargs):
        """ we connected """
        logger.info('WebSocket opened')
        self.write_message(json.dumps(self.init_message))
        # TODO send config info

    def on_close(self):
        """ we're done """
        logger.info('WebSocket closed')
        # os.kill(os.getpid(), signal.SIGKILL)

    def on_message(self, message: str):
        """ we've said something, tell everyone """
        message = json.loads(message)
        if self.done:
            return

        def json_info(info):
            _info = copy.deepcopy(info)
            if 'transaction_graph' in _info:
                _info['transaction_graph'] = {str(k): list(v) for k, v in info['transaction_graph'].items()}
            return _info

        if message['body'] == 'Reseting':
            self.done = False
            obs, info = self.gc.reset()
            self.write_message(
                json.dumps([{
                    'map': {str(k): json.loads(v.json())
                            for k, v in self.gc.entity_manager.map.items()},
                    'info': json_info({
                        **info, 'curr_step': 0
                    }),
                    'reward': {player.id: 0.0
                               for player in self.gc.players},
                    'done': self.done,
                }]))
            self.output_queue.put([obs, info])

        elif message['body'] == 'Requesting':
            actions = self.action_queue.get()
            obs, reward, done, info = self.gc.step(actions)
            self.write_message(
                json.dumps([{
                    'map': {str(k): json.loads(v.json())
                            for k, v in self.gc.entity_manager.map.items()},
                    'info': json_info(info),
                    'reward': reward,
                    'done': done,
                }]))
            self.done = done
            self.output_queue.put([obs, reward, done, info])
        elif message['body'] == 'Shutdown':
            self.thread.join()
        else:
            print('Unrecognised')


class WebApp:

    def __init__(self, gc: GameCore, init_message: dict, port=8081):
        self.action_queue = queue.Queue(1)
        self.output_queue = queue.Queue(1)
        self.thread = threading.Thread(target=self.target)
        url1 = URLSpec(r'/ws/(.*)',
                       Websocket,
                       kwargs={
                           'action_queue': self.action_queue,
                           'output_queue': self.output_queue,
                           'gc': gc,
                           'init_message': init_message,
                           'thread': self.thread
                       })
        url2 = URLSpec(r'/(.*)',
                       StaticFileHandler,
                       kwargs={
                           'path': f'{pathlib.Path(__file__).parent}/static',
                           'default_filename': f'index.html'
                       })
        self.app = Application(
            [url1, url2],
            debug=True,
        )
        self.port = port

    def target(self):

        async def run_server():
            self.app.listen(self.port)
            logger.info(f'listening on port:{self.port}\n')
            print(f'WebApp ==running on "http://127.0.0.1:{self.port}"\n')
            print(' * Debug mode:', 'on')

        async def main():
            """ parse command line, make and start """
            asyncio.create_task(run_server())
            shutdown_event = asyncio.Event()
            await shutdown_event.wait()

        asyncio.run(main())

    def run(self):
        self.thread.start()