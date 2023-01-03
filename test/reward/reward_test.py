from ecoevo.reward import RewardParser
from ecoevo.entities.player import Player
from rich import print
from ecoevo.entities.items import ALL_ITEM_DATA, load_item


def get_info(player: Player, rw_parser: RewardParser, ndigits=8):
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
    player = Player(persona="hazelnut_farmer", id=0, pos=pos)
    rw = reward_parser.parse(player)
    print(f"Initial reward: {rw}")

    # # consume each item once
    # reward_parser.last_utilities[player.id] = 0
    # for item_name in player.stomach.dict():
    #     player.stomach[item_name].num += player.stomach[item_name].harvest_num
    #     print(f"Consume a {item_name}:", get_info(player, reward_parser))
    #     player.stomach[item_name].num = 0
    #     reward_parser.last_utilities[player.id] = 0

    # consume same item multiple times
    item_name = "hazelnut"
    player.stomach[item_name].num = 0
    reward_parser.last_utilities[player.id] = 0
    for i in range(20):
        player.stomach[item_name].num += player.stomach[item_name].harvest_num
        suffix = "st" if i + 1 == 1 else "nd" if i + 1 == 2 else "rd" if i + 1 == 3 else "th"
        print(f"Consume the {i + 1}{suffix} {item_name}:", get_info(player, reward_parser))

    # health
    while player.health > 0:
        player.health -= 20
        if player.health >= 0:
            print(f"Player HP: {player.health}", get_info(player, reward_parser))

    print(f"Player HP: {player.health}", get_info(player, reward_parser))
