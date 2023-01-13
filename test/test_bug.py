from helper import Action, Helper, Item


class TestBug:

    def test_54(self):
        # trader 和 env 关于action的验证不一致，导致交易和step里面的action_valid不一致
        h = Helper().init_points(
            ((8, 8), 0),
            ((8, 9), 1),
        ).reset().set_bag(
            (0, Item.gold, 10),
            (1, Item.sand, 10),
        ).step(
            (0, ((Action.idle, None), (Item.gold, -10), (Item.sand, 10))),
            (1, ((Action.collect, None), (Item.sand, -10), (Item.gold, 10))),
        ).assert_bag(
            (0, Item.sand, 10),
            (1, Item.gold, 10),
        )
