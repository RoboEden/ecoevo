from ecoevo.entities.player import Bag, Player

if __name__ == "__main__":
    bag = Bag()
    print(bag)
    print(bag.coral)
    print('=====================')
    print(bag.coral.num)
    print(bag.remain_volume)

    player = Player('pepper_bro', 0)
    print(player.stomach)
    print(player.backpack)
    print(player.ability)
    print(player.preference)