import random
from typing import Dict, List

from ecoevo.config import EnvConfig, MapSize
from ecoevo.entities.player import Player
from ecoevo.maps import MapManager, Tile
from ecoevo.trader import Trader
from ecoevo.reward import RewardParser
from ecoevo.entities.types import *
from ecoevo.entities.items import ALL_ITEM_DATA

import sys
from loguru import logger


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
        self.logging_level = logging_level
        self.logging_path = logging_path
        logger.add(sys.stderr, level=logging_level)
        logger.add(logging_path, level=logging_level)

    @property
    def num_player(self):
        return len(self.players)

    def reset(self) -> Tuple[Dict[int, Dict[PosType, Tile]], Dict[int, dict]]:
        self.players = []
        self.curr_step = 0
        self.map = self.map_manager.reset_map()
        self.reward_parser.reset()

        # Init players
        points = self.map_manager.sample(len(EnvConfig.personae))
        for id, persona in enumerate(EnvConfig.personae):
            player = Player(persona, id, points[id])
            self.players.append(player)
        self.map_manager.allocate(self.players)

        obs = {player.id: self.get_obs(player) for player in self.players}
        infos = {player.id: player.info for player in self.players}
        self.ids = [player.id for player in self.players]
        return obs, infos

    def step(
        self, actions: List[ActionType]
    ) -> Tuple[Dict[int, Dict[PosType, Tile]], Dict[int, float], bool, Dict[
            int, dict]]:
        self.curr_step += 1
        legal_orders = self.get_legal_orders(actions)
        matched_orders = self.trader.parse(legal_orders)

        # execute
        random.shuffle(self.ids)
        for id in self.ids:
            player = self.players[id]
            action = actions[player.id]
            if player.id in matched_orders:
                main_action, _, _ = action
                _, sell_offer, buy_offer = matched_orders[player.id]
                action = (main_action, sell_offer, buy_offer)

            if self.validate(player, actions[player.id]):
                player.execute(action)

        self.map_manager.allocate(self.players)

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
        x_max = min(player_x + EnvConfig.visual_radius, MapSize.width)
        y_min = max(player_y - EnvConfig.visual_radius, 0)
        y_max = min(player_y + EnvConfig.visual_radius, MapSize.height)

        local_obs = {}
        for i, x in enumerate(range(x_min, x_max)):
            for j, y in enumerate(range(y_min, y_max)):
                if (x, y) in self.map:
                    local_obs[(i, j)] = self.map[(x, y)]

        return local_obs

    def get_legal_orders(
        self,
        actions: List[ActionType],
    ) -> Dict[int, OrderType]:
        legal_orders = {}
        for player in self.players:
            if self.validate(player, actions[player.id]):
                _, sell_offer, buy_offer = actions[player.id]
                legal_orders[player.id] = (player.pos, sell_offer, buy_offer)

        return legal_orders

    def _is_valid_trade(self, player: Player, sell_offer: OfferType,
                        buy_offer: OfferType) -> bool:
        if sell_offer is None or buy_offer is None:
            return False

        sell_item_name, sell_num = sell_offer
        buy_item_name, buy_num = buy_offer
        sell_num, buy_num = abs(sell_num), abs(buy_num)

        # Validate num
        if sell_num <= 0 or buy_num <= 0:
            return False

        # Validate sell
        if player.backpack[sell_item_name].num < sell_num:
            return False

        # Validate buy
        buy_item_volumne = ALL_ITEM_DATA[buy_item_name].capacity * buy_num
        if player.backpack.remain_volume < buy_item_volumne:
            return False

        return True

    def validate(self, player: Player, action: ActionType) -> bool:
        is_valid = True
        main_action, sell_offer, buy_offer = action
        primary_action, secondary_action = main_action

        # check offer
        is_valid = self._is_valid_trade(player, sell_offer, buy_offer)
        if sell_offer != None and buy_offer != None:
            item_to_sell, sell_amount = sell_offer
        else:
            item_to_sell = None

        # check move
        if primary_action == Action.move:
            direction = secondary_action
            x, y = player.pos
            if direction == Move.up:
                y = min(y + 1, MapSize.height - 1)
            if direction == Move.down:
                y = max(y - 1, 0)
            if direction == Move.right:
                x = min(x + 1, MapSize.height - 1)
            if direction == Move.left:
                x = max(x - 1, 0)

            if (x, y) in self.map.keys():
                if self.map[(x, y)].player != None:
                    is_valid = False

        # check collect
        if primary_action == Action.collect:
            if player.backpack.remain_volume == 0:
                is_valid = False

        # check consume
        if primary_action == Action.consume:
            item_to_consume = secondary_action
            if item_to_consume == item_to_sell:
                least_amount = sell_amount + 1
            else:
                least_amount = 1

            if player.backpack[item_to_consume].num < least_amount:
                is_valid = False

        if not is_valid:
            logger.debug(
                f'Skip Invalid Action of Player {player.id}: {action} sell: {sell_offer} buy: {buy_offer}'
            )
        return is_valid