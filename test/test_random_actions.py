from ecoevo import EcoEvo
from ecoevo.types import ActionType, MainActionType, Action, OfferType
from ecoevo.entities.items import ALL_ITEM_DATA
import random

primary_actions = ["idle", "move", "collect", "consume"]
directions = ["up", "down", "right", "left"]
item_names = list(ALL_ITEM_DATA.keys())


def sample_main_action() -> MainActionType:
    primary_action = random.sample(primary_actions, 1)[0]
    secondary_action = None
    if primary_action == Action.idle or primary_action == Action.collect:
        secondary_action = None
    elif primary_action == Action.move:
        secondary_action = random.sample(directions, 1)[0]
    elif primary_action == Action.consume:
        secondary_action = random.sample(item_names, 1)[0]

    main_action = (primary_action, secondary_action)

    return main_action


def sample_offer(max_num: int = 100000) -> OfferType:
    item_name = random.sample(item_names, 1)[0]
    num = random.randint(-abs(max_num), abs(max_num))

    return (item_name, num)


def sample_action(max_sell_num: int = 100000, max_buy_num: int = 100000) -> ActionType:
    main_action = sample_main_action()
    sell_offer = sample_offer(max_sell_num)
    buy_offer = sample_offer(max_buy_num)

    return (main_action, sell_offer, buy_offer)


def test_random_actions():
    # Init env
    env = EcoEvo(logging_level="DEBUG")

    # Reset
    obs, info = env.reset()
    print('num_player:', env.num_player)

    # Step teset
    actions = [(('consume', 'peanut'), ('gold', -5), ('peanut', 20))] * env.num_player
    for _ in range(env.cfg.total_step):
        actions = [sample_action() for _ in range(env.num_player)]
        obs, reward, done, info = env.step(actions)