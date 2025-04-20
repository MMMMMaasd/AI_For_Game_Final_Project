import random
from Config import *

class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.possibilities = list(adjacency_rules.keys())
        self.entropy = len(self.possibilities)
        self.neighbours = dict()

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
    
    def constrain(self, neighbourPossibilities, direction):
        reduced = False

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

