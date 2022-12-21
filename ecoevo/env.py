import sys
import random
from loguru import logger
from typing import Dict, List, Tuple, Optional

from ecoevo.config import EnvConfig, MapConfig
from ecoevo.trader import Trader
from ecoevo.reward import RewardParser
from ecoevo.entities import EntityManager, Tile, Player, ALL_ITEM_DATA
from ecoevo import types as tp
from ecoevo.analyser import Analyser
from ecoevo.types import Action


class EcoEvo:

    def __init__(self,
                 render_mode=None,
                 logging_level="WARNING",
                 logging_path="out.log"):
        self.render_mode = render_mode
        self.entity_manager = EntityManager()
        self.trader = Trader(EnvConfig.trade_radius)
        self.reward_parser = RewardParser()
        self.players: List[Player] = []

        # store infos for last step
        self.last_infos = {}

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

    def gettile(self, pos: tp.PosType) -> Optional[Tile]:
        map = self.entity_manager.map
        if pos in map:
            return self.entity_manager.map[pos]
        else:
            return None

    def reset(
            self
    ) -> Tuple[Dict[tp.IdType, Dict[tp.PosType, Tile]], Dict[tp.IdType, dict]]:
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
        self.last_infos = infos

        self.ids = [player.id for player in self.players]

        return obs, infos

    def step(self, actions: List[tp.ActionType]) -> Tuple[
        Dict[tp.IdType, Dict[tp.PosType, Tile]], Dict[tp.IdType, float], bool, Dict[tp.IdType, dict]]:
        """
        tarder parser

        :param actions:  all players actions

        :return: match_deals:  result of matched deals
        """

        self.curr_step += 1

        # trader
        legal_deals = self.trader.filter_legal_deals(self.players, actions)
        matched_deals = self.trader.parse(legal_deals)

        infos = {}

        # execute
        food_consume, food_collect = 0, 0
        random.shuffle(self.ids)
        for id in self.ids:
            player = self.players[id]
            main_action, sell_offer, buy_offer = actions[player.id]
            if player.id in matched_deals:
                player.trade_result = tp.TradeResult.success
                _, sell_offer, buy_offer = matched_deals[player.id]
                action = (main_action, sell_offer, buy_offer)
            else:
                if player.id in legal_deals:
                    player.trade_result = tp.TradeResult.failed
                action = (main_action, None, None)

            if self.is_action_valid(player, actions[player.id]):
                self.entity_manager.execute(player, action)

                # update action info
                (action_type, action_item), _, _ = action
                if action_type == Action.consume:
                    food_consume += 1 if player.backpack[action_item].disposable else 0
                if action_type == Action.collect:
                    food_collect += 1 if self.entity_manager.map[player.pos].item.disposable else 0
        infos['food_consume'] = food_consume
        infos['food_collect'] = food_collect

        # refresh items
        self.entity_manager.refresh_item()

        obs = {player.id: self.get_obs(player) for player in self.players}
        rewards = {player.id: self.reward_parser.parse(player) for player in self.players}
        done = True if self.curr_step > EnvConfig.total_step else False

        # trade and reward info
        trade_times, item_trade_times, item_trade_amount = Analyser.get_trade_data(matched_deals=matched_deals)
        sum_reward = sum(rewards.values())
        infos = {
            'trade_times': trade_times, 
            'item_trade_times': item_trade_times, 
            'item_trade_amount': item_trade_amount, 
            'sum_reward': sum_reward
        }

        # global game statistics
        infos['total_trade_times'] = infos[
            'trade_times'] + self.last_infos['total_trade_times'] if self.last_infos else infos['trade_times']
        for item in ALL_ITEM_DATA.keys():
            infos['total_{}_trade'.format(item)] = infos['item_trade_amount'][item] + self.last_infos[
                'total_{}_trade'.format(item)] if self.last_infos else infos['item_trade_amount'][item]
        infos['total_food_consume'] = infos[
            'food_consume'] + self.last_infos['total_food_consume'] if self.last_infos else infos['food_consume']
        infos['total_food_collect'] = infos[
            'food_collect'] + self.last_infos['total_food_collect'] if self.last_infos else infos['food_collect']

        # update last info
        self.last_infos = infos

        return obs, rewards, done, infos

    def get_obs(self, player: Player) -> Dict[tp.PosType, Tile]:
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

    def is_action_valid(self, player: Player, action: tp.ActionType) -> bool:
        is_valid = True
        main_action, sell_offer, buy_offer = action
        primary_action, secondary_action = main_action

        if primary_action == tp.Action.idle:
            pass

        # check move
        if primary_action == tp.Action.move:
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
        elif primary_action == tp.Action.collect:
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
        elif primary_action == tp.Action.consume:
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