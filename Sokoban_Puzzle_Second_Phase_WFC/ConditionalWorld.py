from ClassWorld import World
from Config import *
import numpy as np

class ConditionalWorld(World):
    def __init__(self, sizeX, sizeY, floor_mask, wall_mask, target_mask, box_mask, player_mask):
        super().__init__(sizeX, sizeY)
        self.floor_mask = floor_mask
        self.wall_mask = wall_mask
        self.target_mask = target_mask
        self.box_mask = box_mask
        self.player_mask = player_mask
        # self.blocker_mask = blocker_mask if blocker_mask is not None else np.zeros_like(solution_mask, dtype=bool)

        for y in range(self.rows):
            for x in range(self.cols):
                tile = self.tileRows[y][x]
                
                if self.floor_mask[y][x]:
                    tile.possibilities = list(floor_set_tiles)  # restrict to path tiles
                elif self.wall_mask[y][x]:
                    tile.possibilities = list(wall_set_tiles)
                elif self.target_mask[y][x]:
                    tile.possibilities = list(target_set_tiles)
                elif self.box_mask[y][x]:
                    tile.possibilities = list(box_set_tiles)
                elif self.player_mask[y][x]:
                    tile.possibilities = list(player_set_tiles)
                else:
                    tile.possibilities = list(adjacency_rules.keys())  # full set
            
                tile.entropy = len(tile.possibilities)
