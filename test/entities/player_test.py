from rich import print
from ecoevo.entities.player import Player

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