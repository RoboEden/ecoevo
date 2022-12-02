from ecoevo.reward import RewardParser
from ecoevo.entities.player import Player
from ecoevo.entities.items import ALL_ITEM_TYPES, load_item

if __name__ == "__main__":
    reward_parser = RewardParser()
    player = Player(name="pepper_bro", id=0)
    rw = reward_parser.parse(player)
    print(rw)
    
    # item = load_item("pineapple", num=1)
    # player.consume(item)
    # rw = reward_parser.parse(player)
    # print(rw)
    