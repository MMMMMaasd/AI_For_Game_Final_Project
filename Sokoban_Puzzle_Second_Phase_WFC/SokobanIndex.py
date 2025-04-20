import random
from utils import *
from typing import List, Tuple, Optional, Any
from SokobanLevel import Node, SokobanLevel
from generator import *
from pathfinder import *


def randomLevel():
    levelNumber = 0
    inGame = False
    newLevel()

# generate a new level
def newLevel(level_width, level_height, num_of_boxes):
    currentLvl = SokobanLevel(level_width, level_height, num_of_boxes)
    #random_number = random.randint(-2, 5)
    currentLvl.rip(8)
    # generate level
    generatePaths(currentLvl)
    return (currentLvl.trash, currentLvl.get_tile_grid())

def upscale_maze(maze, scale):
    rows, cols = maze.shape
    new_rows, new_cols = rows * scale, cols * scale
    upscaled = np.zeros((new_rows, new_cols), dtype=int)

    for r in range(rows):
        for c in range(cols):
            value = maze[r, c]
            for i in range(scale):
                for j in range(scale):
                    upscaled[r * scale + i, c * scale + j] = value


    return upscaled


    # if the level is unsolvable, generate a new level

    #if (currentLvl.trash):
    #    print("trashlevel")
    #    newLevel()
    #else:
    #    print(currentLvl.get_tile_grid())


# [['WALL', 'WALL', 'WALL', 'Floor', 'Floor', 'WALL', 'WALL', 'WALL', 'WALL', 'WALL'], ['WALL', 'Floor', 'Floor', 'Floor', 'Floor', 'Floor', 'Floor', 'Floor', 'WALL', 'WALL'], ['WALL', 'Floor', 'Floor', 'Floor', 'Floor', 'Floor', 'Floor', 'Floor', 'Floor', 'WALL'], ['WALL', 'Floor', 'BOX', 'TARGET', 'PLAYER', 'Floor', 'Floor', 'BOX', 'Floor', 'WALL'], ['Floor', 'Floor', 'BOX', 'TARGET', 'Floor', 'BOX', 'Floor', 'BOX', 'Floor', 'Floor'], ['Floor', 'Floor', 'TARGET', 'Floor', 'Floor', 'TARGET', 'Floor', 'Floor', 'Floor', 'Floor'], ['WALL', 'WALL', 'WALL', 'Floor', 'Floor', 'WALL', 'TARGET', 'WALL', 'WALL', 'WALL'], ['WALL', 'WALL', 'WALL', 'WALL', 'WALL', 'WALL', 'WALL', 'WALL', 'WALL', 'WALL'], ['WALL', 'WALL', 'WALL', 'WALL', 'WALL', 'WALL', 'WALL', 'WALL', 'WALL', 'WALL'], ['WALL', 'WALL', 'WALL', 'WALL', 'WALL', 'WALL', 'WALL', 'WALL', 'WALL', 'WALL']]

