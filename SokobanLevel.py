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
    def __init__(self, width: int, height: int, num_boxes: int):
        self.width = width
        self.height = height
        self.targets = []
        self.boxes = []
        self.ghostboxes = []
        self.solveCounter = num_boxes
        self.saved_position = []
        self.trash = False
        
        self.nodes = [[Node(x, y) for y in range(width)] for x in range(height)]

        
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
        """
        Places targets, boxes and player for Sokoban puzzle.
        Enhanced to work better with small regions.
        """
        # Detect if this is a small region needing special handling
        small_region = self.width * self.height < 20
        
        # ---- PLACE TARGETS ----
        target_attempts = 50 if small_region else 20
        for i in range(numBoxes):
            placed = False
            # Try multiple times for each target
            for _ in range(target_attempts):
                pos = self.randomSpot()
                if pos:
                    x, y = pos
                    self.targets.append(Button(x, y))
                    placed = True
                    break
                    
            # For small regions, try harder to find spots
            if not placed and small_region:
                # Last resort: scan for any unoccupied spot
                for y in range(1, self.height-1):
                    for x in range(1, self.width-1):
                        if not self.nodes[x][y].wall and not self.nodes[x][y].has_box:
                            self.targets.append(Button(x, y))
                            self.nodes[x][y].tile_id = 0  # Mark as floor
                            placed = True
                            break
                    if placed:
                        break
        
        # Check if we have any targets - if not, mark level as invalid
        if not self.targets:
            print(f"Warning: Couldn't place any targets in {self.width}x{self.height} region")
            self.trash = True
            return
        
        # ---- PLACE BOXES ----
        # Only use targets that were successfully placed
        box_count = min(numBoxes, len(self.targets))
        for i in range(box_count):
            placed = False
            # Try random placement first
            for _ in range(target_attempts):
                pos = self.randomSpot()
                if pos:
                    x, y = pos
                    box = Box(x, y, self.targets[i])
                    self.boxes.append(box)
                    self.nodes[x][y].has_box = True
                    placed = True
                    break
                    
            # For small regions, try placing boxes near their targets
            if not placed and small_region:
                target = self.targets[i]
                # Try adjacent positions first
                for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
                    nx, ny = target.x + dx, target.y + dy
                    if (0 <= nx < self.width and 0 <= ny < self.height and
                        not self.nodes[nx][ny].wall and not self.nodes[nx][ny].has_box):
                        box = Box(nx, ny, target)
                        self.boxes.append(box)
                        self.nodes[nx][ny].has_box = True
                        placed = True
                        break
                        
                # If still not placed, try any valid position
                if not placed:
                    for y in range(1, self.height-1):
                        for x in range(1, self.width-1):
                            if not self.nodes[x][y].wall and not self.nodes[x][y].has_box:
                                box = Box(x, y, self.targets[i])
                                self.boxes.append(box)
                                self.nodes[x][y].has_box = True
                                placed = True
                                break
                        if placed:
                            break
        
        # If no boxes were placed, mark as invalid
        if not self.boxes:
            print("Warning: Couldn't place any boxes")
            self.trash = True
            return
        
        # ---- PLACE PLAYER ----
        # Try random placement
        pos = self.randomSpot()
        player_placed = False
        
        if pos:
            x, y = pos
            player_placed = True
        
        # Try near boxes if random placement failed
        if not player_placed and self.boxes:
            box = self.boxes[0]
            for dx, dy in [(0,1), (1,0), (0,-1), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]:
                nx, ny = box.x + dx, box.y + dy
                if (0 <= nx < self.width and 0 <= ny < self.height and
                    not self.nodes[nx][ny].wall and not self.nodes[nx][ny].has_box):
                    x, y = nx, ny
                    player_placed = True
                    break
                    
        # Last resort: use a target position
        if not player_placed and self.targets:
            x, y = self.targets[0].x, self.targets[0].y
            player_placed = True
            
        # If we still couldn't place the player, mark as invalid
        if not player_placed:
            print("Warning: Couldn't place player")
            self.trash = True
            return
            
        self.setPlayerPos(x, y)
        self.playerstartX = self.playerX
        self.playerstartY = self.playerY


            

    # return a random unoccupied spot and remove the wall
    def randomSpot(self):
        if self.allowedSpots:
            node = random.choice(self.allowedSpots)
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
        return np.array(grid, dtype=int)
        


    def check_region_viability(lvl):
        """Check if a region has enough space for a valid puzzle"""
        open_count = sum(1 for row in lvl.nodes for node in row if not node.wall)
        
        # Need minimum viable space
        if open_count < 4:
            return False
            
        # Check if there's at least one 2x2 open area somewhere
        has_open_area = False
        for y in range(lvl.height - 1):
            for x in range(lvl.width - 1):
                if (not lvl.nodes[y][x].wall and
                    not lvl.nodes[y][x+1].wall and
                    not lvl.nodes[y+1][x].wall and
                    not lvl.nodes[y+1][x+1].wall):
                    has_open_area = True
                    break
                    
        return has_open_area
