import random
from collections import deque
import Config
from SokobanInjector import inject_sokoban_puzzle
from ClassWorld import World

def is_connected(world: World, start: tuple[int,int], end: tuple[int,int]) -> bool:
    """
    BFS on the collapsed world: can you walk from start → end on forest-floor (and through holes once injected)?
    """
    rows, cols = world.rows, world.cols
    visited = {start}
    queue = deque([start])

    while queue:
        r, c = queue.popleft()
        if (r, c) == end:
            return True
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                tid = world.getType(nc, nr)
                if tid in Config.FOREST_FLOOR_TILES or tid in Config.TILE_BOULDER_SPOTS:
                    visited.add((nr, nc))
                    queue.append((nr, nc))
    return False

def find_chokepoints(world: World, path: list[tuple[int,int]]) -> list[tuple[int,int]]:
    """
    A chokepoint is any interior path‐tile whose removal disconnects start/end.
    path is list of (row, col) from start→end.
    """
    if len(path) < 3:
        return []

    start, end = path[0], path[-1]
    chokepoints = []

    for r, c in path[1:-1]:
        tile = world.get_tile(c, r)
        # remove it temporarily
        orig_poss, orig_entropy = tile.possibilities, tile.entropy
        tile.possibilities, tile.entropy = [], 0

        if not is_connected(world, start, end):
            chokepoints.append((r, c))

        # restore
        tile.possibilities, tile.entropy = orig_poss, orig_entropy

    return chokepoints

def choose_sokoban_region(
    world: World,
    path: list[tuple[int,int]],
    size: int = 7
) -> list[tuple[int,int]] | None:
    """
    Pick a chokepoint at random, inject there, and return the region coordinates.
    Returns None if no valid chokepoint was found.
    """
    chokepoints = find_chokepoints(world, path)
    random.shuffle(chokepoints)

    for center in chokepoints:
        region = inject_sokoban_puzzle(
            world,
            path,
            size=size,
            override_center=center
        )
        if region:
            print(f"Agent: injected puzzle at chokepoint {center}")
            return region

    print("Agent: no chokepoint injection succeeded")
    return None
