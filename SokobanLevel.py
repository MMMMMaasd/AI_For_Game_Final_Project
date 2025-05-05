import random
from typing import List, Tuple, Optional, Any
import numpy as np

class Node:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.f = 0  # path-cost-estimation
        self.cost = 0  # path-cost
        self.closed = False  # for pathfinding
        self.checked = False  # for pathfinding
        self.wall = True  # default to wall
        self.occupied = False  # for boxes/player
        self.parent = None  # for path reconstruction
        self.has_box = False  # box marker
        self.used = False  # optimization flag
        self.tile_id = 1  # default wall tile (matching your WFC system)
        self.permanent = False

class Box:
    def __init__(self, X, Y, button):
        self.x = X
        self.y = Y
        self.px = self.x
        self.py = self.y
        self.placed = False
        self.solveButton = button
        
    def setPosition(self, X, Y):
        self.x = X
        self.y = Y

    def placeExactly(self, X, Y):
        self.x = X
        self.y = Y
        self.px = self.x
        self.py = self.y

class Button:
    def __init__(self, X: int, Y:int):
        self.x = X
        self.y = Y

class SokobanLevel:
    def __init__(self, width: int, height: int, num_boxes: int, boundaries: List[Tuple[int, int]] = None, start_pos: Tuple[int, int] = None, end_pos: Tuple[int, int] = None):
        self.width = width
        self.height = height
        self.targets = []
        self.boxes = []
        self.ghostboxes = []
        self.solveCounter = num_boxes
        self.saved_position = []
        self.trash = False
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.boundaries = boundaries if boundaries else []
        
        self.nodes = [[Node(x, y) for y in range(width)] for x in range(height)]

        # Initialize boundaries as permanent walls
        for x, y in self.boundaries:
            if 0 <= x < height and 0 <= y < width:
                self.nodes[x][y].wall = True
                self.nodes[x][y].tile_id = 1
                self.nodes[x][y].permanent = True
        
        if end_pos:
            end_x, end_y = end_pos
            if 0 <= end_x < height and 0 <= end_y < width:
                self.nodes[end_x][end_y].wall = False
                self.nodes[end_x][end_y].tile_id = 0
                self.nodes[end_x][end_y].permanent = True
                
        # Initialize grid (1=wall, 0=floor)
        self.defineAllowedSpots()
        self.place_objects(num_boxes)
        
    # write all nodes, where placement is allowed into a list
    def defineAllowedSpots(self):
        self.allowedSpots = []
        for i in range(2, self.height - 2):
            for j in range(2, self.width - 2):
                self.allowedSpots.append(self.nodes[i][j])

    def place_objects(self, numBoxes):
        # place buttons
        for i in range(numBoxes):
            pos = self.randomSpot()
            if pos:
                x, y = pos
                self.targets.append(Button(x, y))
                # self.nodes[x][y].tile_id = 13  # Set button tile ID
        
        for i in range(numBoxes):
            pos = self.randomSpot()
            if pos:
                x, y = pos
                box = Box(x, y, self.targets[i])
                self.boxes.append(box)
                self.nodes[x][y].has_box = True
                # self.nodes[x][y].tile_id = 68  # Box tile ID
        
        pos = self.randomSpot()
        if not pos:
            x, y = self.targets[0].x, self.targets[0].y
        else:
            x, y = pos
        self.setPlayerPos(self.start_pos[0], self.start_pos[1])
        self.playerstartX = self.playerX
        self.playerstartY = self.playerY
        # self.nodes[x][y].tile_id = 99  # Player tile ID
            

    # return a random unoccupied spot and remove the wall
    def randomSpot(self):
        available_spots = [spot for spot in self.allowedSpots if not spot.permanent]
        if available_spots:
            node = random.choice(available_spots)
            self.allowedSpots.remove(node)
            node.wall = False
            node.tile_id = 0 #Floor tile id
            if (self.blockaded(node.x, node.y)):
                return self.randomSpot()
            return (node.x, node.y)
        return None;

    # randomly remove walls from the level
    def rip(self, amount):
        for i in range(amount):
            if len(self.allowedSpots):
                self.randomSpot()

    def setPlayerPos(self, X, Y):
        self.playerX = X;
        self.playerY = Y;

    # check if a spot is blockaded by boxes
    def blockaded(self, X, Y):
        if (X+1 < self.height and self.nodes[X + 1][Y].has_box):
            if (Y+1 < self.height and self.nodes[X + 1][Y + 1].has_box and self.nodes[X][Y + 1].has_box):
                return True
            if (Y - 1 >= 0 and self.nodes[X + 1][Y - 1].has_box and self.nodes[X][Y - 1].has_box):
                return True
                
        if (X-1 >= 0 and self.nodes[X - 1][Y].has_box):
            if (Y-1 >= 0 and self.nodes[X - 1][Y - 1].has_box and self.nodes[X][Y - 1].has_box):
                return True
            if (Y+1 < self.width and self.nodes[X - 1][Y + 1].has_box and self.nodes[X][Y + 1].has_box):
                return True
        return False
    
    def get_tile_grid(self):
        grid = [[0 for _ in row] for row in self.nodes]
        # Apply wall tiles (1)
        for row in self.nodes:
            for node in row:
                if node.wall:
                    grid[node.x][node.y] = 1

        # Apply targets (2)
        for target in self.targets:
            grid[target.x][target.y] = 2

        # Apply boxes (3)
        for box in self.boxes:
            grid[box.x][box.y] = 3

        # Apply player (4)
        grid[self.playerX][self.playerY] = 4
        grid[self.end_pos[0]][self.end_pos[1]] = 5
        return np.array(grid, dtype=int)
        
       # for row in self.nodes:
       #     for node in row:
       #         if node.wall == False:
       #             node.tile_id = 0
       # for target in self.targets:
       #     self.nodes[target.x][target.y].tile_id = 2
        
       # for box in self.boxes:
       #     self.nodes[box.x][box.y].tile_id = 3
       # for row in self.nodes:
       #     for node in row:
       #         if node.wall:
       #             node.tile_id = 1
        
       # self.nodes[self.playerX][self.playerY].tile_id = 4
        
       # return [[node.tile_id for node in row] for row in self.nodes]
        


