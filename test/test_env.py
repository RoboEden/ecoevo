from helper import ALL_ITEMS, Action, Helper, Item

from ecoevo import EcoEvo


class TestDemo:

    def test_collect(self):
        h = Helper().init_points(((8, 8), 0), ).init_tiles(
            ((8, 8), Item.gold, ALL_ITEMS.gold.consume_num + 1), ).reset().assert_tiles(
                ((8, 8), Item.gold, ALL_ITEMS.gold.consume_num + 1), ).step(
                    (0, ((Action.collect, None), None, None)), ).assert_tiles(((8, 8), Item.gold, 1), )

    def test_trade(self):
        h = Helper().init_points(
            ((8, 8), 0),
            ((8, 9), 1),
        ).reset().set_bag(
            (0, Item.gold, 5),
            (1, Item.sand, 10),
        ).step(
            (0, ((Action.idle, None), (Item.gold, -5), (Item.sand, 10))),
            (1, ((Action.idle, None), (Item.sand, -10), (Item.gold, 5))),
        ).assert_bag(
            (0, Item.sand, 10),
            (1, Item.gold, 5),
        )
        transaction_graph = h.info['transaction_graph']
        assert transaction_graph[(0, 1)] == (Item.gold, 5)
        assert transaction_graph[(1, 0)] == (Item.sand, 10)
        assert len(transaction_graph) == 2