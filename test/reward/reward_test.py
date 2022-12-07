from ecoevo.reward import RewardParser
from ecoevo.entities.player import Player
from rich import print
from ecoevo.entities.items import ALL_ITEM_DATA, load_item


def get_info(player: Player, rw_parser: RewardParser, ndigits=4):
    last_u = rw_parser.last_utilities[player.id]
    u = reward_parser.utility(player)
    cost = reward_parser.cost(player)
    rw = reward_parser.parse(player)

    return {
        "last_u": round(last_u, ndigits),
        "utility": round(u, ndigits),
        "cost": round(cost, ndigits),
        "reward": round(rw, ndigits)
    }


if __name__ == "__main__":
    # Init
    reward_parser = RewardParser()
    pos = (5, 7)
    player = Player("hazelnut_farmer", 0, pos)
    rw = reward_parser.parse(player)
    print(f"Initial reward: {rw}")

    # Consume
    for itm_name in player.stomach.dict():
        player.stomach[itm_name].num += 1
        print(f"Consume a {itm_name}:", get_info(player, reward_parser))

    # Consume the same item multiple times
    for _ in range(10):
        itm_name = "gold"
        player.stomach[itm_name].num += 1
        print(f"Consume a {itm_name}:", get_info(player, reward_parser))

    # Weight
    for itm_name in player.backpack.dict():
        player.backpack[itm_name].num += 1
        print(f"Add a {itm_name}:", get_info(player, reward_parser))

    # Health
    while player.health > 0:
        player.health -= 30
        print(f"Player HP: {player.health}", get_info(player, reward_parser))

    print(f"Player HP: {player.health}", get_info(player, reward_parser))
