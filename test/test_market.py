from ecoevo import EcoEvo
from ecoevo.config import PlayerConfig

from helper import Helper, Item, Action, ITEMS

class TestAcceptOffer:

    def test_none(self):
        h = Helper()
        h.init_pos({0: (0, 0), 1: (0, 1)})
        h.reset()

        h.step({0: ((Action.idle, None), None, None, None)})
        assert h.get_error_log().find(" ") < 0

    def test_empty(self):
        h = Helper()
        h.init_pos({0: (0, 0), 1: (0, 1)})
        h.reset()

        h.step({0: ((Action.idle, None), None, (0, 0), None)})
        assert h.get_error_log().find("Offer does not exist") >= 0

    def test_distance(self):
        h = Helper()
        h.init_pos({0: (16, 16), 1: (16, 24), 2: (24, 16), 3: (16, 8), 4: (8, 16), 5: (16, 9)})
        h.reset()

        # submit an offer
        h.set_bag(0, {Item.stone: 1})
        h.set_bag(1, {Item.gold: 1})
        h.set_bag(2, {Item.gold: 1})
        h.set_bag(3, {Item.gold: 1})
        h.set_bag(4, {Item.gold: 1})
        h.set_bag(5, {Item.gold: 1})
        h.step({0: ((Action.idle, None), ((Item.stone, -1), (Item.gold, 1)), None, None)})

        # false cases
        h.step({1: ((Action.idle, None), None, (0, 0), None)})
        idx_error = h.get_error_log().find("Offer player too far to trade")
        assert idx_error >= 0
        h.step({2: ((Action.idle, None), None, (0, 0), None)})
        idx_error = h.get_error_log().find("Offer player too far to trade",
                                           idx_error + len("Offer player too far to trade"))
        assert idx_error >= 0
        h.step({3: ((Action.idle, None), None, (0, 0), None)})
        idx_error = h.get_error_log().find("Offer player too far to trade",
                                           idx_error + len("Offer player too far to trade"))
        assert idx_error >= 0
        h.step({4: ((Action.idle, None), None, (0, 0), None)})
        idx_error = h.get_error_log().find("Offer player too far to trade",
                                           idx_error + len("Offer player too far to trade"))
        assert idx_error >= 0

        # true case
        h.step({5: ((Action.idle, None), None, (0, 0), None)})
        idx_error = h.get_error_log().find("Offer player too far to trade",
                                           idx_error + len("Offer player too far to trade"))
        assert idx_error < 0

    def test_num_volume(self):
        h = Helper()
        h.init_pos({0: (0, 0), 1: (0, 1), 2: (1, 0), 3: (1, 1)})
        h.reset()

        # submit an offer
        h.set_bag(0, {Item.stone: 1})
        h.set_bag(
            2, {
                Item.gold:
                1,
                Item.peanut:
                round(PlayerConfig.bag_volume - ITEMS.gold.capacity / ITEMS.peanut.capacity)
            })
        h.set_bag(3, {Item.gold: 1})
        h.step({0: ((Action.idle, None), ((Item.stone, -1), (Item.gold, 1)), None, None)})

        # false case
        h.step({1: ((Action.idle, None), None, (0, 0), None)})
        assert h.get_warning_log().find("free num not enough") >= 0
        h.step({2: ((Action.idle, None), None, (0, 0), None)})
        idx_error = h.get_warning_log().find("remain volume not enough")
        assert idx_error >= 0

        # true case
        h.step({3: ((Action.idle, None), None, (0, 0), None)})
        idx_error = h.get_warning_log().find("not enough", idx_error + len("remain volume not enough"))
        assert idx_error < 0

    def test_result(self):
        h = Helper()
        h.init_pos({0: (0, 0), 1: (0, 10), 2: (1, 0)})
        h.reset()

        # submit an offer
        h.set_bag(0, {Item.gold: 1})
        h.set_bag(1, {Item.stone: 1})
        h.set_bag(2, {Item.stone: 1})
        h.step({0: ((Action.idle, None), ((Item.gold, -1), (Item.stone, 1)), None, None)})

        # offer failed case
        h.step({1: ((Action.idle, None), None, (0, 0), None)})
        assert h.get_player(1).backpack.gold.num == 0 and h.get_player(1).backpack.stone.num == 1
        assert h.get_player(0).backpack.gold.num == 1 and h.get_player(0).backpack.stone.num == 0
        assert h.get_player(0).backpack.gold.free_num == 0 and h.get_player(0).backpack.gold.locked_num == 1
        assert h.get_player(
            0).backpack.locked_volume == ITEMS.stone.capacity - ITEMS.gold.capacity
        assert h.info['transaction_graph'] == {}

        # offer success case
        h.step({2: ((Action.idle, None), None, (0, 0), None)})
        assert h.get_player(2).backpack.gold.num == 1 and h.get_player(2).backpack.stone.num == 0
        assert h.get_player(0).backpack.gold.num == 0 and h.get_player(0).backpack.stone.num == 1
        assert h.get_player(0).backpack.gold.free_num == 0 and h.get_player(0).backpack.gold.locked_num == 0
        assert h.get_player(0).backpack.locked_volume == 0
        assert h.info['transaction_graph'] == {(0, 2): ('gold', 1), (2, 0): ('stone', 1)}

    def test_random_chain(self):

        def accept_chain():
            h = Helper()
            h.init_pos({0: (0, 0), 1: (0, 1), 2: (1, 0)})
            h.reset()

            # submit offers
            h.set_bag(0, {Item.gold: 1})
            h.set_bag(1, {Item.stone: 1})
            h.set_bag(2, {Item.coral: 1})
            h.step({
                1: ((Action.idle, None), ((Item.stone, -1), (Item.gold, 1)), None, None),
                2: ((Action.idle, None), ((Item.coral, -1), (Item.gold, 1)), None, None)
            })

            # trade
            h.step({0: ((Action.idle, None), None, (1, 0), None), 1: ((Action.idle, None), None, (2, 0), None)})

            return True if h.get_player(1).backpack.coral.num == 1 else False

        list_success = [accept_chain() for _ in range(10)]
        assert True in list_success and False in list_success

    def test_random_twice(self):

        def accept_twice():
            h = Helper()
            h.init_pos({0: (0, 0), 1: (0, 1), 2: (1, 0)})
            h.reset()

            # submit an offer
            h.set_bag(0, {Item.gold: 1})
            h.set_bag(1, {Item.stone: 1})
            h.set_bag(2, {Item.stone: 1})
            h.step({0: ((Action.idle, None), ((Item.gold, -1), (Item.stone, 1)), None, None)})

            # trade
            h.step({1: ((Action.idle, None), None, (0, 0), None), 2: ((Action.idle, None), None, (0, 0), None)})

            return 1 if h.get_player(1).backpack.gold.num == 1 else 2 if h.get_player(2).backpack.gold.num == 1 else 0

        list_pid_success = [accept_twice() for _ in range(10)]
        assert 1 in list_pid_success and 2 in list_pid_success and 0 not in list_pid_success


class TestCancelOffer:

    def test_none(self):
        h = Helper()
        h.init_pos({0: (0, 0)})
        h.reset()

        # cancel an empty offer
        h.step({0: ((Action.idle, None), None, None, None)})
        assert h.get_info_log().find(" ") < 0

    def test_empty(self):
        h = Helper()
        h.init_pos({0: (0, 0)})
        h.reset()

        # cancel an empty offer
        h.step({0: ((Action.idle, None), None, None, 0)})
        assert h.get_info_log().find("try cancel empty offer") >= 0

    def test_success(self):
        h = Helper()
        h.init_pos({0: (0, 0)})
        h.reset()
        h.set_bag(0, {Item.stone: PlayerConfig.max_offer})

        # submit offers
        for _ in range(PlayerConfig.max_offer):
            h.step({0: ((Action.idle, None), ((Item.stone, -1), (Item.gold, 1)), None, None)})
        offers = h.get_player(0).offers
        offers_std = [(('stone', -1), ('gold', 1)) for _ in range(PlayerConfig.max_offer)]
        assert offers == offers_std

        # cancel offers
        for i in range(PlayerConfig.max_offer):
            h.step({0: ((Action.idle, None), None, None, i)})
        offers = h.get_player(0).offers
        offers_std = [None for _ in range(PlayerConfig.max_offer)]
        assert offers == offers_std


class TestSubmitOffer:
    def test_submit_none(self):
        h = Helper()
        h.reset()
        h.set_bag(0, {Item.gold: 1})
        h.set_bag(1, {Item.gold: 1})
        
        h.step({
            0: ((Action.idle, None), ((Item.gold, -1), (Item.sand, 1)), None, None),
            1: ((Action.idle, None), None, None, None),
        })
        
        assert h.get_player_offers(0) == [((Item.gold, -1), (Item.sand, 1))]
        assert h.get_player_offers(1) == []
        assert h.get_error_log() == ''
    
    def test_basic_check(self):
        h = Helper()
        h.reset()
        for i in range(6):
            h.set_bag(i, {Item.gold: 1})
        h.step({
            0: ((Action.idle, None), ((Item.gold, -1), (Item.sand, 1)), None, None),
            1: ((Action.idle, None), ((Item.gold, -1), (Item.gold, -1)), None, None),
            2: ((Action.idle, None), ((Item.gold, 0), (Item.sand, 1)), None, None),
            3: ((Action.idle, None), ((Item.gold, 1), (Item.sand, 1)), None, None),
            4: ((Action.idle, None), ((Item.gold, -1), (Item.sand, 0)), None, None),
            5: ((Action.idle, None), ((Item.gold, -1), (Item.sand, -1)), None, None),
        })
        assert h.get_player_offers(0) == [((Item.gold, -1), (Item.sand, 1))]
        for i in range(1, 6):
            assert h.get_player_offers(i) == []
        assert h.get_error_log() == ''
    
    def test_item_num(self):
        h = Helper()
        h.reset()
        for i in range(3):
            h.set_bag(i, {Item.gold: 2})
        h.step({
            0: ((Action.idle, None), ((Item.gold, -1), (Item.sand, 1)), None, None),
            1: ((Action.idle, None), ((Item.gold, -2), (Item.sand, 1)), None, None),
            2: ((Action.idle, None), ((Item.gold, -3), (Item.sand, 1)), None, None),
        })
        assert h.get_player_offers(0) == [((Item.gold, -1), (Item.sand, 1))]
        assert h.get_player_offers(1) == [((Item.gold, -2), (Item.sand, 1))]
        assert h.get_player_offers(2) == []
        assert h.get_error_log() == ''
    
    def test_volume(self):
        S = PlayerConfig.bag_volume
        h = Helper()
        h.reset()
        h.set_bag(0, {Item.gold: S})
        h.set_bag(1, {Item.gold: S})
        h.set_bag(2, {Item.gold: S})
        h.step({
            0: ((Action.idle, None), ((Item.gold, -2), (Item.sand, 1)), None, None),
            1: ((Action.idle, None), ((Item.gold, -2), (Item.sand, 2)), None, None),
            2: ((Action.idle, None), ((Item.gold, -2), (Item.sand, 3)), None, None),
        })
        assert h.get_player_offers(0) == [((Item.gold, -2), (Item.sand, 1))]
        assert h.get_player_offers(1) == [((Item.gold, -2), (Item.sand, 2))]
        assert h.get_player_offers(2) == []
        assert h.get_error_log() == ''
    
    def test_max_offer(self):
        M = PlayerConfig.max_offer
        h = Helper()
        h.reset()
        h.set_bag(0, {Item.gold: M+10})
        for i in range(M):
            h.step({
                0: ((Action.idle, None), ((Item.gold, -1), (Item.sand, 1)), None, None),
            })
            if i < M:
                assert len(h.get_player_offers(0)) == i+1
                assert h.get_error_log() == ''
            else:
                assert len(h.get_player_offers(0)) == M
                assert h.get_error_log() != ''
    
    def test_lock_item(self):
        h = Helper()
        h.reset()
        h.set_bag(0, {Item.gold: 2})
        h.set_bag(1, {Item.gold: 1})

        h.step({
            0: ((Action.idle, None), ((Item.gold, -1), (Item.sand, 1)), None, None),
            1: ((Action.idle, None), ((Item.gold, -1), (Item.sand, 1)), None, None),
        })
        assert len(h.get_player_offers(0)) == 1
        assert len(h.get_player_offers(1)) == 1
        assert h.get_player(0).backpack.gold.locked_num == 1
        assert h.get_player(1).backpack.gold.locked_num == 1
        
        h.step({
            0: ((Action.idle, None), ((Item.gold, -1), (Item.sand, 1)), None, None),
            1: ((Action.idle, None), ((Item.gold, -1), (Item.sand, 1)), None, None),
        })
        assert len(h.get_player_offers(0)) == 2
        assert len(h.get_player_offers(1)) == 1
        assert h.get_player(0).backpack.gold.locked_num == 2
        assert h.get_player(1).backpack.gold.locked_num == 1
    
    def test_lock_volume(self):
        S = PlayerConfig.bag_volume
        h = Helper()
        h.reset()
        h.set_bag(0, {Item.gold: S-3})
        h.set_bag(1, {Item.gold: S-3})
        h.set_bag(2, {Item.gold: S-3})
        h.set_bag(3, {Item.gold: S-3})

        h.step({
            0: ((Action.idle, None), ((Item.gold, -2), (Item.sand, 1)), None, None),
            1: ((Action.idle, None), ((Item.gold, -2), (Item.sand, 2)), None, None),
            2: ((Action.idle, None), ((Item.gold, -2), (Item.sand, 3)), None, None),
            3: ((Action.idle, None), ((Item.gold, -2), (Item.sand, 3)), None, None),
        })
        assert len(h.get_player_offers(0)) == 1
        assert len(h.get_player_offers(1)) == 1
        assert len(h.get_player_offers(2)) == 1
        assert len(h.get_player_offers(3)) == 1
        assert h.get_player(0).backpack.locked_volume == 0
        assert h.get_player(1).backpack.locked_volume == 0
        assert h.get_player(2).backpack.locked_volume == 1
        assert h.get_player(3).backpack.locked_volume == 1
        
        h.step({
            0: ((Action.idle, None), ((Item.gold, -1), (Item.sand, 2)), None, None),
            1: ((Action.idle, None), ((Item.gold, -1), (Item.sand, 10)), None, None),
            2: ((Action.idle, None), ((Item.gold, -1), (Item.sand, 3)), None, None),
            3: ((Action.idle, None), ((Item.gold, -1), (Item.sand, 4)), None, None),
        })
        assert len(h.get_player_offers(0)) == 2
        assert len(h.get_player_offers(1)) == 1
        assert len(h.get_player_offers(2)) == 2
        assert len(h.get_player_offers(3)) == 1
        assert h.get_player(0).backpack.locked_volume == 1
        assert h.get_player(1).backpack.locked_volume == 0
        assert h.get_player(2).backpack.locked_volume == 3
        assert h.get_player(3).backpack.locked_volume == 1
        
        assert h.get_error_log() == ''
    
    def test_offers(self):
        M = PlayerConfig.max_offer
        h = Helper()
        h.reset()
        h.set_bag(0, {Item.gold: 1, Item.sand: 1})

        O = [
            ((Item.gold, -1), (Item.coral, 1)),
            ((Item.sand, -1), (Item.coral, 1)),
        ]
        h.step({
            0: ((Action.idle, None), O[0], None, None),
        })
        assert len(h.get_player(0).offers) == M
        assert h.get_player(0).offers[0] == O[0]
        assert h.get_player(0).offers.count(None) == M-1

        h.step({
            0: ((Action.idle, None), O[1], None, None),
        })
        assert len(h.get_player(0).offers) == M
        assert h.get_player(0).offers[0] == O[0]
        assert h.get_player(0).offers[1] == O[1]
        assert h.get_player(0).offers.count(None) == M-2


class TestComplex:
    def test_submit_and_accept(self):
        # accept prioritized
        h = Helper()
        h.init_pos({})
        h.reset()
        h.set_bag(0, {Item.gold: 1})
        h.set_bag(1, {Item.gold: 1})
        h.set_bag(2, {Item.sand: 1})
        h.set_bag(3, {Item.sand: 1})
        O_SG = (Item.sand, -1), (Item.gold, 1)
        O_GC = (Item.gold, -1), (Item.coral, 1)
        O_SC = (Item.sand, -1), (Item.coral, 1)
        
        h.step({
            2: ((Action.idle, None), O_SG, None, None),
            3: ((Action.idle, None), O_SG, None, None),
        })
        assert h.get_player_offers(2) == [O_SG]
        assert h.get_player_offers(3) == [O_SG]
        
        h.step({
            0: ((Action.idle, None), O_SC, (2, 0), None),
            1: ((Action.idle, None), O_GC, (3, 0), None),
        })
        assert h.get_bag(0) == {Item.sand: 1}
        assert h.get_bag(1) == {Item.sand: 1}
        assert h.get_player_offers(0) == [O_SC]
        assert h.get_player_offers(1) == []
    
    def test_submit_and_accepted(self):
        # accepted prioritized
        h = Helper()
        h.init_pos({})
        h.reset()
        h.set_bag(0, {Item.gold: 1})
        h.set_bag(1, {Item.gold: 1})
        h.set_bag(2, {Item.sand: 1})
        h.set_bag(3, {Item.sand: 1})
        O_GS = ((Item.gold, -1), (Item.sand, 1))
        O_GC = ((Item.gold, -1), (Item.coral, 1))
        O_SC = ((Item.sand, -1), (Item.coral, 1))

        h.step({
            0: ((Action.idle, None), O_GS, None, None),
            1: ((Action.idle, None), O_GS, None, None),
        })
        assert h.get_bag(0) == {Item.gold: 1}
        assert h.get_bag(1) == {Item.gold: 1}
        assert h.get_player_offers(0) == [O_GS]
        assert h.get_player_offers(1) == [O_GS]

        h.step({
            0: ((Action.idle, None), O_SC, None, None),
            1: ((Action.idle, None), O_GC, None, None),
            2: ((Action.idle, None), None, (0, 0), None),
            3: ((Action.idle, None), None, (1, 0), None),
        })
        assert h.get_bag(0) == {Item.sand: 1}
        assert h.get_bag(1) == {Item.sand: 1}
        assert h.get_player_offers(0) == [O_SC]
        assert h.get_player_offers(1) == []
    
    def test_submit_and_cancel(self):
        # cancel prioritized
        M = PlayerConfig.max_offer
        h = Helper()
        h.init_pos({})
        h.reset()
        h.set_bag(0, {Item.gold: 2})
        h.set_bag(1, {Item.gold: 1})
        O_GS = ((Item.gold, -1), (Item.sand, 1))
        O_GC = ((Item.gold, -1), (Item.coral, 1))
        O_GP = ((Item.gold, -1), (Item.peanut, 1))
        
        h.step({
            0: ((Action.idle, None), O_GS, None, None),
            1: ((Action.idle, None), O_GS, None, None),
        })
        assert h.get_player(0).offers == [O_GS] + [None] * (M-1)
        assert h.get_player(1).offers == [O_GS] + [None] * (M-1)
        
        h.step({
            0: ((Action.idle, None), O_GC, None, None),
        })
        assert h.get_player(0).offers == [O_GS, O_GC] + [None] * (M-2)
        assert h.get_player(1).offers == [O_GS] + [None] * (M-1)
        assert h.get_player(0).backpack.gold.free_num == 0
        assert h.get_player(1).backpack.gold.free_num == 0
        
        h.step({
            0: ((Action.idle, None), O_GP, None, 0),
            1: ((Action.idle, None), O_GP, None, 0),
        })
        assert h.get_player(0).offers == [O_GP, O_GC] + [None] * (M-2)
        assert h.get_player(1).offers == [O_GP] + [None] * (M-1)
        assert h.get_player(0).backpack.gold.free_num == 0
        assert h.get_player(1).backpack.gold.free_num == 0

    def test_accept_and_accepted(self):
        # special case: accept is valid only after accepted
        MAX_TRIAL = 10
        O_GS = ((Item.gold, -1), (Item.sand, 1))
        O_PS = ((Item.peanut, -1), (Item.sand, 1))

        h = Helper()
        h.init_pos({})
        
        case_accept_first = False
        case_accepted_first = False
        for trial in range(MAX_TRIAL):
            h.reset()
            h.set_bag(0, {Item.gold: 1})
            h.set_bag(1, {Item.peanut: 1})
            h.set_bag(2, {Item.sand: 1})
                        
            h.step({
                0: ((Action.idle, None), O_GS, None, None),
                1: ((Action.idle, None), O_PS, None, None),
            })
            assert h.get_player_offers(0) == [O_GS]
            assert h.get_player_offers(1) == [O_PS]
            
            h.step({
                0: ((Action.idle, None), None, (1, 0), None),
                2: ((Action.idle, None), None, (0, 0), None),
            })
            
            if h.get_player_offers(1) == []:
                case_accepted_first = True # player 0 accepted then accept success
                assert h.get_player_offers(0) == []
                assert h.get_player_offers(1) == []
                assert h.get_bag(0) == {Item.peanut: 1}
                assert h.get_bag(1) == {Item.sand: 1}
                assert h.get_bag(2) == {Item.gold: 1}
            else:
                case_accept_first = True # player 0 accept fail then accepted
                assert h.get_player_offers(0) == []
                assert h.get_player_offers(1) == [O_PS]
                assert h.get_bag(0) == {Item.sand: 1}
                assert h.get_bag(1) == {Item.peanut: 1}
                assert h.get_bag(2) == {Item.gold: 1}
            
            if case_accept_first and case_accepted_first:
                break
        assert case_accept_first and case_accepted_first
    
    def test_accept_and_cancel(self):
        O_GS = ((Item.gold, -1), (Item.sand, 2))
        O_SG = ((Item.sand, -2), (Item.gold, 1))
        h = Helper()
        h.init_pos({})
        h.reset()
        h.set_bag(0, {Item.gold: 1})
        h.set_bag(1, {Item.sand: 2})
        h.step({
            0: ((Action.idle, None), O_GS, None, None),
            1: ((Action.idle, None), O_SG, None, None),
        })
        assert h.get_player(0).backpack.gold.locked_num == 1
        assert h.get_player(0).backpack.locked_volume == 1
        
        # accept should fail
        h.step({
            0: ((Action.idle, None), None, (1, 0), 0),
        })
        assert h.get_player_offers(0) == []
        assert h.get_player_offers(1) == [O_SG]
        assert h.get_bag(0) == {Item.gold: 1}
        assert h.get_bag(1) == {Item.sand: 2}
        assert h.get_player(0).backpack.gold.locked_num == 0
        assert h.get_player(0).backpack.locked_volume == 0
        assert h.get_error_log() == ''
        assert h.get_warning_log() != ''
        
    
    def test_accepted_and_cancel(self):
        O_GS = ((Item.gold, -1), (Item.sand, 2))
        h = Helper()
        h.init_pos({})
        h.reset()
        h.set_bag(0, {Item.gold: 1})
        h.set_bag(1, {Item.sand: 2})
        h.step({
            0: ((Action.idle, None), O_GS, None, None),
        })
        assert h.get_player_offers(0) == [O_GS]
        assert h.get_player(0).backpack.gold.locked_num == 1
        assert h.get_player(0).backpack.locked_volume == 1
        
        # cancel should fail
        h.step({
            0: ((Action.idle, None), None, None, 0),
            1: ((Action.idle, None), None, (0, 0), None),
        })
        assert h.get_player_offers(0) == []
        assert h.get_bag(0) == {Item.sand: 2}
        assert h.get_bag(1) == {Item.gold: 1}
        assert h.get_player(0).backpack.gold.locked_num == 0
        assert h.get_player(0).backpack.locked_volume == 0
        assert h.get_error_log() == ''
        assert h.get_warning_log() == ''