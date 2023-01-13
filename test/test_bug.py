from helper import Action, Helper, Item, Move


def test_38():
    h = Helper()
    h.init_points(((0, 0), 0), )
    h.reset()
    h.step(
        (0, ((Action.move, Move.down), None, None)),\
    )
    h.assert_pos_player(((0, 0), 0), )
    h.assert_no_error_log()


def test_54():
    # trader 和 env 关于action的验证不一致，导致交易和step里面的action_valid不一致
    h = Helper()
    h.init_points(
        ((8, 8), 0),
        ((8, 9), 1),
    )
    h.reset()
    h.set_bag(
        (0, Item.gold, 10),
        (1, Item.sand, 10),
    )
    h.step(
        (0, ((Action.idle, None), (Item.gold, -10), (Item.sand, 10))),
        (1, ((Action.collect, None), (Item.sand, -10), (Item.gold, 10))),
    )
    h.assert_bag(
        (0, Item.sand, 10),
        (1, Item.gold, 10),
    )
