from helper import ITEMS, Action, Helper, Item, Move

from ecoevo.config import EnvConfig, MapConfig, PlayerConfig


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
        h.set_bag(0, {Item.stone: 1})
        h.set_bag(1, {Item.gold: G})

        h.step({
            0: ((Action.collect, None), (Item.stone, -1), (Item.gold, G)),
            1: ((Action.idle, None), (Item.gold, -G), (Item.stone, 1)),
        })

        assert h.get_tile_item((0, 0)) == (Item.coral, 1)
        assert h.get_bag(0) == {Item.gold: G}
        assert h.get_bag(1) == {Item.stone: 1}
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
        assert h.get_error_log() == ''
        assert 'towards map boarder' in h.get_warning_log()
        assert 'hit player' not in h.get_warning_log()

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


class TestConsume:

    def test_stomach_accumulate(self):
        assert not ITEMS.gold.disposable
        assert ITEMS.peanut.disposable
        h = Helper()
        h.reset()
        G = 5
        P = 3
        PC = ITEMS.peanut.consume_num
        h.set_bag(0, {Item.gold: G})
        h.set_bag(1, {Item.peanut: P * PC})

        STEP = 4
        for i in range(1, STEP + 1):
            h.step({
                0: ((Action.consume, Item.gold), None, None),
                1: ((Action.consume, Item.peanut), None, None),
            })
            assert h.get_stomach(0) == {Item.gold: i * G}
            assert h.get_stomach(1) == {Item.peanut: min(i, P) * PC}
            assert h.get_bag(0) == {Item.gold: G}
            pn = max(P - i, 0) * PC
            assert h.get_bag(1) == ({Item.peanut: pn} if pn else {})


class TestTrade:

    def test_transaction_graph(self):
        h = Helper()
        h.init_pos({
            0: (8, 8),
            1: (8, 9),
        })
        h.reset()
        h.set_bag(0, {Item.gold: 5})
        h.set_bag(1, {Item.sand: 10})
        h.step({
            0: ((Action.idle, None), (Item.gold, -5), (Item.sand, 10)),
            1: ((Action.idle, None), (Item.sand, -10), (Item.gold, 5)),
        })

        transaction_graph = h.info['transaction_graph']
        assert transaction_graph[(0, 1)] == (Item.gold, 5)
        assert transaction_graph[(1, 0)] == (Item.sand, 10)
        assert h.get_bag(0) == {Item.sand: 10}
        assert h.get_bag(1) == {Item.gold: 5}
        assert len(transaction_graph) == 2

    def test_main_action_partial_fail(self):
        # trader 和 env 关于action的验证不一致，导致交易和step里面的action_valid不一致
        h = Helper()
        h.init_pos({
            0: (8, 8),
            1: (8, 9),
        })
        h.reset()
        h.set_bag(0, {Item.gold: 10})
        h.set_bag(1, {Item.sand: 10})
        h.step({
            0: ((Action.idle, None), (Item.gold, -10), (Item.sand, 10)),
            1: ((Action.collect, None), (Item.sand, -10), (Item.gold, 10)),
        })

        assert h.get_bag(0) == {Item.sand: 10}
        assert h.get_bag(1) == {Item.gold: 10}
        assert h.get_error_log() == ''

    def test_illegal_sell_amount_0(self):
        h = Helper()
        h.init_pos({
            0: (8, 8),
            1: (8, 9),
        })
        h.reset()
        h.set_bag(0, {Item.gold: 5})
        h.set_bag(1, {Item.sand: 10})
        h.step({
            0: ((Action.idle, None), (Item.gold, 0), (Item.sand, 10)),
            1: ((Action.idle, None), (Item.sand, -10), (Item.gold, 5)),
        })

        assert h.get_bag(0) == {Item.gold: 5}
        assert h.get_bag(1) == {Item.sand: 10}

    def test_illegal_sell_amount_1(self):
        h = Helper()
        h.init_pos({
            0: (8, 8),
            1: (8, 9),
        })
        h.reset()
        h.set_bag(0, {Item.gold: 5})
        h.set_bag(1, {Item.sand: 10})
        h.step({
            0: ((Action.idle, None), (Item.gold, 1), (Item.sand, 10)),
            1: ((Action.idle, None), (Item.sand, -10), (Item.gold, 5)),
        })

        assert h.get_bag(0) == {Item.gold: 5}
        assert h.get_bag(1) == {Item.sand: 10}

    def test_illegal_buy_amount_0(self):
        h = Helper()
        h.init_pos({
            0: (8, 8),
            1: (8, 9),
        })
        h.reset()
        h.set_bag(0, {Item.gold: 5})
        h.set_bag(1, {Item.sand: 10})
        h.step({
            0: ((Action.idle, None), (Item.gold, -5), (Item.sand, 0)),
            1: ((Action.idle, None), (Item.sand, -10), (Item.gold, 5)),
        })

        assert h.get_bag(0) == {Item.gold: 5}
        assert h.get_bag(1) == {Item.sand: 10}

    def test_illegal_buy_amount_neg1(self):
        h = Helper()
        h.init_pos({
            0: (8, 8),
            1: (8, 9),
        })
        h.reset()
        h.set_bag(0, {Item.gold: 5})
        h.set_bag(1, {Item.sand: 10})
        h.step({
            0: ((Action.idle, None), (Item.gold, -5), (Item.sand, -1)),
            1: ((Action.idle, None), (Item.sand, -10), (Item.gold, 5)),
        })

        assert h.get_bag(0) == {Item.gold: 5}
        assert h.get_bag(1) == {Item.sand: 10}


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

    def test_refresh_collect_loop(self):
        h = Helper()
        P = ITEMS.peanut.harvest_num
        h.init_tiles({
            (0, 0): (Item.peanut, P),
        })
        h.init_pos({
            0: (0, 0),
        })
        h.reset()

        LOOP = 3
        for loop in range(LOOP):
            for i in range(ITEMS.peanut.collect_time):
                assert h.get_tile_item((0, 0)) == (Item.peanut, P)
                assert h.env.gettile((0, 0)).item.refresh_remain is None
                assert h.get_bag(0) == {Item.peanut: loop * P} or loop == 0 and h.get_bag(0) == {}
                h.step({
                    0: ((Action.collect, None), None, None),
                })
            for i in reversed(range(ITEMS.peanut.refresh_time)):
                assert h.get_tile_item((0, 0)) == (Item.peanut, 0)
                assert h.env.gettile((0, 0)).item.refresh_remain == i
                assert h.get_bag(0) == {Item.peanut: (loop + 1) * P}
                h.step({})
        assert h.get_tile_item((0, 0)) == (Item.peanut, ITEMS.peanut.reserve_num)
        assert h.env.gettile((0, 0)).item.refresh_remain is None
        assert h.get_bag(0) == {Item.peanut: LOOP * P}


class TestMap:

    def test_fix_map(self):
        h = Helper()
        h.reset()
        m1 = h.get_map_items()
        h.reset()
        m2 = h.get_map_items()

        assert m1 == m2
        assert h.get_error_log() == ''

    def test_random_map_difference(self):
        h = Helper()
        h.cfg.random_generate_map = True
        h.reset()
        m1 = h.get_map_items()
        h.reset()
        m2 = h.get_map_items()

        assert m1 != m2
        assert h.get_error_log() == ''

    def test_random_map_resource_num(self):
        h = Helper()
        h.cfg.random_generate_map = True

        for loop in range(5):
            h.reset()
            count = {item: 0 for item in ITEMS.dict()}
            for _, (item, num) in h.get_map_items().items():
                if item != 'empty':
                    assert num == ITEMS[item].reserve_num
                    count[item] += 1
            assert count == {item: MapConfig.generate_num_block_resource for item in ITEMS.dict()}

        assert h.get_error_log() == ''


class TestObs:

    def test_rel_pos_coord_max(self):
        # env的get_obs里的MapSize.width和MapSize.height应该减一
        X, Y = MapConfig.width, MapConfig.height
        V = EnvConfig.visual_radius
        h = Helper()
        h.init_pos({
            0: (X - 1, Y - 1),
            1: (X - 1, Y - 2),
            2: (X - 2, Y - 1),
        })
        # - - -
        # 2 0 |
        #   1 |
        h.reset()
        assert h.obs[0][(V, V)].player.id == 0
        assert h.obs[0][(V, V - 1)].player.id == 1
        assert h.obs[0][(V - 1, V)].player.id == 2
        assert h.obs[1][(V, V + 1)].player.id == 0
        assert h.obs[1][(V, V)].player.id == 1
        assert h.obs[1][(V - 1, V + 1)].player.id == 2
        assert h.obs[2][(V + 1, V)].player.id == 0
        assert h.obs[2][(V + 1, V - 1)].player.id == 1
        assert h.obs[2][(V, V)].player.id == 2
