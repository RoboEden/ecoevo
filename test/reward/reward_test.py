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

    # consume each item once
    for itm_name in player.stomach.dict():
        player.stomach[itm_name].num += player.stomach[itm_name].harvest_num
        print(f"Consume a {itm_name}:", get_info(player, reward_parser))
        player.stomach[itm_name].num = 0

    # consume same item multiple times
    player.stomach[itm_name].num = 0
    for _ in range(20):
        itm_name = "hazelnut"
        player.stomach[itm_name].num += player.stomach[itm_name].harvest_num
        print(f"Consume a {itm_name}:", get_info(player, reward_parser))

    # health
    while player.health > 0:
        player.health -= 20
        if player.health >= 0:
            print(f"Player HP: {player.health}", get_info(player, reward_parser))

    print(f"Player HP: {player.health}", get_info(player, reward_parser))
