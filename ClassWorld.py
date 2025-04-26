# ClassWorld.py
import random
from ClassTile import Tile
from ClassStack import Stack
import Config # Import the central config

class World:
    """Manages the grid of tiles and the WFC algorithm."""

    def __init__(self, sizeX, sizeY):
        """Initializes the world grid."""
        self.cols = sizeX
        self.rows = sizeY
        self.tileRows = [] # 2D list of Tile objects

        # Create tiles
        for y in range(sizeY):
            row_tiles = [Tile(x, y) for x in range(sizeX)]
            self.tileRows.append(row_tiles)

        # Connect neighbors
        for y in range(sizeY):
            for x in range(sizeX):
                tile = self.tileRows[y][x]
                # Check and add neighbors in N, E, S, W order
                if y > 0:
                    tile.addNeighbour(Config.NORTH, self.tileRows[y - 1][x])
                if x < sizeX - 1:
                    tile.addNeighbour(Config.EAST, self.tileRows[y][x + 1])
                if y < sizeY - 1:
                    tile.addNeighbour(Config.SOUTH, self.tileRows[y + 1][x])
                if x > 0:
                    tile.addNeighbour(Config.WEST, self.tileRows[y][x - 1])

    def get_tile(self, x, y):
         """Safely gets a tile at given coordinates."""
         if 0 <= y < self.rows and 0 <= x < self.cols:
             return self.tileRows[y][x]
         return None

    def getEntropy(self, x, y):
        """Gets the entropy of a tile at (x, y)."""
        tile = self.get_tile(x,y)
        return tile.entropy if tile else -1 # Return -1 for out of bounds

    def getType(self, x, y):
        """Gets the collapsed type of a tile at (x, y)."""
        tile = self.get_tile(x,y)
        if tile and tile.entropy == 0 and tile.possibilities:
            return tile.possibilities[0]
        return None # Return None if not collapsed, invalid, or out of bounds

    def getLowestEntropyTiles(self, region=None):
        """
        Finds tiles with the lowest entropy > 0, optionally within a region.

        Args:
            region (list, optional): List of (x, y) tuples defining the area to search.
                                     If None, searches the whole grid.

        Returns:
            list: A list of Tile objects with the lowest entropy.
        """
        lowest_entropy = float('inf')
        candidate_tiles = []

        if region:
            coords_to_check = region
        else:
            coords_to_check = ((x, y) for y in range(self.rows) for x in range(self.cols))

        for x, y in coords_to_check:
            tile = self.get_tile(x, y)
            if tile and tile.entropy > 0: # Only consider uncollapsed tiles
                if tile.entropy < lowest_entropy:
                    lowest_entropy = tile.entropy
                    candidate_tiles = [tile]
                elif tile.entropy == lowest_entropy:
                    candidate_tiles.append(tile)

        return candidate_tiles

    def waveFunctionCollapseStep(self, adjacency_rules, weights, region=None):
        """
        Performs one step of the WFC algorithm.

        Args:
            adjacency_rules (dict): Adjacency rules for the current phase.
            weights (dict): Tile weights for the current phase.
            region (list, optional): List of (x, y) tuples defining the area
                                     where collapse should occur. If None, uses
                                     the whole grid.

        Returns:
            int: 0 if collapse is complete (or failed), 1 if progress was made.
        """
        # 1. Observation: Find the tile(s) with the lowest entropy
        lowest_entropy_tiles = self.getLowestEntropyTiles(region=region)

        if not lowest_entropy_tiles:
            # Check if ALL tiles in the region (or grid) are collapsed
            coords_to_check = region if region else ((x, y) for y in range(self.rows) for x in range(self.cols))
            all_collapsed = True
            contradiction = False
            for x, y in coords_to_check:
                tile = self.get_tile(x, y)
                if tile and tile.entropy > 0:
                    all_collapsed = False
                    break
                if tile and tile.entropy == 0 and not tile.possibilities:
                    contradiction = True # Found a contradiction state

            if contradiction:
                print("WFC failed due to contradiction.")
                return 0 # Failed
            if all_collapsed:
                # print("WFC complete for region." if region else "WFC complete for grid.")
                return 0 # Done
            else:
                # This case might happen if entropy calculation is off or region logic is complex
                print("Warning: No lowest entropy tiles found, but not all tiles are collapsed.")
                return 0 # Stuck or error


        # 2. Collapse: Choose one tile randomly and collapse it
        tile_to_collapse = random.choice(lowest_entropy_tiles)
        tile_to_collapse.collapse(weights)

        # Check if collapse resulted in an invalid state (empty possibilities)
        if not tile_to_collapse.possibilities:
             print(f"ERROR: Tile ({tile_to_collapse.x}, {tile_to_collapse.y}) collapsed to an empty state!")
             # Mark as contradiction - WFC should stop
             return 0 # Failed state


        # 3. Propagation: Update neighbors' possibilities
        propagation_stack = Stack()
        propagation_stack.push(tile_to_collapse)

        while not propagation_stack.is_empty():
            current_tile = propagation_stack.pop()
            current_possibilities = current_tile.getPossibilities()

            # Propagate to neighbors
            for direction, neighbor_tile in current_tile.neighbours.items():
                # Only propagate if neighbor is within the target region (if specified)
                # and is not already collapsed
                if neighbor_tile.entropy > 0 and (region is None or (neighbor_tile.x, neighbor_tile.y) in region):
                    reduced = neighbor_tile.constrain(current_possibilities, direction, adjacency_rules)

                    if reduced:
                        # If neighbor possibilities were reduced, push it onto the stack
                        # to propagate further from it.
                        propagation_stack.push(neighbor_tile)

                        # Check if the neighbor collapsed into a contradiction
                        if neighbor_tile.entropy == 0 and not neighbor_tile.possibilities:
                            print(f"WFC failed: Contradiction propagated to ({neighbor_tile.x}, {neighbor_tile.y}).")
                            return 0 # Failed state


        return 1 # Progress was made

    def runWFC(self, adjacency_rules, weights, region=None):
         """Runs the WFC algorithm until completion or failure."""
         steps = 0
         max_steps = self.rows * self.cols * 10 # Safety break
         while self.waveFunctionCollapseStep(adjacency_rules, weights, region) == 1:
             steps += 1
             if steps > max_steps:
                 print("ERROR: WFC exceeded maximum steps. Aborting.")
                 break
         print(f"WFC finished in {steps} steps.")


