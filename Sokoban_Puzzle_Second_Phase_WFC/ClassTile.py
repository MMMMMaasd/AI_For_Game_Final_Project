import random
from Config import *

class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.possibilities = list(adjacency_rules.keys())
        self.entropy = len(self.possibilities)
        self.neighbours = dict()
        self.collapsed_neighbors = {}

    def addNeighbour(self, direction, tile):
        self.neighbours[direction] = tile
    
    def getNeighbour(self, direction):
        return self.neighbours[direction]
    
    def getDirections(self):
        return list(self.neighbours.keys())

    def getPossibilities(self):
        return self.possibilities
    
    def collapse(self):
        weights = [tileWeights[possibility] for possibility in self.possibilities]
        self.possibilities = random.choices(self.possibilities, weights=weights, k=1)
        self.entropy = 0
        
    def update_collapsed_neighbors(self):
        for direction, neighbor in self.neighbours.items():
            self.collapsed_neighbors[direction] = (neighbor.entropy == 0)
            
    def get_known_neighbors(self):
        known = {}
        for direction, neighbor in self.neighbours.items():
            if self.collapsed_neighbors.get(direction, False):
                known[direction] = neighbor.possibilities[0] if neighbor.possibilities else None
            else:
                known[direction] = None
        return known
        
    def _apply_progressive_boundary_rules(self, known_neighbors):
        left = known_neighbors.get(WEST)
        right = known_neighbors.get(EAST)
        top = known_neighbors.get(NORTH)
        bottom = known_neighbors.get(SOUTH)

        required_tile = None
        
        if left in inner_set_tiles:
            required_tile = TILE_ROCK_WALL_LEFT
            
            # Refine if we know top/bottom neighbors
            if top in inner_set_tiles and bottom not in inner_set_tiles:
                required_tile = TILE_ROCK_VERTICAL_DIAGONAL_LEFT
            elif top not in inner_set_tiles and bottom in inner_set_tiles:
                required_tile = TILE_ROCK_WALL_BOTTOM_LEFT

        elif right in inner_set_tiles:
            required_tile = TILE_ROCK_WALL_RIGHT2
            if top in inner_set_tiles and bottom not in inner_set_tiles:
                required_tile = TILE_ROCK_VERTICAL_DIAGONAL_RIGHT
            elif top not in inner_set_tiles and bottom in inner_set_tiles:
                required_tile = TILE_ROCK_WALL_BOTTOM_RIGHT

        elif top in inner_set_tiles:
            required_tile = TILE_ROCK_VERTICAL_MID

        elif bottom in inner_set_tiles:
            required_tile = TILE_ROCK_WALL_BOTTOM_MID

        # Apply if we found a rule
        if required_tile and required_tile in self.possibilities:
            self.possibilities = [required_tile]
            self.entropy = 1
            return True
            
        return False
    
    def constrain(self, neighbourPossibilities, direction):
        reduced = False

        if self.entropy > 1:
            self.update_collapsed_neighbors()
            known = self.get_known_neighbors()
            reduced |= self._apply_progressive_boundary_rules(known)


        if self.entropy > 0:
            # ✅ First, determine the opposite direction
            if direction == NORTH:
                opposite = SOUTH
            elif direction == EAST:
                opposite = WEST
            elif direction == SOUTH:
                opposite = NORTH
            elif direction == WEST:
                opposite = EAST
            else:
                raise ValueError(f"Invalid direction: {direction}")

            # ✅ Collect all valid connectors from neighbor possibilities
            connectors = set()
            for neighbourPossibility in neighbourPossibilities:
                connectors |= adjacency_rules[neighbourPossibility][direction]
            
            print(f"[DEBUG] Constraining ({self.x}, {self.y}) from dir {direction}")
            print(f"Neighbor possibilities: {neighbourPossibilities}")
            print(f"Valid connectors: {connectors}")
            print(f"Current possibilities: {self.possibilities}")
    
            # ✅ Remove any invalid possibilities
            for possibility in self.possibilities.copy():
                if possibility not in connectors:
                    self.possibilities.remove(possibility)
                    reduced = True
            print(f"New possibilities: {self.possibilities}")
            self.entropy = len(self.possibilities)

        return reduced

