# ClassTile.py
import random
from Config import * # Import the central config

class Tile:
    """Represents a single tile in the WFC grid."""
    def __init__(self, x, y):
        self.is_right_boundary = False
        self.is_left_boundary = False
        self.x = x
        self.y = y
        # Initial possibilities depend on the phase, set by ClassWorld or SokobanInjector
        self.possibilities = []
        self.entropy = 0
        self.neighbours = {} # Dict: direction -> Tile
        self.is_path = False # Flag for Phase 1 solution path
        self.is_sokoban_area = False # Flag for Phase 2 puzzle area

    def addNeighbour(self, direction, tile):
        """Adds a neighboring tile."""
        self.neighbours[direction] = tile

    def getNeighbour(self, direction):
        """Gets the neighbor in a specific direction."""
        return self.neighbours.get(direction)

    def getDirections(self):
        """Gets a list of directions where neighbors exist."""
        return list(self.neighbours.keys())

    def getPossibilities(self):
        """Gets the current list of possible tile IDs."""
        return self.possibilities

    def collapse(self, weights_dict):
        """
        Collapses the tile to a single possibility based on weights.

        Args:
            weights_dict (dict): A dictionary mapping tile IDs to their weights
                                 for the current WFC phase.
        """
        """
        if not self.possibilities:
            print(f"ERROR: Attempting to collapse tile ({self.x}, {self.y}) with no possibilities!")
            self.entropy = 0 # Mark as collapsed (though invalidly)
            return

        # Filter possibilities that actually exist in the weights dictionary
        valid_possibilities = [p for p in self.possibilities if p in weights_dict]
        if not valid_possibilities:
             # Fallback: if no possibilities have weights, choose randomly from original set
             if self.possibilities:
                 print(f"Warning: No weights found for possibilities {self.possibilities} at ({self.x}, {self.y}). Choosing randomly.")
                 self.possibilities = random.choices(self.possibilities, k=1)
             else:
                 # This case should ideally not happen if the initial check passed
                 print(f"ERROR: Tile ({self.x}, {self.y}) has no possibilities left after weight filtering.")
                 self.possibilities = [] # Collapse to empty state
        else:
            # Get weights corresponding to the valid possibilities
            weights = [weights_dict[p] for p in valid_possibilities]
            # Perform weighted random choice
            self.possibilities = random.choices(valid_possibilities, weights=weights, k=1)

        self.entropy = 0 # Mark as collapsed
        """
        weights = [weights_dict[possibility] for possibility in self.possibilities]
        self.possibilities = random.choices(self.possibilities, weights=weights, k=1)
        self.entropy = 0

    def constrain(self, neighbourPossibilities, direction, adjacency_rules):
        """
        Reduces possibilities based on a neighbor's state using specific adjacency rules.

        Args:
            neighbourPossibilities (list): List of possible IDs for the neighbor tile.
            direction (int): The direction FROM this tile TO the neighbor (e.g., Config.NORTH).
            adjacency_rules (dict): The adjacency rules dictionary for the current phase.

        Returns:
            bool: True if possibilities were reduced, False otherwise.
        """
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
             # apply left/right path‐boundary restrictions if flagged
            if self.is_left_boundary:
                self.possibilities = [
                    p for p in self.possibilities
                    if p not in INNER_BOUNDARIES_LEFT_RESTRICT
                ]
                self.entropy = len(self.possibilities)
                if self.entropy == 0:
                    return False
            elif self.is_right_boundary:
                self.possibilities = [
                    p for p in self.possibilities
                    if p not in INNER_BOUNDARIES_RIGHT_RESTRICT
                ]
                self.entropy = len(self.possibilities)
                if self.entropy == 0:
                    return False
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
        if self.entropy == 0: # Already collapsed
            return False

        # Determine the direction FROM the neighbor TO this tile
        opposite_direction = (direction + 2) % 4

        # Collect all tile IDs that are allowed TO BE AT THIS TILE'S LOCATION,
        # given the neighbor's possibilities and the direction from the neighbor.
        allowed_here = set()
        for neighbor_tile_id in neighbourPossibilities:
            if neighbor_tile_id in adjacency_rules:
                # Find what tiles are allowed in the 'opposite_direction' of the neighbor
                allowed_neighbors = adjacency_rules[neighbor_tile_id].get(opposite_direction, set())
                allowed_here.update(allowed_neighbors)
            # else: tile not in rules, cannot constrain based on it

        # Filter current possibilities
        initial_count = len(self.possibilities)
        self.possibilities = [p for p in self.possibilities if p in allowed_here]

        # Update entropy and check if reduced
        self.entropy = len(self.possibilities)
        if self.entropy < initial_count:
            reduced = True

        # Check for contradiction
        if self.entropy == 0:
            print(f"WARNING: Contradiction detected at ({self.x}, {self.y}) due to neighbor constraint (direction={direction}). Possibilities became empty.")
            # Keep possibilities empty to signify contradiction
            reduced = True # It was reduced (to zero)

        return reduced
    """
