import random
from ClassTile import Tile
from ClassStack import Stack
from Config import *


class World:

    def __init__(self, sizeX, sizeY, maze_tile_grid=None):
        self.cols = sizeX
        self.rows = sizeY
        self.stone_tiles = []
        self.maze_tile_grid = maze_tile_grid

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
        tile = self.tileRows[y][x]

        if tile.entropy == 0:
            if tile.possibilities and tile.possibilities[0] is not None:
                return tile.possibilities[0]
            else:
                print(f"[Warning] Tile at ({x}, {y}) is collapsed but has no valid type. Restarting WFC...")
    
                tile = self.tileRows[y][x]

                print("  This tile's possibilities:", tile.possibilities)
                print("  Neighbor info:")
                directions = tile.getDirections()
                for dir in directions:
                    neighbor = tile.getNeighbour(dir)
                    if neighbor:
                        print(f"    Direction {dir}:")
                        print(f"      Collapsed: {neighbor.entropy == 0}")
                        print(f"      Possibilities: {neighbor.possibilities}")

                self.resetWorld()               # Reset tile states
                self.waveFunctionCollapse()     # Re-run WFC
                return self.getType(x, y)       # Try again after re-collapsing

        return None


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
    
    def addStoneTile(self, x, y, type_id):
        self.stone_tiles.append((x, y, type_id))


    def waveFunctionCollapse(self):
        # === Stone tiles phase: force collapsed tiles and propagate to neighbors ===
        if hasattr(self, "stone_tiles") and self.stone_tiles:
            for x, y, type_id in self.stone_tiles:
                tile = self.tileRows[y][x]
                tile.possibilities = [type_id]
                tile.entropy = 0
                tile.collapsed = True   # 🛑 Critical! Lock preset tiles

                directions = tile.getDirections()
                for direction in directions:
                    neighbour = tile.getNeighbour(direction)
                    if neighbour.entropy != 0:
                        neighbour.constrain(tile.getPossibilities(), direction)

    # Do not clear stone_tiles if you want to allow dynamic adding


            # self.stone_tiles.clear()  # Clear stone tiles after applying

        # === Normal WFC collapse phase ===
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

                    if self.maze_tile_grid is not None:
                        maze_value = self.maze_tile_grid[neighbour.y][neighbour.x]
                        if maze_value == 1 or maze_value == 4 or maze_value == 6:
                            neighbour.possibilities = [p for p in neighbour.possibilities if p in solution_set_tiles]
                            neighbour.entropy = len(neighbour.possibilities)
                        elif maze_value == 7:
                            neighbour.possibilities = [p for p in neighbour.possibilities if p in blocker_set_tiles]
                            neighbour.entropy = len(neighbour.possibilities)
                        else:
                            neighbour.possibilities = [p for p in neighbour.possibilities if p in adjacency_rules.keys()]
                            neighbour.entropy = len(neighbour.possibilities)

                    if reduced:
                        stack.push(neighbour)  # Propagate constraint


        return 1

    
    def resetWorld(self):
        allowed_tiles = set(adjacency_rules.keys()) - {TILE_PLAYER, TILE_GRASS_HOLE, TILE_GRASS_STONE}
        
        for y in range(self.rows):
            for x in range(self.cols):
                tile = self.tileRows[y][x]

                if self.maze_tile_grid is not None:
                    maze_value = self.maze_tile_grid[y][x]

                    if maze_value == 1 or maze_value == 4 or maze_value == 6:
                        # 🎯 If maze is solution path or box neighbor, restrict to solution tiles
                        tile.possibilities = list(solution_set_tiles)
                    elif maze_value == 7:
                        # 🎯 If maze is blocker, restrict to blocker set tiles
                        tile.possibilities = list(blocker_set_tiles)
                    else:
                        tile.possibilities = list(allowed_tiles)
                else:
                    tile.possibilities = list(allowed_tiles)

                tile.entropy = len(tile.possibilities)

