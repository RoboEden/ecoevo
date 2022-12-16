import sys
import random
from loguru import logger
from typing import Dict, List

from ecoevo.config import EnvConfig, MapConfig
from ecoevo.trader import Trader
from ecoevo.reward import RewardParser
from ecoevo.entities import EntityManager, Tile, Player, ALL_ITEM_DATA
from ecoevo.types import *


class EcoEvo:

    def __init__(self,
                 render_mode=None,
                 total_step=EnvConfig.total_step,
                 trade_radius=EnvConfig.trade_radius,
                 visual_radius=EnvConfig.visual_radius,
                 personae=EnvConfig.personae,
                 bag_volume=EnvConfig.bag_volume,
                 logging_level="WARNING",
                 logging_path="out.log"):
        # Ugly change EnvConfig         
        EnvConfig.total_step=total_step
        EnvConfig.trade_radius=trade_radius
        EnvConfig.visual_radius=visual_radius
        EnvConfig.personae=personae
        EnvConfig.bag_volume=bag_volume

        self.render_mode = render_mode
        self.entity_manager = EntityManager()
        self.trader = Trader(EnvConfig.trade_radius)
        self.reward_parser = RewardParser()
        self.players: List[Player] = []
        # Logging
        logger.remove()
        logger.add(sys.stderr, level=logging_level)
        logger.add(logging_path, level=logging_level)

    @property
    def num_player(self) -> int:
        return len(self.players)

    @property
    def all_item_names(self) -> list:
        return list(ALL_ITEM_DATA.keys())

    def gettile(self, pos: PosType) -> Optional[Tile]:
        map = self.entity_manager.map
        if pos in map:
            return self.entity_manager.map[pos]
        else:
            return None

    def reset(
            self
    ) -> Tuple[Dict[IdType, Dict[PosType, Tile]], Dict[IdType, dict]]:
        self.players = []
        self.curr_step = 0
        self.reward_parser.reset()
        points = self.entity_manager.sample(len(EnvConfig.personae))
        for id, persona in enumerate(EnvConfig.personae):
            player = Player(persona=persona, id=id, pos=points[id])
            self.players.append(player)

        self.entity_manager.reset_map(self.players)

        obs = {player.id: self.get_obs(player) for player in self.players}
        infos = {}
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
                player.trade_result = TradeResult.success
                _, sell_offer, buy_offer = matched_deals[player.id]
                action = (main_action, sell_offer, buy_offer)
            else:
                if player.id in legal_deals:
                    player.trade_result = TradeResult.failed
                action = (main_action, None, None)

            if self.is_action_valid(player, actions[player.id]):
                self.entity_manager.execute(player, action)

        self.entity_manager.refresh_item()

        # if self.curr_step // EnvConfig.refresh_interval:
        #     self.entity_manager.refresh()

        obs = {player.id: self.get_obs(player) for player in self.players}
        rewards = {
            player.id: self.reward_parser.parse(player)
            for player in self.players
        }
        done = True if self.curr_step > EnvConfig.total_step else False
        infos = {}
        return obs, rewards, done, infos

    def get_obs(self, player: Player) -> Dict[PosType, Tile]:
        player_x, player_y = player.pos
        x_min = max(player_x - EnvConfig.visual_radius, 0)
        x_max = min(player_x + EnvConfig.visual_radius, MapConfig.width - 1)
        y_min = max(player_y - EnvConfig.visual_radius, 0)
        y_max = min(player_y + EnvConfig.visual_radius, MapConfig.height - 1)

        local_obs = {}
        for x in range(x_min, x_max + 1):
            for y in range(y_min, y_max + 1):
                tile = self.gettile((x, y))
                if tile:
                    local_x = x - player_x + EnvConfig.visual_radius
                    local_y = y - player_y + EnvConfig.visual_radius
                    local_obs[(local_x, local_y)] = tile

        return local_obs

    def is_action_valid(self, player: Player, action: ActionType) -> bool:
        is_valid = True
        main_action, sell_offer, buy_offer = action
        primary_action, secondary_action = main_action

        if primary_action == Action.idle:
            pass

        # check move
        elif primary_action == Action.move:
            x, y = player.next_pos(secondary_action)
            tile = self.gettile((x, y))
            if tile:
                if tile.player is not None:
                    hitted_player = tile.player
                    is_valid = False
                    logger.warning(
                        f'Player {player.id} at {player.pos} tried to hit player {hitted_player.id} at {hitted_player.pos}'
                    )

        # check collect
        elif primary_action == Action.collect:
            item = self.gettile(player.pos).item
            if item:
                # no item to collect or the amount of item not enough
                if item.num < item.harvest_num:
                    is_valid = False
                    logger.warning(
                        f'No resource! Player {player.id} cannot collect {item} at {player.pos}'
                    )
                # bagpack volume not enough
                if player.backpack.remain_volume < item.harvest_num * item.capacity:
                    is_valid = False

                    logger.warning(
                        f'Bag full! Player {player.id} cannot collect {item} at {player.pos}'
                    )
            else:
                is_valid = False
                logger.warning(
                    f'No item exists! Player {player.id} cannot collect {player.pos}'
                )

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
                    f'Player {player.id} cannot consume "{consume_item_name}" since num no more than {least_amount}.'
                )
        else:
            logger.debug(
                f'Failed to parse primary action. Player {player.id}: {primary_action} '
            )

        return is_valid