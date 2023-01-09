from rich import print

from ecoevo.entities.player import Player
from ecoevo.reward import RewardParser


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
    print("#############################################")
    print("Consume each item once")
    print("#############################################")
    reward_parser = RewardParser()
    pos = (5, 7)
    player = Player(persona="hazelnut_farmer", id=0, pos=pos)
    rw = reward_parser.parse(player)
    print(f"Initial reward: {rw}")
    for itm_name in player.stomach.dict():
        player.stomach[itm_name].num += player.stomach[itm_name].harvest_num
        print(f"Add {itm_name} to stomach with {player.stomach[itm_name].harvest_num} num :",
              get_info(player, reward_parser))

    print("#############################################")
    print("Consume the same item multiple times")
    print("#############################################")
    reward_parser = RewardParser()
    pos = (5, 7)
    player = Player(persona="hazelnut_farmer", id=0, pos=pos)
    rw = reward_parser.parse(player)
    print(f"Initial reward: {rw}")

    itm_name = "gold"
    harvest_num = player.backpack[itm_name].harvest_num
    print(f"Add {harvest_num} num of {itm_name} to backpack")
    player.backpack[itm_name].num += harvest_num
    print(f"current num of {itm_name} in backpack: {player.backpack[itm_name].num}")

    for ith in range(30):
        is_disposable = player.backpack[itm_name].disposable
        if is_disposable:
            player.stomach[itm_name].num += player.backpack[itm_name].consume_num
        else:
            player.stomach[itm_name].num += player.backpack[itm_name].num
        print(f"Consume {ith}th {itm_name}:", get_info(player, reward_parser))
