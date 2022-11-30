from ecoevo.maps.map import MapGenerator

if __name__ == "__main__":
    map_generator = MapGenerator()
    data = map_generator.data
    print(data['tiles'])
    print(data['amount'])
    print(data.keys())
    map = map_generator.gen_map()