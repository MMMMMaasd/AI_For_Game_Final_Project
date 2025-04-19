from Config import NORTH, EAST, SOUTH, WEST, adjacency_rules1, path_only_rules

def constrain_path(self, neighbourPossibilities, direction):
    if self.entropy == 0:
        return False

    # Determine the opposite direction
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

    # Gather allowed connectors based on the neighbor's possibilities
    connectors = set()
    for neighbor_tile in neighbourPossibilities:
        if neighbor_tile in path_only_rules:
            connectors |= path_only_rules[neighbor_tile][opposite]

    # If no allowed connector exists, collapse to contradiction
    if not connectors:
        print(f"⚠️ Contradiction at ({self.x}, {self.y}): no allowed tiles from neighbors {neighbourPossibilities}")
        self.possibilities = []
        self.entropy = 0
        return True

    reduced = False
    for p in self.possibilities.copy():
        if p not in connectors:
            self.possibilities.remove(p)
            reduced = True

    self.entropy = len(self.possibilities)
    return reduced

def constrain_full(self, neighbourPossibilities, direction):
    if self.entropy == 0:
        return False

    # Determine the opposite direction
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

    # Use full adjacency rules
    connectors = set()
    for neighbor_tile in neighbourPossibilities:
        if neighbor_tile in adjacency_rules1:
            connectors |= adjacency_rules1[neighbor_tile][opposite]

    # If no valid connectors, collapse to contradiction
    if not connectors:
        print(f"⚠️ Contradiction at Second WFC ({self.x}, {self.y}): no allowed tiles from neighbors {neighbourPossibilities}")
        self.possibilities = []
        self.entropy = 0
        return True

    reduced = False
    for p in self.possibilities.copy():
        if p not in connectors:
            self.possibilities.remove(p)
            reduced = True

    self.entropy = len(self.possibilities)
    return reduced