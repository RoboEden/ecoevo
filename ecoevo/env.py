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


class EcoEvo:

    def __init__(self, render_mode=None, config=EnvConfig, logging_level="WARNING", logging_path="out.log"):
        self.cfg = config
        self.render_mode = render_mode
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
        points = self.entity_manager.sample(len(self.cfg.personae))
        for id, persona in enumerate(self.cfg.personae):
            player = Player(persona=persona, id=id, pos=points[id])
            self.players.append(player)

        self.entity_manager.reset_map(self.players)

        obs = {player.id: self.get_obs(player) for player in self.players}
        self.info = {}

        self.ids = [player.id for player in self.players]

        return obs, deepcopy(self.info)

    def step(
        self, actions: List[ActionType]
    ) -> Tuple[Dict[IdType, Dict[PosType, Tile]], Dict[IdType, float], bool, Dict[IdType, dict]]:
        actions_valid = {}
        self.curr_step += 1

        # First check all main actions
        is_action_valids = [True] * len(actions)
        for player_id, action in enumerate(actions):
            player = self.players[player_id]
            is_action_valids[player_id] = self.is_main_action_valid(player=player, action=action)
            # Clear offers if not valid
            if not is_action_valids[player_id]:
                actions[player_id] = ((Action.idle, None), None, None)

        # trader
        matched_deals = self.trader.parse(players=self.players, actions=actions)

        # execute
        random.shuffle(self.ids)
        for id in self.ids:
            # Validation
            if not is_action_valids[id]:
                continue

            player = self.players[id]
            main_action, sell_offer, buy_offer = actions[player.id]
            if player.id in matched_deals:
                _, sell_offer, buy_offer = matched_deals[player.id]
                action = (main_action, sell_offer, buy_offer)
            else:
                action = (main_action, None, None)

            self.entity_manager.execute(player, action)
            if player.id in self.trader.legal_deals:
                if player.trade_result != TradeResult.success:
                    player.trade_result = TradeResult.failed
            actions_valid[player.id] = action[0]
            # consumption
            player.health = max(0, player.health - PlayerConfig.comsumption_per_step)

        obs = {player.id: self.get_obs(player) for player in self.players}
        rewards = {player.id: self.reward_parser.parse(player) for player in self.players}
        done = True if self.curr_step > self.cfg.total_step else False
        self.info = Analyser.get_info(done=done,
                                      info=self.info,
                                      players=self.players,
                                      matched_deals=matched_deals,
                                      actions_valid=actions_valid,
                                      reward_info={
                                          player.id: {
                                              'reward': rewards[player.id],
                                              'utility': self.reward_parser.last_utilities[player.id],
                                              'cost': self.reward_parser.total_costs[player.id]
                                          }
                                          for player in self.players
                                      })

        # refresh items
        self.entity_manager.refresh_item()

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

    def is_main_action_valid(self, player: Player, action: ActionType) -> bool:
        is_valid = True
        main_action, sell_offer, buy_offer = action
        primary_action, secondary_action = main_action

        if primary_action == Action.idle:
            return is_valid

        # check move
        elif primary_action == Action.move:
            x, y = player.next_pos(secondary_action)
            tile = self.gettile((x, y))
            if tile:
                if tile.player is not None:
                    hitted_player = tile.player
                    is_valid = False
                    logger.debug(
                        f'Player {player.id} at {player.pos} tried to hit player {hitted_player.id} at {hitted_player.pos}'
                    )

        # check collect
        elif primary_action == Action.collect:
            item = self.gettile(player.pos).item
            if item:
                # no item to collect or the amount of item not enough
                if item.num < item.harvest_num:
                    is_valid = False
                    logger.debug(f'No resource! Player {player.id} cannot collect {item} at {player.pos}')
                # bagpack volume not enough
                least_volume = item.harvest_num * item.capacity
                if sell_offer is not None and buy_offer is not None:
                    buy_item_name, buy_num = buy_offer
                    least_volume += buy_num * player.backpack[buy_item_name].capacity

                if player.backpack.remain_volume < least_volume:
                    is_valid = False

                    logger.debug(f'Bag full! Player {player.id} cannot collect {item} at {player.pos}')
            else:
                is_valid = False
                logger.debug(f'No item exists! Player {player.id} cannot collect {player.pos}')

        # check consume
        elif primary_action == Action.consume:
            consume_item_name = secondary_action

            # handle consume and sell same item
            least_amount = player.backpack[consume_item_name].consume_num
            if sell_offer is not None and buy_offer is not None:
                sell_item_name, sell_num = sell_offer
                if consume_item_name == sell_item_name:
                    least_amount += sell_num

            if player.backpack[consume_item_name].num < least_amount:
                is_valid = False
                logger.debug(
                    f'Player {player.id} cannot consume "{consume_item_name}" since num no more than {least_amount}.')
        else:
            logger.debug(f'Failed to parse primary action. Player {player.id}: {primary_action} ')

        return is_valid
