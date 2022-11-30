import numpy as np
import json
from typing import Dict, Tuple
from ecoevo.entities.agent import Agent
from ecoevo.entities.items import Item
from ecoevo.config import MapSize

class MapGenerator:
    def __init__(self) -> None:
        path = './files/base.json'
        with open(path) as fp:
            self.data = json.load(fp)
    
    @staticmethod
    def gen_random_grid(width: int, height: int, NUM_TILE_TYPE: int):
        data = np.random.randint(low=0, high=NUM_TILE_TYPE, size=(height, width))
        
        return data

    def gen_map(self) -> Dict[Tuple[int,int], Dict[str:Item, str:Agent]]:
        map = {}
        for x, y in self.data.items:
            map[(x,y)] = {'item': Item(type),'agent':Agent(self.data['type'])}
        
        return map