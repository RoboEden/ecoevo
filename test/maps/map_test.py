from ecoevo.maps.map import MapManager
from ecoevo.entities.player import Player

if __name__ == "__main__":
    map_manager = MapManager()
    data = map_manager.data
    map = map_manager.reset_map()
    player0 = Player('pepper_bro', 0, (1, 1))
    player1 = Player('pepper_bro', 1, (2, 2))
    player2 = Player('pepper_bro', 2, (6, 3))
    player3 = Player('pepper_bro', 3, (2, 6))
    map_manager.allocate([player0, player1, player2, player3])
    # print(map)
    print(map.keys())