import random
from ClassTile import Tile
from ClassStack import Stack
from Config import *
from Config import PATH_TILES
from Constraint import constrain_path, constrain_full


class World:

    def __init__(self, sizeX, sizeY):
        self.cols = sizeX
        self.rows = sizeY
        self.last_collapsed_tile = None
        self.tileRows = []
        """ for y in range(sizeY):
            tiles = []
            for x in range(sizeX):
                tile = Tile(x, y)
                tiles.append(tile)
            self.tileRows.append(tiles) """

        for y in range(sizeY):
            tiles = []
            for x in range(sizeX):
                tile = Tile(x, y)
                tile.possibilities = list(PATH_TILES)  # Only allow path tiles
                tile.entropy = len(tile.possibilities)
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

    """ def getType(self, x, y):
        if self.tileRows[y][x].entropy == 0:
            return self.tileRows[y][x].possibilities[0]
        return None  # or return a default value
 """
    
    def getType(self, x, y):
        tile = self.tileRows[y][x]
        if tile.entropy == 0 and tile.possibilities:
            return tile.possibilities[0]
        return None  # or a default tile ID


    def getLowestEntropy(self):
        lowestEntropy = float('inf')
        for y in range(self.rows):
            for x in range(self.cols):
                entropy = self.tileRows[y][x].entropy
                if 0 < entropy < lowestEntropy:
                    lowestEntropy = entropy
        return lowestEntropy
    

    """ def getTilesLowestEntropy(self):
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
 """
    """ def waveFunctionCollapse(self):
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
     """  
    """ def waveFunctionCollapse(self):
        tilesLowestEntropy = self.getTilesLowestEntropy()

        if not tilesLowestEntropy:
            return 0  # Done

        tileToCollapse = random.choice(tilesLowestEntropy)
        tileToCollapse.collapse()
        self.last_collapsed_tile = tileToCollapse

        # 🛑 Stop if top row is reached
        if tileToCollapse in self.tileRows[0]:
            return 0

        stack = Stack()
        stack.push(tileToCollapse)

        while not stack.is_empty():
            tile = stack.pop()
            tilePossibilities = tile.getPossibilities()
            directions = tile.getDirections()

            # Define preferred direction order: N, E, W, S
            weighted_directions = [NORTH]*4 + [EAST]*2 + [WEST]*2 + [SOUTH]
            random.shuffle(weighted_directions)

            # Filter valid directions based on the current tile's neighbors
            directions = tile.getDirections()
            preferred_order = [d for d in weighted_directions if d in directions]

            for direction in preferred_order:
                if direction in directions:
                    neighbour = tile.getNeighbour(direction)
                    if neighbour.entropy != 0:
                        reduced = neighbour.constrain(tilePossibilities, direction)
                        if reduced:
                            stack.push(neighbour)


        return 1
 """
    
    def waveFunctionCollapse(self, weights_override=None):
        # print(weights_override)
        tilesLowestEntropy = self.getTilesLowestEntropy()

        if not tilesLowestEntropy:
            return 0  # Done

        tileToCollapse = random.choice(tilesLowestEntropy)
        tileToCollapse.collapse(weights_override)
        self.last_collapsed_tile = tileToCollapse

        # 🛑 Stop if top row is reached
        if tileToCollapse in self.tileRows[0]:
            return 0

        stack = Stack()
        stack.push(tileToCollapse)

        while not stack.is_empty():
            tile = stack.pop()
            tilePossibilities = tile.getPossibilities()
            directions = tile.getDirections()

            # Define preferred direction order: N, E, W, S
            weighted_directions = [NORTH]*20 + [EAST]*20 + [WEST]*4 + [SOUTH]
            random.shuffle(weighted_directions)

            # Filter valid directions based on the current tile's neighbors
            directions = tile.getDirections()
            preferred_order = [d for d in weighted_directions if d in directions]

            for direction in preferred_order:
                if direction in directions:
                    neighbour = tile.getNeighbour(direction)
                    if neighbour.entropy != 0:
                        reduced = neighbour.constrain_func(tilePossibilities, direction)
                        if reduced:
                            stack.push(neighbour)

        return 1


    def getTilesLowestEntropy(self):
        def find_uncollapsed_neighbor_chain(origin_tile, depth=2):
            """ Recursively look for the nearest uncollapsed neighbor within a limited depth """
            frontier = [origin_tile]
            visited = set()

            for _ in range(depth):
                next_frontier = []
                for tile in frontier:
                    if tile in visited:
                        continue
                    visited.add(tile)

                    for neighbor in tile.neighbours.values():
                        if neighbor.entropy > 0:
                            return [neighbor]  # Found a valid next tile to collapse

                        next_frontier.append(neighbor)
                frontier = next_frontier

            return []  # No valid uncollapsed neighbors found

        # --- First: try adjacent to last collapsed tile ---
        if self.last_collapsed_tile:
            neighbors = list(self.last_collapsed_tile.neighbours.values())
            random.shuffle(neighbors)

            for neighbor in neighbors:
                if neighbor.entropy > 0:
                    return [neighbor]

            # --- Second: recurse into neighbor chains (depth 2 or more) ---
            deeper = find_uncollapsed_neighbor_chain(self.last_collapsed_tile, depth=3)
            if deeper:
                return deeper

        # --- Final fallback: global least entropy search ---
        lowestEntropy = float('inf')
        tileList = []

        for y in range(self.rows):
            for x in range(self.cols):
                tile = self.tileRows[y][x]
                if 0 < tile.entropy < lowestEntropy:
                    lowestEntropy = tile.entropy
                    tileList = [tile]
                elif tile.entropy == lowestEntropy:
                    tileList.append(tile)

        return tileList
    def seed_path_start(self, path_tile_id):
        """Force a starting tile at a random position on the bottom row."""
        import random
        start_x = random.randint(0, self.cols - 1)
        start_y = self.rows - 1
        tile = self.tileRows[start_y][start_x]
        tile.possibilities = [path_tile_id]
        tile.entropy = 0
        self.last_collapsed_tile = tile  # Set it to guide the first step

    """ def seed_path_end(self, path_tile_id):
        # Force an end tile on a random position in the top row.
        import random
        end_x = random.randint(0, self.cols - 1)
        end_y = 0
        tile = self.tileRows[end_y][end_x]
        tile.possibilities = [path_tile_id]
        tile.entropy = 0 """

    """ def prepare_for_second_pass(self, all_tile_ids):
        from ClassStack import Stack

        stack = Stack()

        for y in range(self.rows):
            for x in range(self.cols):
                tile = self.tileRows[y][x]

                if tile.entropy == 0 and tile.possibilities:
                    # Already collapsed from first pass — use it to start propagation
                    stack.push(tile)
                else:
                    # Reset everything else
                    tile.possibilities = list(all_tile_ids)
                    tile.entropy = len(tile.possibilities)

        # Now propagate constraints from collapsed path tiles
        while not stack.is_empty():
            tile = stack.pop()
            tilePossibilities = tile.getPossibilities()
            directions = tile.getDirections()

            for direction in directions:
                neighbor = tile.getNeighbour(direction)
                if neighbor.entropy != 0:
                    if neighbor.constrain_func:
                        reduced = neighbor.constrain_func(tilePossibilities, direction)
                        if reduced:
                            stack.push(neighbor)
                    else:
                        raise ValueError(f"No constraint function set for tile at ({neighbor.x}, {neighbor.y})")
     """                    

    def prepare_for_second_pass(self):
        # Go through all tiles
        for row in self.tileRows:
            for tile in row:
                if tile.entropy == 0:
                    # Already collapsed → keep it
                    continue
                else:
                    # Reset uncollapsed tiles' possibilities to all full tile set
                    tile.possibilities = list(adjacency_rules1.keys())
                    tile.entropy = len(tile.possibilities)

        # Re-propagate constraints from collapsed neighbors
        from ClassStack import Stack
        stack = Stack()

        for row in self.tileRows:
            for tile in row:
                if tile.entropy == 0:
                    stack.push(tile)

        while not stack.is_empty():
            tile = stack.pop()
            tilePossibilities = tile.getPossibilities()
            for direction in tile.getDirections():
                neighbor = tile.getNeighbour(direction)
                if neighbor.entropy > 0:
                    reduced = neighbor.constrain_func(tilePossibilities, direction)
                    if reduced:
                        stack.push(neighbor)

    """ def set_constrain_mode(self, mode):
        if mode == "path":
            from Constraint import constrain_path
            constraint = constrain_path
        elif mode == "full":
            from Constraint import constrain_full
            constraint = constrain_full
        else:
            raise ValueError("Unknown constraint mode")

        for row in self.tileRows:
            for tile in row:
                tile.constrain_func = constraint
 """
    
    def set_constrain_mode(self, mode):
        from Constraint import constrain_path, constrain_full
        for row in self.tileRows:
            for tile in row:
                if mode == "path":
                    tile.constrain_func = constrain_path.__get__(tile)
                elif mode == "full":
                    tile.constrain_func = constrain_full.__get__(tile)
                else:
                    raise ValueError(f"Unknown constraint mode: {mode}")




    def debug_uncollapsed_tiles(self):
        print("Uncollapsed or broken tiles:")
        for y in range(self.rows):
            for x in range(self.cols):
                tile = self.tileRows[y][x]
                if tile.entropy > 0:
                    print(f" - ({x}, {y}) not collapsed (entropy={tile.entropy})")
                elif not tile.possibilities:
                    print(f" - ({x}, {y}) collapsed but EMPTY possibilities ❌")


