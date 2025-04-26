# SokobanInjector.py
import random
import Config

def inject_sokoban_puzzle(world, path_coords, size=5):
    """
    Injects a Sokoban puzzle onto the maze path.

    Args:
        world (World): The world object, assumed to have completed Phase 1 maze generation.
        path_coords (list): List of (row, col) tuples representing the solution path.
        size (int): The approximate size (width/height) of the Sokoban area.

    Returns:
        list: Coordinates (x, y) of the injected region, or None if injection failed.
    """
    if not path_coords:
        print("Error: Cannot inject Sokoban puzzle without a path.")
        return None

    # 1. Choose injection center on the path (avoid start/end)
    if len(path_coords) < 3:
        idx = len(path_coords) // 2
    else:
        idx = random.randint(1, len(path_coords) - 2)
    center_row, center_col = path_coords[idx]
    print(f"Injecting Sokoban puzzle centered at: ({center_row}, {center_col})")

    # 2. Define & clamp region
    half = size // 2
    min_r, max_r = max(0, center_row - half), min(world.rows - 1, center_row + half)
    min_c, max_c = max(0, center_col - half), min(world.cols - 1, center_col + half)

    region_tiles = []
    region_coords = []
    for r in range(min_r, max_r + 1):
        for c in range(min_c, max_c + 1):
            t = world.get_tile(c, r)
            if t:
                region_tiles.append(t)
                region_coords.append((c, r))

    if not region_tiles:
        print("Error: Injection region is empty.")
        return None

    print(f"Injection region: {len(region_tiles)} tiles")

    # 3. Reset possibilities in region to only Sokoban‐relevant set
    domain = list(Config.SOKOBAN_ALLOWED_TILES | Config.TILE_BOULDER_SPOTS)
    for t in region_tiles:
        t.possibilities = domain.copy()
        t.entropy = len(t.possibilities)
        t.is_sokoban_area = True

    # 4. Find candidate seed spots (prefer original path)
    seeds = [world.get_tile(c, r) for (r, c) in [(pr, pc) for pr,pc in path_coords
             if min_r <= pr <= max_r and min_c <= pc <= max_c]]
    if not seeds:
        seeds = region_tiles
        print("Warning: No path‐tiles in region; seeding randomly.")

    if len(seeds) < 2:
        print(f"Error: Need at least 2 seeds, have {len(seeds)}")
        return None

    random.shuffle(seeds)

    # 5a. Seed a hole (boulder spot) using one of your Tanibo hole IDs
    hole_tile = seeds.pop()
    hole_id   = random.choice(list(Config.TILE_BOULDER_SPOTS))
    hole_tile.possibilities = [hole_id]
    hole_tile.entropy       = 0
    print(f"Seeded hole at ({hole_tile.x}, {hole_tile.y}) → tile {hole_id}")

    # 5b. Seed a box
    box_tile = seeds.pop()
    box_tile.possibilities = [Config.SOKOBAN_BOX_ID]
    box_tile.entropy       = 0
    print(f"Seeded Box at ({box_tile.x}, {box_tile.y})")

    # 6. Run local WFC on only the Sokoban area
    print("Running local Sokoban‐area WFC…")
    world.runWFC(
        adjacency_rules=Config.adjacency_rules_sokoban,
        weights=Config.tile_weights_sokoban,
        region=region_coords
    )
    print("Sokoban WFC complete.")

    return region_coords
