import sys
import random
from loguru import logger
from typing import Dict, List

from ecoevo.config import EnvConfig, MapSize
from ecoevo.maps import MapManager, Tile
from ecoevo.trader import Trader
from ecoevo.reward import RewardParser
from ecoevo.entities.player import Player
from ecoevo.entities.types import *


class EcoEvo:

    def __init__(self,
                 render_mode=None,
                 logging_level="WARNING",
                 logging_path="out.log"):
        self.render_mode = render_mode
        self.map_manager = MapManager()
        self.trader = Trader(EnvConfig.trade_radius)
        self.reward_parser = RewardParser()
        self.players: List[Player] = []
        # Logging
        logger.add(sys.stderr, level=logging_level)
        logger.add(logging_path, level=logging_level)

    @property
    def num_player(self):
        return len(self.players)

    def reset(
            self
    ) -> Tuple[Dict[IdType, Dict[PosType, Tile]], Dict[IdType, dict]]:
        self.players = []
        self.curr_step = 0
        self.map = self.map_manager.reset_map()
        self.reward_parser.reset()
        # Init players
        points = self.map_manager.sample(len(EnvConfig.personae))
        for id, persona in enumerate(EnvConfig.personae):
            player = Player(persona, id, points[id])
            self.players.append(player)
        self.map_manager.load_players(self.players)

        obs = {player.id: self.get_obs(player) for player in self.players}
        infos = {player.id: player.info for player in self.players}
        self.ids = [player.id for player in self.players]
        return obs, infos

    def step(
        self, actions: List[ActionType]
    ) -> Tuple[Dict[IdType, Dict[PosType, Tile]], Dict[IdType, float], bool,
               Dict[IdType, dict]]:
        self.curr_step += 1
        legal_deals = self.trader.filter_legal_deals(self.players, actions)
        matched_deals = self.trader.parse(legal_deals)

        # execute
        random.shuffle(self.ids)
        for id in self.ids:
            player = self.players[id]
            main_action, sell_offer, buy_offer = actions[player.id]
            if player.id in matched_deals:
                player.trade_result = 'Success'
                _, sell_offer, buy_offer = matched_deals[player.id]
                action = (main_action, sell_offer, buy_offer)
            else:
                if player.id in legal_deals:
                    player.trade_result = 'Failed'
                action = (main_action, None, None)

            if self.is_action_valid(player, actions[player.id]):
                self.map_manager.execute(player, action)

        # if self.curr_step // EnvConfig.refresh_interval:
        #     self.map_manager.refresh()

        obs = {player.id: self.get_obs(player) for player in self.players}
        rewards = {
            player.id: self.reward_parser.parse(player)
            for player in self.players
        }
        done = True if self.curr_step > EnvConfig.total_step else False
        infos = {player.id: player.info for player in self.players}
        return obs, rewards, done, infos

    def get_obs(self, player: Player) -> Dict[PosType, Tile]:
        player_x, player_y = player.pos
        x_min = max(player_x - EnvConfig.visual_radius, 0)
        x_max = min(player_x + EnvConfig.visual_radius, MapSize.width-1)
        y_min = max(player_y - EnvConfig.visual_radius, 0)
        y_max = min(player_y + EnvConfig.visual_radius, MapSize.height-1)

        local_obs = {}
        for i, x in enumerate(range(x_min, x_max)):
            for j, y in enumerate(range(y_min, y_max)):
                if (x, y) in self.map:
                    local_obs[(i, j)] = self.map[(x, y)]

        return local_obs

    def is_action_valid(self, player: Player, action: ActionType) -> bool:
        is_valid = True
        main_action, sell_offer, buy_offer = action
        primary_action, secondary_action = main_action

        # check move
        if primary_action == Action.move:
            x, y = player.next_pos(secondary_action)
            if (x, y) in self.map:
                if self.map[(x, y)].player != None:
                    hitted_player = self.map[(x, y)].player
                    is_valid = False
                    logger.warning(
                        f'Player {player.id} tried to hit player {hitted_player}'
                    )

        # check collect
        if primary_action == Action.collect:
            item = self.map[player.pos].item
            # no item to collect or the amount of item not enough
            if item is None or item.num < item.harvest_num:
                is_valid = False
                logger.warning(
                    f'No resource! Player {player.id} cannot collect {item} at {player.pos}'
                )
            # bagpack volume not enough
            if player.backpack.remain_volume < item.harvest_num * item.capacity:
                is_valid = False

                logger.warning(
                    f'Bag full! Player {player.id} cannot collect {item} at {self.pos}'
                )

        # check consume
        if primary_action == Action.consume:
            consume_item_name = secondary_action
            least_amount = player.backpack[consume_item_name].consume_num
            if sell_offer is not None:
                sell_item_name, sell_num = sell_offer
                if consume_item_name == sell_item_name:
                    least_amount += sell_num

            if player.backpack[consume_item_name].num < least_amount:
                is_valid = False
                logger.debug(
                    f'Player {player.id} cannot consume "{consume_item_name}" since num no more than {least_amount}.'
                )

        return is_valid