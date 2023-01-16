from helper import ITEMS, Action, Helper, Item, Move

from ecoevo.config import PlayerConfig


class TestCollect:

    def test_success(self):
        h = Helper()
        h.init_pos({0: (8, 8)})
        G = ITEMS.gold.harvest_num + 1
        h.init_tiles({
            (8, 8): (Item.gold, G),
        })
        h.reset()

        for _ in range(h.env.players[0].ability[Item.gold]):
            assert h.get_tile_item((8, 8)) == (Item.gold, G)
            h.step({
                0: ((Action.collect, None), None, None),
            })

        assert h.get_tile_item((8, 8)) == (Item.gold, 1)
        assert h.get_error_log() == ''
        assert h.env.players[0].collect_remain is None

    def test_exceed_volumn_after_trade(self):
        # 潜在风险：trade之后collect之前没有做背包容量检查
        h = Helper()
        h.init_pos({
            0: (0, 0),
            1: (0, 1),
        })
        h.init_tiles({(0, 0): (Item.coral, 1)})
        h.reset()
        S = 1
        G = (PlayerConfig.bag_volume - S * ITEMS.stone.capacity) // ITEMS.gold.capacity
        h.env.players[0].backpack.stone.num = 1
        h.env.players[1].backpack.gold.num = G

        h.step({
            0: ((Action.collect, None), (Item.stone, -1), (Item.gold, G)),
            1: ((Action.idle, None), (Item.gold, -G), (Item.stone, 1)),
        })

        assert h.get_tile_item((0, 0)) == (Item.coral, 1)
        assert h.env.players[0].backpack.gold.num == G
        assert h.env.players[0].backpack.coral.num == 0
        assert h.env.players[1].backpack.stone.num == 1
        assert h.get_error_log() == ''


class TestMove:

    def test_border_error_log(self):
        # player 在边界处如果输出非法的移动动作， 会报warning "Player X  tried to hit player X"
        h = Helper()
        h.init_pos({
            0: (0, 0),
        })
        h.reset()

        h.step({
            0: ((Action.move, Move.down), None, None),
        })

        assert h.env.players[0].pos == (0, 0)
        assert h.env.gettile((0, 0)).player.id == 0

    def test_conflict(self):
        h = Helper()
        h.init_pos({
            0: (16, 13),
            1: (16, 15),
        })
        h.reset()

        h.step({
            0: ((Action.move, Move.up), None, None),
            1: ((Action.move, Move.down), None, None),
        })

        assert h.get_error_log() == ''
        assert h.env.gettile((16, 14)).player.id in [0, 1]
        assert h.env.players[0].pos in [(16, 13), (16, 14)]
        assert h.env.players[1].pos in [(16, 14), (16, 15)]


class TestTrade:

    def test_transaction_graph(self):
        h = Helper()
        h.init_pos({
            0: (8, 8),
            1: (8, 9),
        })
        h.reset()
        h.env.players[0].backpack.gold.num = 5
        h.env.players[1].backpack.sand.num = 10
        h.step({
            0: ((Action.idle, None), (Item.gold, -5), (Item.sand, 10)),
            1: ((Action.idle, None), (Item.sand, -10), (Item.gold, 5)),
        })

        transaction_graph = h.info['transaction_graph']
        assert transaction_graph[(0, 1)] == (Item.gold, 5)
        assert transaction_graph[(1, 0)] == (Item.sand, 10)
        assert h.env.players[0].backpack.sand.num == 10
        assert h.env.players[1].backpack.gold.num == 5
        assert h.env.players[0].backpack.gold.num == 0
        assert h.env.players[1].backpack.sand.num == 0
        assert len(transaction_graph) == 2

    def test_main_action_partial_fail(self):
        # trader 和 env 关于action的验证不一致，导致交易和step里面的action_valid不一致
        h = Helper()
        h.init_pos({
            0: (8, 8),
            1: (8, 9),
        })
        h.reset()
        h.env.players[0].backpack.gold.num = 10
        h.env.players[1].backpack.sand.num = 10
        h.step({
            0: ((Action.idle, None), (Item.gold, -10), (Item.sand, 10)),
            1: ((Action.collect, None), (Item.sand, -10), (Item.gold, 10)),
        })

        assert h.env.players[0].backpack.sand.num == 10
        assert h.env.players[1].backpack.gold.num == 10
        assert h.get_error_log() == ''


class TestHealth:

    def test_decrease(self):
        h = Helper()
        h.reset()
        D = PlayerConfig.comsumption_per_step
        init_health = [1, D, D + 1]
        actions = {}
        for i in range(3):
            h.env.players[i].health = init_health[i]
            h.env.players[i + 3].health = init_health[i]
            h.env.players[i + 3].backpack.pineapple.num = ITEMS.pineapple.consume_num
            actions[i + 3] = ((Action.consume, Item.pineapple), None, None)

        h.step(actions)

        E = ITEMS.pineapple.consume_num * ITEMS.pineapple.supply
        for i in range(3):
            assert h.env.players[i].health == max(init_health[i] - D, 0)
            assert h.env.players[i + 3].health == min(init_health[i] + E, PlayerConfig.max_health) - D
            assert h.env.reward_parser.last_costs[i] > h.env.reward_parser.last_costs[i + 3] or (i == 2)
        assert h.get_error_log() == ''


class TestItemRefresh:

    def test(self):
        h = Helper()
        P = ITEMS.gold.harvest_num
        h.init_tiles({
            (0, 0): (Item.peanut, P),
        })
        h.init_pos({
            0: (0, 0),
        })
        h.reset()

        for i in range(ITEMS.peanut.collect_time):
            assert h.get_tile_item((0, 0)) == (Item.peanut, P)
            assert h.env.gettile((0, 0)).item.refresh_remain is None
            h.step({
                0: ((Action.collect, None), None, None),
            })
        for i in reversed(range(ITEMS.peanut.refresh_time)):
            assert h.get_tile_item((0, 0)) == (Item.peanut, 0)
            assert h.env.gettile((0, 0)).item.refresh_remain == i
            h.step({})

        assert h.get_tile_item((0, 0)) == (Item.peanut, ITEMS.peanut.reserve_num)
        assert h.env.gettile((0, 0)).item.refresh_remain is None
