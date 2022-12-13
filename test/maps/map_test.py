from ecoevo.maps.map import MapManager
from ecoevo.entities.player import Player
from rich import print

if __name__ == "__main__":
    map_manager = MapManager()
    data = map_manager.data
    map = map_manager.reset_map()
    player0 = Player(persona='gold_digger', id=0, pos=(1, 1))
    player1 = Player(persona='hazelnut_farmer', id=1, pos=(2, 2))
    player2 = Player(persona='coral_collector', id=2, pos=(6, 3))
    player3 = Player(persona='sand_picker', id=3, pos=(2, 6))
    map_manager.allocate([player0, player1, player2, player3])
    # print(map)
    print(map.keys())