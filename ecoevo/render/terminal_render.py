from ecoevo.entities import Tile
from ecoevo.render import print
from typing import Dict, List
from ecoevo.types import *

class TerminalRender:

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.player_to_emoji = {
            'gold_digger': ':angry_face:',
            'hazelnut_farmer': ':angry_face_with_horns:',
            'coral_collector': ':anguished_face:',
            'sand_picker': ':anxious_face_with_sweat:',
            'pineapple_farmer': ':astonished_face:',
            'peanut_farmer': ':beaming_face_with_smiling_eyes:',
            'stone_picker': ':cat_face:',
            'pumpkin_farmer': ':bear_face:',
        }

        self.item_to_emoji = {
            'gold': '🪙 ',
            'hazelnut': ':chestnut:',
            'coral': '🪸 ',
            'sand': '🏖️ ',
            'pineapple': ':pineapple:',
            'peanut': ':peanuts:',
            'stone': '🪨 ',
            'pumpkin': ':jack_o_lantern:',
        }

    def render(self, map: Dict[PosType, Tile]):
        screen = []
        for i in range(self.height // 2):
            screen.append(['⬛', '⬛', ':brown_square:', ':brown_square:'] *
                          (self.width // 2))
            screen.append(['⬛', '⬛', ':brown_square:', ':brown_square:'] *
                          (self.width // 2))
            screen.append([':brown_square:', ':brown_square:', '⬛', '⬛'] *
                          (self.width // 2))
            screen.append([':brown_square:', ':brown_square:', '⬛', '⬛'] *
                          (self.width // 2))

        for pos, tile in map.items():
            x, y = pos

            if tile.item is not None:
                screen[2 * x][2 * y] = self.item_to_emoji[tile.item.name]
            if tile.player is not None:
                screen[2 * x +
                       1][2 * y +
                          1] = self.player_to_emoji[tile.player.persona]
        self.show(screen)

    def show(self, screen: List[List[str]]):
        scren_width = 2 * self.width + 2
        print(':heavy_minus_sign:' * scren_width)
        for k, v in self.item_to_emoji.items():
            print(k, v)
        print(':white_large_square:' * scren_width)
        for row in screen:
            row = ''.join(row)
            print(f':white_large_square:{row}:white_large_square:')
        print(':white_large_square:' * scren_width)
        for k, v in self.player_to_emoji.items():
            print(k, v)
        print(':heavy_minus_sign:' * scren_width)