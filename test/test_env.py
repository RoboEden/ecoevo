from helper import ALL_ITEMS, Action, Helper, Item, Move

from ecoevo import EcoEvo


def test_collect_success():
    h = Helper()
    h.init_points(((8, 8), 0), )
    h.init_tiles(((8, 8), Item.gold, ALL_ITEMS.gold.harvest_num + 1), )
    h.reset()

    for _ in range(h.env.players[0].ability[Item.gold]):
        h.assert_tiles(((8, 8), Item.gold, ALL_ITEMS.gold.harvest_num + 1), )
        h.step((0, ((Action.collect, None), None, None)), )

    h.assert_tiles(((8, 8), Item.gold, 1), )
    h.assert_no_error_log()
    assert h.env.players[0].collect_remain is None


def test_move_conflict():
    from ecoevo.config import MapConfig
    h = Helper()
    h.init_points(
        ((16, 13), 0),
        ((16, 15), 1),
    )
    h.reset()
    h.step(
        (0, ((Action.move, Move.up), None, None)),
        (1, ((Action.move, Move.down), None, None)),
    )
    h.assert_no_error_log()
    assert h.env.gettile((16, 14)).player.id in [0, 1]
    assert h.env.players[0].pos in [(16, 13), (16, 14)]
    assert h.env.players[1].pos in [(16, 14), (16, 15)]


def test_health_decrease():
    from ecoevo.config import PlayerConfig
    h = Helper()
    h.reset()
    D = PlayerConfig.comsumption_per_step
    init_health = [1, D, D + 1]
    actions = []
    for i in range(3):
        h.env.players[i].health = init_health[i]
        h.env.players[i + 3].health = init_health[i]
        h.env.players[i + 3].backpack.pineapple.num = ALL_ITEMS.pineapple.consume_num
        actions.append((i + 3, ((Action.consume, Item.pineapple), None, None)))
    h.step(*actions)
    E = ALL_ITEMS.pineapple.consume_num * ALL_ITEMS.pineapple.supply
    for i in range(3):
        assert h.env.players[i].health == max(init_health[i] - D, 0)
        assert h.env.players[i + 3].health == min(init_health[i] + E, PlayerConfig.max_health) - D
        assert h.env.reward_parser.last_costs[i] > h.env.reward_parser.last_costs[i + 3] or (i == 2)


def test_trade():
    h = Helper().init_points(
        ((8, 8), 0),
        ((8, 9), 1),
    )
    h.reset()
    h.set_bag(
        (0, Item.gold, 5),
        (1, Item.sand, 10),
    )
    h.step(
        (0, ((Action.idle, None), (Item.gold, -5), (Item.sand, 10))),
        (1, ((Action.idle, None), (Item.sand, -10), (Item.gold, 5))),
    )
    h.assert_bag(
        (0, Item.sand, 10),
        (1, Item.gold, 5),
    )
    transaction_graph = h.info['transaction_graph']
    assert transaction_graph[(0, 1)] == (Item.gold, 5)
    assert transaction_graph[(1, 0)] == (Item.sand, 10)
    assert len(transaction_graph) == 2
