from helper import ITEMS, Action, Helper, Item, Move

from ecoevo.config import EnvConfig, MapConfig, PlayerConfig, RewardConfig


class TestEnvBasic:

    def test_step_and_done(self):
        STEP = 3
        h = Helper()
        h.cfg.total_step = STEP
        h.reset()

        for step in range(STEP):
            assert step == 0 or h.done == False
            assert h.gamecore.curr_step == step
            h.step({})

        assert h.done == True
        assert h.gamecore.curr_step == STEP


class TestCollect:

    def test_success(self):
        h = Helper()
        h.init_pos({0: (8, 8)})
        G = ITEMS.gold.harvest_num + 1
        h.init_tiles({
            (8, 8): (Item.gold, G),
        })
        h.reset()

        for _ in range(h.gamecore.players[0].ability[Item.gold]):
            assert h.get_tile_item((8, 8)) == (Item.gold, G)
            h.step({
                0: ((Action.collect, None), None, None, None),
            })

        assert h.get_tile_item((8, 8)) == (Item.gold, 1)
        assert h.get_error_log() == ''
        assert h.gamecore.players[0].collect_remain == 0

    def test_exceed_volumn_after_trade(self):
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
            0: ((Action.idle, None), ((Item.stone, -1), (Item.gold, G)), None, None),
            1: ((Action.idle, None), None, None, None),
        })
        h.step({
            0: ((Action.collect, None), None, None, None),
            1: ((Action.idle, None), None, (0, 0), None),
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
            0: ((Action.move, Move.down), None, None, None),
        })

        assert h.gamecore.players[0].pos == (0, 0)
        assert h.get_tile_player((0, 0)).id == 0
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
            0: ((Action.move, Move.up), None, None, None),
            1: ((Action.move, Move.down), None, None, None),
        })

        assert h.get_error_log() == ''
        assert h.get_tile_player((16, 14)).id in [0, 1]
        assert h.gamecore.players[0].pos in [(16, 13), (16, 14)]
        assert h.gamecore.players[1].pos in [(16, 14), (16, 15)]


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
                0: ((Action.consume, Item.gold), None, None, None),
                1: ((Action.consume, Item.peanut), None, None, None),
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
            0: ((Action.idle, None), ((Item.gold, -5), (Item.sand, 10)), None, None),
            1: ((Action.idle, None), None, None, None),
        })
        h.step({
            0: ((Action.idle, None), None, None, None),
            1: ((Action.idle, None), None, (0, 0), None),
        })

        transaction_graph = h.info['transaction_graph']
        assert transaction_graph[(0, 1)] == (Item.gold, 5)
        assert transaction_graph[(1, 0)] == (Item.sand, 10)
        assert h.get_bag(0) == {Item.sand: 10}
        assert h.get_bag(1) == {Item.gold: 5}
        assert len(transaction_graph) == 2

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
            0: ((Action.idle, None), ((Item.gold, 0), (Item.sand, 10)), None, None),
            1: ((Action.idle, None), ((Item.sand, -10), (Item.gold, 5)), None, None),
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
            0: ((Action.idle, None), ((Item.gold, 1), (Item.sand, 10)), None, None),
            1: ((Action.idle, None), ((Item.sand, -10), (Item.gold, 5)), None, None),
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
            0: ((Action.idle, None), ((Item.gold, -5), (Item.sand, 0)), None, None),
            1: ((Action.idle, None), ((Item.sand, -10), (Item.gold, 5)), None, None),
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
            0: ((Action.idle, None), ((Item.gold, -5), (Item.sand, -1)), None, None),
            1: ((Action.idle, None), ((Item.sand, -10), (Item.gold, 5)), None, None),
        })

        assert h.get_bag(0) == {Item.gold: 5}
        assert h.get_bag(1) == {Item.sand: 10}

class TestOffer:
    def test_lock_and_unlock_item(self):
        h = Helper()
        h.reset()
        h.set_bag(0, {Item.gold: 4})
        h.set_bag(1, {Item.gold: 5})
        h.set_bag(2, {Item.gold: 6})
        h.step({
            0: ((Action.idle, None), ((Item.gold, -5), (Item.sand, 1)), None, None),
            1: ((Action.idle, None), ((Item.gold, -5), (Item.sand, 1)), None, None),
            2: ((Action.idle, None), ((Item.gold, -5), (Item.sand, 1)), None, None),
        })
        
        def num(id):
            item = h.get_player(id).backpack.gold
            return item.num, item.locked_num, item.free_num        
        assert len(h.get_player_offers(0)) == 0 and num(0) == (4, 0, 4)
        assert len(h.get_player_offers(1)) == 1 and num(1) == (5, 5, 0)
        assert len(h.get_player_offers(2)) == 1 and num(2) == (6, 5, 1)
        assert h.get_error_log() == ''

        h.step({
            1: ((Action.idle, None), None, None, 0),
            2: ((Action.idle, None), None, None, 0),
        })
        assert len(h.get_player_offers(0)) == 0 and num(0) == (4, 0, 4)
        assert len(h.get_player_offers(1)) == 0 and num(1) == (5, 0, 5)
        assert len(h.get_player_offers(2)) == 0 and num(2) == (6, 0, 6)
        assert h.get_error_log() == ''

    def test_lock_and_unlock_volume(self):
        h = Helper()
        assert ITEMS.gold.capacity == 1
        S = PlayerConfig.bag_volume
        h.reset()
        h.set_bag(0, {Item.gold: S-1})
        h.set_bag(1, {Item.gold: S-1})
        h.set_bag(2, {Item.gold: S-1})
        h.set_bag(3, {Item.gold: S-1})
        h.step({
            0: ((Action.idle, None), ((Item.gold, -2), (Item.sand, 1)), None, None),
            1: ((Action.idle, None), ((Item.gold, -2), (Item.sand, 2)), None, None),
            2: ((Action.idle, None), ((Item.gold, -2), (Item.sand, 3)), None, None),
            3: ((Action.idle, None), ((Item.gold, -2), (Item.sand, 4)), None, None),
        })
        
        def volnum(id):
            bag = h.get_player(id).backpack
            return bag.used_volume, bag.locked_volume, bag.remain_volume
        
        assert len(h.get_player_offers(0)) == 1 and volnum(0) == (S-1, 0, 1)
        assert len(h.get_player_offers(1)) == 1 and volnum(1) == (S-1, 0, 1)
        assert len(h.get_player_offers(2)) == 1 and volnum(2) == (S-1, 1, 0)
        assert len(h.get_player_offers(3)) == 0 and volnum(3) == (S-1, 0, 1)
        assert h.get_error_log() == ''

        h.step({
            0: ((Action.idle, None), None, None, 0),
            1: ((Action.idle, None), None, None, 0),
            2: ((Action.idle, None), None, None, 0),
        })
        assert len(h.get_player_offers(0)) == 0 and volnum(0) == (S-1, 0, 1)
        assert len(h.get_player_offers(1)) == 0 and volnum(1) == (S-1, 0, 1)
        assert len(h.get_player_offers(2)) == 0 and volnum(1) == (S-1, 0, 1)
        assert len(h.get_player_offers(3)) == 0 and volnum(1) == (S-1, 0, 1)
        assert h.get_error_log() == ''  

    def test_lock_item_consume(self):
        h = Helper()
        h.reset()
        h.set_bag(0, {Item.gold: 8})
        h.set_bag(1, {Item.peanut: 8})
        h.step({
            0: ((Action.consume, Item.gold), ((Item.gold, -5), (Item.sand, 1)), None, None),
            1: ((Action.consume, Item.peanut), ((Item.peanut, -5), (Item.sand, 1)), None, None),
        })
        assert h.get_bag(0) == {Item.gold: 8}
        assert h.get_player(0).stomach.gold.num == 3
        assert h.get_bag(1) == {Item.peanut: 5}
        assert h.get_player(1).stomach.peanut.num == 3
        
    def test_lock_item_submit(self):
        h = Helper()
        h.reset()
        h.set_bag(0, {Item.gold: 8})
        h.set_bag(1, {Item.gold: 10})
        for i in range(2):
            h.step({
                0: ((Action.idle, None), ((Item.gold, -5), (Item.sand, 1)), None, None),
                1: ((Action.idle, None), ((Item.gold, -5), (Item.sand, 1)), None, None),
            })
        assert h.get_player(0).backpack.gold.free_num == 3
        assert h.get_player(1).backpack.gold.free_num == 0
    
    def test_lock_item_accept(self):
        h = Helper()
        h.init_pos({})
        h.reset()
        h.set_bag(0, {Item.gold: 8})
        h.set_bag(1, {Item.sand: 8})
        h.step({
            0: ((Action.idle, None), ((Item.gold, -5), (Item.sand, 1)), None, None),
            1: ((Action.idle, None), ((Item.sand, -1), (Item.gold, 5)), None, None),
        })
        h.step({
            0: ((Action.idle, None), None, (1, 0), None),
        })
        assert h.get_bag(0) == {Item.gold: 8} and h.get_bag(1) == {Item.sand: 8}
        h.step({
            1: ((Action.idle, None), None, (0, 0), None),
        })
        assert h.get_bag(0) == {Item.gold: 3, Item.sand: 1} and h.get_bag(1) == {Item.sand: 7, Item.gold: 5}
        
    def test_lock_volume_collect(self):
        h = Helper()
        assert ITEMS.gold.capacity == 1
        S = PlayerConfig.bag_volume
        h.init_tiles({
            (0, 0): (Item.sand, ITEMS.sand.harvest_num),
            (0, 1): (Item.sand, ITEMS.sand.harvest_num),
        })
        h.init_pos({
            0: (0, 0),
            1: (0, 1),
        })
        h.reset()
        h.set_bag(0, {Item.gold: 1})
        h.set_bag(1, {Item.gold: 1})
        h.step({
            0: ((Action.collect, None), ((Item.gold, -1), (Item.sand, S)), None, None),
            1: ((Action.collect, None), ((Item.gold, -1), (Item.sand, 2)), None, None),
        })
        assert h.get_bag(0) == {Item.gold: 1}
        assert h.get_bag(1) == {Item.gold: 1, Item.sand: ITEMS.sand.harvest_num}
        
    def test_lock_volume_submit(self):
        S = PlayerConfig.bag_volume
        h = Helper()
        h.reset()
        h.set_bag(0, {Item.gold: 2})
        h.set_bag(1, {Item.gold: 2})
        h.step({
            0: ((Action.idle, None), ((Item.gold, -1), (Item.sand, S)), None, None),
            1: ((Action.idle, None), ((Item.gold, -1), (Item.sand, 2)), None, None),
        })
        h.step({
            0: ((Action.idle, None), ((Item.gold, -1), (Item.sand, 1)), None, None),
            1: ((Action.idle, None), ((Item.gold, -1), (Item.sand, 1)), None, None),
        })
        assert len(h.get_player_offers(0)) == 1
        assert len(h.get_player_offers(1)) == 2
            
    def test_lock_volume_accept(self):
        S = PlayerConfig.bag_volume
        h = Helper()
        h.init_pos({})
        h.reset()
        h.set_bag(0, {Item.gold: 2})
        h.set_bag(1, {Item.gold: 2})
        h.set_bag(2, {Item.sand: 2})
        h.step({
            0: ((Action.idle, None), ((Item.gold, -1), (Item.sand, S-1)), None, None),
            1: ((Action.idle, None), ((Item.gold, -1), (Item.sand, 1)), None, None),
            2: ((Action.idle, None), ((Item.sand, -2), (Item.gold, 1)), None, None),
        })
        assert len(h.get_player_offers(0)) == 1 and h.get_player(0).backpack.remain_volume == 0
        assert len(h.get_player_offers(1)) == 1
        assert len(h.get_player_offers(2)) == 1

        # should fail
        h.step({
            0: ((Action.idle, None), None, (2, 0), None),
        })
        assert h.get_bag(0) == {Item.gold: 2} and h.get_bag(2) == {Item.sand: 2}

        # should success
        h.step({
            1: ((Action.idle, None), None, (2, 0), None),
        })
        assert h.get_bag(1) == {Item.gold: 1, Item.sand: 2} and h.get_bag(2) == {Item.gold: 1}
        
    
class TestHealth:

    def test_decrease(self):
        h = Helper()
        h.reset()
        D = PlayerConfig.comsumption_per_step
        init_health = [1, D, D + 1]
        actions = {}
        for i in range(3):
            h.gamecore.players[i].health = init_health[i]
            h.gamecore.players[i + 3].health = init_health[i]
            h.gamecore.players[i + 3].backpack.pineapple.num = ITEMS.pineapple.consume_num
            actions[i + 3] = ((Action.consume, Item.pineapple), None, None, None)

        h.step(actions)

        E = ITEMS.pineapple.consume_num * ITEMS.pineapple.supply
        for i in range(3):
            assert h.gamecore.players[i].health == max(init_health[i] - D, 0)
            assert h.gamecore.players[i + 3].health == min(init_health[i] + E, PlayerConfig.max_health) - D
            assert h.gamecore.reward_parser.last_costs[i] > h.gamecore.reward_parser.last_costs[i + 3] or (i == 2) or (
                RewardConfig.penalty == 0)
        assert h.get_error_log() == ''

class TestItemRefresh:

    def test_refresh_collect_loop(self):
        h = Helper()
        P = ITEMS.pineapple.harvest_num
        h.init_tiles({
            (0, 0): (Item.pineapple, P),
        })
        h.init_pos({
            0: (0, 0),
        })
        h.reset()
        
        def get_refresh_remain(pos):
            return h.gamecore.entity_manager.map.get(pos).item.refresh_remain
        
        COLLECT_TIME = h.get_tile_player((0, 0)).ability['pineapple']

        LOOP = 3
        for loop in range(LOOP):
            h.set_bag(0, {})
            for i in range(COLLECT_TIME):
                assert h.get_tile_item((0, 0)) == (Item.pineapple, P)
                assert get_refresh_remain((0, 0)) == 0
                assert h.get_bag(0) == {}
                h.step({
                    0: ((Action.collect, None), None, None, None),
                })
            for i in reversed(range(1, ITEMS.pineapple.refresh_time)):
                assert h.get_tile_item((0, 0)) == (Item.pineapple, 0)
                assert get_refresh_remain((0, 0)) == i
                assert h.get_bag(0) == {Item.pineapple: P}
                h.step({})
        assert h.get_tile_item((0, 0)) == (Item.pineapple, ITEMS.pineapple.reserve_num)
        assert get_refresh_remain((0, 0)) == 0


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
        # gamecore的get_obs里的MapSize.width和MapSize.height应该减一
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


class TestInfo:

    def test_trade_time_and_amount_per_item(self):
        LIST = list(ITEMS.dict().keys())
        CYCLE = 3
        STEP = len(LIST) * CYCLE * 2
        AMOUNT = [i + 1 for i in range(len(LIST))]

        h = Helper()
        h.cfg.total_step = STEP
        h.init_pos({
            0: (0, 0),
            1: (0, 1),
        })
        h.reset()

        for step in range(STEP):
            if  step % 2 == 0:
                case = step // 2
                index = [case % len(LIST), (case + 1) % len(LIST)]
                items = [LIST[i] for i in index]
                nums = [AMOUNT[i] for i in index]
                for i in range(2):
                    h.set_bag(i, {items[i]: nums[i]})
                h.step({
                    0: ((Action.idle, None), ((items[0], -nums[0]), (items[1], nums[1])), None, None),
                    1: ((Action.idle, None), None, None, None),
                })
            else:
                h.step({
                    0: ((Action.idle, None), None, None, None),
                    1: ((Action.idle, None), None, (0, 0), None),
                })
                

        assert h.info['trade_times'] == STEP // 2 / h.gamecore.num_player
        for item, amount in zip(LIST, AMOUNT):
            assert h.info[item + '_trade_times'] == CYCLE * 2 / h.gamecore.num_player
            assert h.info[item + '_trade_amount'] == CYCLE * 2 * amount / h.gamecore.num_player
    
    def test_utility(self):
        import warnings
        warnings.warn('test_utility skipped')
        return

        import math
        STEP = 2
        CONSUME = {
            0: [Item.gold] * 2,
            1: [Item.pineapple] * 2,
            2: [Item.gold, Item.pineapple],
        }
        PC = ITEMS.pineapple.consume_num
        G = 100
        P = PC * 2

        h = Helper()
        h.cfg.total_step = STEP
        h.reset()

        for i in range(3):
            h.set_bag(i, {Item.gold: G, Item.pineapple: P})

        for step in range(STEP):
            h.step({id: ((Action.consume, CONSUME[id][step]), None, None) for id in range(3)})

        utilities = h.gamecore.reward_parser.last_utilities
        assert utilities[0] == math.log(G * 2 * ITEMS.gold.capacity / 10 + 1)
        assert utilities[1] == math.log(P * ITEMS.pineapple.capacity / 10 + 1) * 2
        assert utilities[2] == math.log(G * ITEMS.gold.capacity / 10 +
                                        1) + math.log(PC * ITEMS.pineapple.capacity / 10 + 1) * 2
        assert h.info['final_avr_utility'] == sum(utilities.values()) / h.gamecore.num_player
        assert h.info['final_max_utility'] == max(utilities.values())
        assert h.info['final_min_utility'] == min(utilities.values())
