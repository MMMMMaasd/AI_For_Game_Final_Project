import random
from ClassTile import Tile
from ClassStack import Stack
from Config import *


class World:

    def __init__(self, sizeX, sizeY):
        self.cols = sizeX
        self.rows = sizeY

        self.tileRows = []
        for y in range(sizeY):
            tiles = []
            for x in range(sizeX):
                tile = Tile(x, y)
                tiles.append(tile)
            self.tileRows.append(tiles)

        # Connect neighboring tiles
        for y in range(sizeY):
            for x in range(sizeX):
                tile = self.tileRows[y][x]
                if y > 0:
                    tile.addNeighbour(NORTH, self.tileRows[y - 1][x])
                if x < sizeX - 1:
                    tile.addNeighbour(EAST, self.tileRows[y][x + 1])
                if y < sizeY - 1:
                    tile.addNeighbour(SOUTH, self.tileRows[y + 1][x])
                if x > 0:
                    tile.addNeighbour(WEST, self.tileRows[y][x - 1])

    def getEntropy(self, x, y):
        return self.tileRows[y][x].entropy

    def getType(self, x, y):
        if self.tileRows[y][x].entropy == 0:
            return self.tileRows[y][x].possibilities[0]
        return None  # or return a default value

    def getLowestEntropy(self):
        lowestEntropy = float('inf')
        for y in range(self.rows):
            for x in range(self.cols):
                entropy = self.tileRows[y][x].entropy
                if 0 < entropy < lowestEntropy:
                    lowestEntropy = entropy
        return lowestEntropy

    def getTilesLowestEntropy(self):
        lowestEntropy = float('inf')
        tileList = []

        for y in range(self.rows):
            for x in range(self.cols):
                tile = self.tileRows[y][x]
                if tile.entropy > 0:
                    if tile.entropy < lowestEntropy:
                        tileList.clear()
                        lowestEntropy = tile.entropy
                    if tile.entropy == lowestEntropy:
                        tileList.append(tile)
        return tileList

    def waveFunctionCollapse(self):
        tilesLowestEntropy = self.getTilesLowestEntropy()

        if not tilesLowestEntropy:
            return 0  # Done

        tileToCollapse = random.choice(tilesLowestEntropy)
        tileToCollapse.collapse()

        stack = Stack()
        stack.push(tileToCollapse)

        while not stack.is_empty():
            tile = stack.pop()
            tilePossibilities = tile.getPossibilities()
            directions = tile.getDirections()

            for direction in directions:
                neighbour = tile.getNeighbour(direction)
                if neighbour.entropy != 0:
                    reduced = neighbour.constrain(tilePossibilities, direction)
                    if reduced:
                        stack.push(neighbour)  # Propagate constraint

        return 1
