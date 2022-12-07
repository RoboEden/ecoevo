from ecoevo.maps.map import MapManager
from ecoevo.entities.player import Player
from rich import print

if __name__ == "__main__":
    map_manager = MapManager()
    data = map_manager.data
    map = map_manager.reset_map()
    player0 = Player('gold_digger', 0, (1, 1))
    player1 = Player('hazelnut_farmer', 1, (2, 2))
    player2 = Player('coral_collector', 2, (6, 3))
    player3 = Player('sand_picker', 3, (2, 6))
    map_manager.allocate([player0, player1, player2, player3])
    # print(map)
    print(map.keys())