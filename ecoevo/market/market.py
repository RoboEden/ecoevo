from typing import List, Dict, Tuple
import random

from loguru import logger

from ecoevo.config import EnvConfig
from ecoevo.entities import Player
from ecoevo.types import IdType, ItemNumType, ActionType

IDX_SUBMIT_ACTION, IDX_ACCEPT_ACTION, IDX_CANCEL_ACTION = 1, 2, 3


class Market(object):
    """
    market
    """

    def __init__(self) -> None:
        """
        market, initialise
        """

        self.players = None
        self.actions = None

    def trade(self, players: List[Player], actions: List[ActionType]) -> Dict[Tuple[IdType, IdType], ItemNumType]:
        """
        trade

        :param players:  list of all players
        :param actions:  list of all players' actions

        :return: transaction_graph:  item flows during trades
        """

        self.players = players
        self.actions = actions

        transaction_graph = self._accept_offers()
        self._cancel_offers()
        self._add_offers()

        return transaction_graph

    def _accept_offers(self) -> Dict[Tuple[IdType, IdType], ItemNumType]:
        """
        offer acceptions

        :return: transaction_graph:  item flows during trades
        """

        transaction_graph = {}

        shuffled_ids = [player.id for player in self.players]
        random.shuffle(shuffled_ids)
        for pid in shuffled_ids:
            player, accept_action = self.players[pid], self.actions[pid][IDX_ACCEPT_ACTION]

            # not accepting
            if not accept_action:
                continue

            pid_offer, offer_idx = accept_action
            if pid_offer == pid:
                logger.warning(f"player {pid} must accept offer of other's")
                continue
            player_offer: Player = self.players[pid_offer]
            offer = player_offer.offers[offer_idx]

            # offer does not exist
            if not offer:
                logger.error(f"Offer does not exist")
                continue

            # distance out of limit
            if abs(player.pos[0] -
                   player_offer.pos[0]) > EnvConfig.trade_radius or abs(player.pos[1] -
                                                                        player_offer.pos[1]) > EnvConfig.trade_radius:
                logger.error(f"Offer player too far to trade")
                continue

            # execute trade
            trade_success = player.try_accept_offer(offer)
            if trade_success:
                # update transaction graph
                (item_sell, num_sell), (item_buy, num_buy) = offer
                num_sell = abs(num_sell)
                transaction_graph[pid_offer, pid] = (item_sell, num_sell)
                transaction_graph[pid, pid_offer] = (item_buy, num_buy)

                player_offer.offer_accepted(offer_idx)

        return transaction_graph

    def _cancel_offers(self):
        """
        offer canceling
        """

        for player in self.players:
            offer_idx = self.actions[player.id][IDX_CANCEL_ACTION]
            if offer_idx is not None:
                player.offer_cancel(offer_idx)

    def _add_offers(self):
        """
        add a new offer
        """

        for player in self.players:
            offer = self.actions[player.id][IDX_SUBMIT_ACTION]
            if offer:
                add_success = player.offer_try_add(offer)

                if not add_success:
                    logger.debug(f"Player {player.id} add offer {offer} failed")
