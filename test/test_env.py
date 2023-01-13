from helper import ALL_ITEMS, Action, Helper, Item, Move

from ecoevo import EcoEvo


def test_collect_success():
    h = Helper().init_points(((8, 8), 0), ).init_tiles(((8, 8), Item.gold, ALL_ITEMS.gold.harvest_num + 1), ).reset()

    for _ in range(h.env.players[0].ability[Item.gold]):
        h.assert_tiles(((8, 8), Item.gold, ALL_ITEMS.gold.harvest_num + 1), ).step(
            (0, ((Action.collect, None), None, None)), )

    h.assert_tiles(((8, 8), Item.gold, 1), ).assert_no_error_log()
    assert h.env.players[0].collect_remain is None


def test_move_conflict():
    from ecoevo.config import MapConfig
    h = Helper().init_points(
        ((16, 13), 0),
        ((16, 15), 1),
    ).reset().step(
        (0, ((Action.move, Move.up), None, None)),
        (1, ((Action.move, Move.down), None, None)),
    ).assert_no_error_log()
    assert h.env.gettile((16, 14)).player.id in [0, 1]
    assert h.env.players[0].pos in [(16, 13), (16, 14)]
    assert h.env.players[1].pos in [(16, 14), (16, 15)]


def test_trade():
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
