from ClassWorld import World
from Config import *
import numpy as np

class ConditionalWorld(World):
    def __init__(self, sizeX, sizeY, solution_mask, blocker_mask=None):
        super().__init__(sizeX, sizeY)
        self.solution_mask = solution_mask
        self.blocker_mask = blocker_mask if blocker_mask is not None else np.zeros_like(solution_mask, dtype=bool)

        for y in range(self.rows):
            for x in range(self.cols):
                tile = self.tileRows[y][x]

                if self.solution_mask[y][x]:
                    tile.possibilities = list(solution_set_tiles)  # restrict to path tiles

                elif self.blocker_mask[y][x]:
                    tile.possibilities = list(blocker_set_tiles)  # restrict to blocker tiles

                else:
                    tile.possibilities = list(adjacency_rules.keys())  # full set

                tile.entropy = len(tile.possibilities)
