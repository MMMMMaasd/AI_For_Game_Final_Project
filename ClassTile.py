import random
from Config import *

class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.possibilities = list(adjacency_rules1.keys())
        self.entropy = len(self.possibilities)
        self.neighbours = dict()
        self.constrain_func = None

    def addNeighbour(self, direction, tile):
        self.neighbours[direction] = tile
    
    def getNeighbour(self, direction):
        return self.neighbours[direction]
    
    def getDirections(self):
        return list(self.neighbours.keys())

    def getPossibilities(self):
        return self.possibilities
    
    def collapse(self, weights_dict=None):
        if weights_dict:
            weights = [weights_dict.get(p, 1) for p in self.possibilities]
        else:
            weights = [tileWeights.get(p, 1) for p in self.possibilities]
        self.possibilities = random.choices(self.possibilities, weights=weights, k=1)
        self.entropy = 0
    
    """ def constrain(self, neighbourPossibilities, direction):
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

            # ✅ Remove any invalid possibilities
            for possibility in self.possibilities.copy():
                if possibility not in connectors:
                    self.possibilities.remove(possibility)
                    reduced = True

            self.entropy = len(self.possibilities)

        return reduced
 """
"""  def constrain(self, neighbourPossibilities, direction):
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
                if neighbourPossibility in adjacency_rules:
                    connectors |= adjacency_rules[neighbourPossibility][opposite]

            # ❌ Contradiction: no allowed tiles based on neighbor's constraints
            if not connectors:
                self.possibilities = []
                self.entropy = 0
                return True

            # ✅ Remove any invalid possibilities
            for possibility in self.possibilities.copy():
                if possibility not in connectors:
                    self.possibilities.remove(possibility)
                    reduced = True

            # ✅ Update entropy after reduction
            self.entropy = len(self.possibilities)

        return reduced
 """
