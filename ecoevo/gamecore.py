import random
import sys
from copy import deepcopy
from typing import Dict, List, Optional, Tuple

from loguru import logger

from ecoevo.analyser import Analyser
from ecoevo.config import EnvConfig, MapConfig, PlayerConfig
from ecoevo.entities import ALL_ITEM_DATA, EntityManager, Player, Tile
from ecoevo.reward import RewardParser
from ecoevo.trader import Trader
from ecoevo.types import Action, ActionType, IdType, PosType, TradeResult


class GameCore:

    def __init__(self, config=EnvConfig, logging_level="WARNING", logging_path="out.log"):
        self.cfg = config
        self.entity_manager = EntityManager()
        self.trader = Trader(self.cfg.trade_radius)
        self.reward_parser = RewardParser()
        self.players: List[Player] = []

        self.info = {}

        # Logging
        logger.remove()
        logger.add(sys.stderr, level=logging_level)
        logger.add(logging_path, level=logging_level)

    @property
    def num_player(self) -> int:
        return len(self.players)

    @property
    def all_item_names(self) -> List[str]:
        return list(ALL_ITEM_DATA.keys())

    def gettile(self, pos: PosType) -> Optional[Tile]:
        map = self.entity_manager.map
        if pos in map:
            return self.entity_manager.map[pos]
        else:
            return None

    def reset(self) -> Tuple[Dict[IdType, Dict[PosType, Tile]], Dict[IdType, dict]]:
        self.players = []
        self.curr_step = 0
        self.reward_parser.reset()
        self.analyser = Analyser()
        self.trader.dict_flow = {}
        points = self.cfg.init_points or self.entity_manager.sample(len(self.cfg.personae))
        for id, persona in enumerate(self.cfg.personae):
            player = Player(persona=persona, id=id, pos=points[id])
            self.players.append(player)

        self.entity_manager.reset_map(self.players, random_generate=self.cfg.random_generate_map)

        obs = {player.id: self.get_obs(player) for player in self.players}
        self.info = {}

        self.shuffled_ids = [player.id for player in self.players]

        return obs, deepcopy(self.info)

    def step(
        self, actions: List[ActionType]
    ) -> Tuple[Dict[IdType, Dict[PosType, Tile]], Dict[IdType, float], bool, Dict[IdType, dict]]:
        random.shuffle(self.shuffled_ids)
        self.curr_step += 1

        # validate trade action
        for id, action in enumerate(actions):
            main_action, sell_offer, buy_offer = action
            player = self.players[id]
            if sell_offer is None or buy_offer is None:
                actions[id] = (main_action, None, None)
                player.trade_result = TradeResult.absent
            else:
                if self.is_trade_valid(player, action):
                    player.trade_result = TradeResult.failed  # may changed to success later if the deal is matched
                else:
                    actions[id] = (main_action, None, None)
                    player.trade_result = TradeResult.illegal
                player.last_action.sell_offer.sell_item = sell_offer[0]
                player.last_action.sell_offer.sell_num = sell_offer[1]
                player.last_action.buy_offer.buy_item = buy_offer[0]
                player.last_action.buy_offer.buy_num = buy_offer[1]

        # match trade
        matched_deals, transaction_graph = self.trader.parse(self.players, actions)

        # execute trade
        success_trades = {}
        for id in self.shuffled_ids:
            if id in matched_deals:
                player = self.players[id]
                _, sell_offer, buy_offer = matched_deals[id]
                player.trade(sell_offer, buy_offer)
                player.trade_result = TradeResult.success
                success_trades[id] = (sell_offer, buy_offer)

        # validate and execute main action
        executed_main_actions = {}
        for id in self.shuffled_ids:
            player = self.players[id]
            action = actions[id]
            player.last_action.main_action.primary = action[0][0]
            player.last_action.main_action.secondary = action[0][1]
            if self.is_main_action_valid(player, action):
                self.entity_manager.execute_main_action(player, action)
                executed_main_actions[id] = action[0]

        # health decrease
        for id in self.shuffled_ids:
            player = self.players[id]
            player.health = max(0, player.health - PlayerConfig.comsumption_per_step)

        # refresh items
        self.entity_manager.refresh_item()

        # generate obs, reward, info
        obs = {player.id: self.get_obs(player) for player in self.players}
        rewards = {player.id: self.reward_parser.parse(player) for player in self.players}
        done = self.curr_step >= self.cfg.total_step
        self.info = self.analyser.get_info(
            self.curr_step, done, self.info, self.players, self.entity_manager, matched_deals, transaction_graph,
            executed_main_actions, {
                player.id: {
                    'reward': rewards[player.id],
                    'utility': self.reward_parser.last_utilities[player.id],
                    'item_utility': self.reward_parser.last_item_utilities[player.id],
                    'cost': self.reward_parser.total_costs[player.id],
                }
                for player in self.players
            })
        self.info['transaction_graph'] = transaction_graph

        return obs, rewards, done, deepcopy(self.info)

    def get_obs(self, player: Player) -> Dict[PosType, Tile]:
        player_x, player_y = player.pos
        x_min = max(player_x - self.cfg.visual_radius, 0)
        x_max = min(player_x + self.cfg.visual_radius, MapConfig.width - 1)
        y_min = max(player_y - self.cfg.visual_radius, 0)
        y_max = min(player_y + self.cfg.visual_radius, MapConfig.height - 1)

        local_obs = {}
        for x in range(x_min, x_max + 1):
            for y in range(y_min, y_max + 1):
                tile = self.gettile((x, y))
                if tile:
                    local_x = x - player_x + self.cfg.visual_radius
                    local_y = y - player_y + self.cfg.visual_radius
                    local_obs[(local_x, local_y)] = tile

        return local_obs

    def is_trade_valid(self, player: Player, action: ActionType) -> bool:
        _, sell_offer, buy_offer = action

        if sell_offer is None or buy_offer is None:
            return False

        sell_item_name, sell_num = sell_offer
        buy_item_name, buy_num = buy_offer

        if sell_item_name == buy_item_name or sell_num >= 0 or buy_num <= 0:
            return False

        # check sell item amount
        sell_item = player.backpack[sell_item_name]
        if sell_item.num < abs(sell_num):
            return False

        # check buy item bag volume
        buy_item_volume = player.backpack[buy_item_name].capacity * buy_num
        if player.backpack.remain_volume < buy_item_volume:
            return False

        return True

    def is_main_action_valid(self, player: Player, action: ActionType) -> bool:
        main_action, _, _ = action
        primary_action, secondary_action = main_action

        # Check main action
        if primary_action == Action.idle:
            return True

        # check move
        elif primary_action == Action.move:
            if secondary_action is None:
                logger.critical(f'Player {player.id} move with no direction')
                return False
            next_pos = player.next_pos(secondary_action)
            if player.pos == next_pos:
                logger.warning(f'Player {player.id} move towards map boarder')
                return False
            tile = self.gettile(next_pos)
            if tile:
                if tile.player is not None:
                    hitted_player = tile.player
                    logger.warning(
                        f'Player {player.id} at {player.pos} tried to hit player {hitted_player.id} at {hitted_player.pos}'
                    )
                    return False

        # check collect
        elif primary_action == Action.collect:
            item = self.gettile(player.pos).item
            if item:
                # no item to collect or the amount of item not enough
                if item.num < item.harvest_num:
                    logger.warning(f'No resource! Player {player.id} cannot collect {item} at {player.pos}')
                    return False
                # bagpack volume not enough
                least_volume = item.harvest_num * item.capacity
                if player.backpack.remain_volume < least_volume:
                    logger.warning(f'Bag full! Player {player.id} cannot collect {item} at {player.pos}')
                    return False
            else:
                logger.warning(f'No item exists! Player {player.id} cannot collect {player.pos}')
                return False

        # check consume
        elif primary_action == Action.consume:
            if secondary_action is None:
                return False

            consume_item_name = secondary_action

            # handle consume and sell same item
            least_num = player.backpack[consume_item_name].consume_num
            if player.backpack[consume_item_name].num < least_num:
                logger.warning(
                    f'Player {player.id} cannot consume "{consume_item_name}" since num no more than {least_num}.')
                return False
        else:
            logger.warning(f'Failed to parse primary action. Player {player.id}: {primary_action} ')
            return False

        return True
