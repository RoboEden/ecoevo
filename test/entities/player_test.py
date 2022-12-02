from rich import print
from ecoevo.entities.player import Player
from ecoevo.entities.items import load_item

if __name__ == "__main__":

    player = Player('pepper_bro', 0)

    print('========= name ===========')
    print(player.name)
    print('========= ability ===========')
    print(player.ability)
    print('========= preference ===========')
    print(player.preference)
    print('========= backpack ===========')
    print(player.backpack)
    print('========= stomach ===========')
    print(player.stomach)
    print('========= pos ===========')
    print(player.pos)
    print('========= id ===========')
    print(player.id)
    print('========= health ===========')
    print(player.health)
    print('========= collect_cast_remain ===========')
    print(player.collect_cast_remain)

    player.pos = (5, 7)
    peanut = load_item('peanut', num=100)

    # player.collect
    print(f'######### collect start #########')
    for i in range(10):
        print(f'######### {i} #########')
        player.collect(peanut)
        print('========= collect_cast_remain ===========')
        print(player.collect_cast_remain)
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

    # player.move
    print('========= before pos ===========')
    print(player.pos)
    player.move('up')
    print('========= after pos ===========')
    print(player.pos)
    player.move('down')
    print('========= after pos ===========')
    print(player.pos)
    player.move('right')
    print('========= after pos ===========')
    print(player.pos)
    player.move('left')
    print('========= after pos ===========')
    print(player.pos)

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

    # player.execute
    print('========= before pos ===========')
    print(player.pos)
    print('========= before backpack peanut ===========')
    print(player.backpack.peanut)
    print('========= before backpack gold ===========')
    print(player.backpack.gold)
    player.execute(('move', 'up'), ('peanut', -1), ('gold', 2))
    print('========= after pos ===========')
    print(player.pos)
    print('========= after backpack peanut ===========')
    print(player.backpack.peanut)
    print('========= after backpack gold ===========')
    print(player.backpack.gold)