from ecoevo.maps.map import MapGenerator

if __name__ == "__main__":
    map_generator = MapGenerator()
    data = map_generator.data
    map = map_generator.gen_map()
    # print(map)
    print(map[(0, 1)])