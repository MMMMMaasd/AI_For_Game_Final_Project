import random
import Config

def inject_sokoban_puzzle(world, path_coords, size=5, override_center=None):
    """
    Injects a Sokoban puzzle onto the maze path.

    Args:
        world (World): The world object, assumed to be collapsed from Phase 1.
        path_coords (list): List of (row, col) tuples representing the solution path.
        size (int): The approximate size (width/height) of the Sokoban area.
        override_center (tuple, optional): If given, force the puzzle to center on (row, col).

    Returns:
        list: Coordinates (x, y) of the injected region, or None if injection failed.
    """
    if not path_coords:
        print("Error: Cannot inject Sokoban puzzle without a path.")
        return None

    # 1. Select Injection Point (allow override)
    if override_center:
        center_row, center_col = override_center
    else:
        if len(path_coords) < 3:
            idx = len(path_coords) // 2
        else:
            idx = random.randint(1, len(path_coords) - 2)
        center_row, center_col = path_coords[idx]
    print(f"Injecting Sokoban puzzle centered at: ({center_row}, {center_col})")

    # 2. Define & clamp region
    half = size // 2
    min_r = max(0, center_row - half)
    max_r = min(world.rows - 1, center_row + half)
    min_c = max(0, center_col - half)
    max_c = min(world.cols - 1, center_col + half)

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
    domain = list(Config.SOKOBAN_ALLOWED_TILES)
    for t in region_tiles:
        t.possibilities = domain.copy()
        t.entropy = len(t.possibilities)
        t.is_sokoban_area = True

    # 4. Seed hole(s) and box(es)
    # 4a: pick one hole ID and one tile to seed
    hole_tile = random.choice(region_tiles)
    hole_id = random.choice(list(Config.TILE_BOULDER_SPOTS))
    hole_tile.possibilities = [hole_id]
    hole_tile.entropy = 0
    print(f"Seeded hole at ({hole_tile.x}, {hole_tile.y}) → tile {hole_id}")

    # 4b: pick another tile for the box
    box_tile = random.choice([t for t in region_tiles if t is not hole_tile])
    box_tile.possibilities = [Config.SOKOBAN_BOX_ID]
    box_tile.entropy = 0
    print(f"Seeded Box at ({box_tile.x}, {box_tile.y})")

    # 5. Run local WFC on only the Sokoban area
    print("Running local Sokoban‐area WFC…")
    world.runWFC(
        adjacency_rules=Config.adjacency_rules_sokoban,
        weights=Config.tile_weights_sokoban,
        region=region_coords
    )
    print("Sokoban WFC complete.")

    return region_coords
