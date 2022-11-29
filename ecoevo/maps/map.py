import numpy as np


class MapGenerator:
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def gen_random_grid(width: int, height: int, NUM_TILE_TYPE: int):
        data = np.random.randint(low=0, high=NUM_TILE_TYPE, size=(height, width))
        
        return data