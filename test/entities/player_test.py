from rich import print
from ecoevo.entities import Player, load_item

if __name__ == "__main__":
    pos = (5, 7)
    player = Player(persona='hazelnut_farmer', id=0, pos=pos)
    print(player)
    print('preference', player.preference)
    print('ability', player.ability)

    peanut = load_item('peanut', num=100)

    # player.collect
    print(f'######### collect start #########')
    for i in range(10):
        print(f'######### {i} #########')
        player.collect(peanut)
        print('========= collect_remain ===========')
        print(player.collect_remain)
        print('========= backpack peanut ===========')
        print(player.backpack.peanut)

    # player.consume
    print(peanut.num)
    player.health -= 10
    print('========= before health ===========')
    print(player.health)
    player.consume('peanut')
    print('========= after health ===========')
    print(player.health)
    print('========= backpack peanut ===========')
    print(player.backpack.peanut)
    player.consume('sand')
    
    # player.next_pos
    print('pos', player.pos)
    print('up', player.next_pos('up'))
    print('down', player.next_pos('down'))
    print('right', player.next_pos('right'))
    print('left', player.next_pos('left'))

    # player.trade
    player.trade(('sand', -1), ('peanut', 2))
    print('Now add one sand to bag')
    player.backpack.sand.num = 1
    print('========= before backpack sand ===========')
    print(player.backpack.sand)
    player.trade(('sand', -1), ('peanut', 2))
    print('========= after backpack sand ===========')
    print(player.backpack.sand)
    print('========= after backpack peanut ===========')
    print(player.backpack.peanut)