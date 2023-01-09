from rich import print

from ecoevo.entities.items import ALL_ITEM_DATA, load_item
from ecoevo.entities.player import Player
from ecoevo.reward import RewardParser


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
    print("########################################")
    print("consume each item once")
    print("########################################")
    for item_name in ALL_ITEM_DATA.keys():
        reward_parser = RewardParser()
        pos = (5, 7)
        player = Player(persona="hazelnut_farmer", id=0, pos=pos)
        rw = reward_parser.parse(player)
        print(f"Initial reward: {rw}")
        player.stomach[item_name].num += player.stomach[item_name].harvest_num
        print(f"Consume a {item_name}:", get_info(player, reward_parser))
        print()

    print("########################################")
    print("consume same item multiple times")
    print("########################################")
    reward_parser = RewardParser()
    pos = (5, 7)
    player = Player(persona="hazelnut_farmer", id=0, pos=pos)
    rw = reward_parser.parse(player)
    print(f"Initial reward: {rw}")
    item_name = "hazelnut"
    player.stomach[item_name].num = 0
    for i in range(30):
        player.stomach[item_name].num += player.stomach[item_name].harvest_num
        suffix = "st" if i + 1 == 1 else "nd" if i + 1 == 2 else "rd" if i + 1 == 3 else "th"
        print(f"Consume the {i + 1}{suffix} {item_name}:", get_info(player, reward_parser))

    item_name = "gold"
    player.stomach[item_name].num += player.stomach[item_name].harvest_num
    print(f"Consume a {item_name}:", get_info(player, reward_parser))

    print("########################################")
    print("test health")
    print("########################################")
    while player.health > 0:
        player.health -= 20
        if player.health >= 0:
            print(f"Player HP: {player.health}", get_info(player, reward_parser))

    print(f"Player HP: {player.health}", get_info(player, reward_parser))
