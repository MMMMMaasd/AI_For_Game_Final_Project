import random
import Config
from utils import *
from typing import List, Tuple, Optional, Any
from SokobanLevel import Node, SokobanLevel
from generator import *
from pathfinder import *

def inject_sokoban_puzzle(world, path_coords, size=5, seeds=None):
    """
    Injects a Sokoban puzzle onto the maze.

    Args:
        world (World): The world after Phase 1 maze generation.
        path_coords (list): Solution-path (row, col) tuples.
        size (int): Width/height of injection region (unused here—seeds drive region).
        seeds (list of (r, c), optional): Explicit hole/stone seed coords.
    Returns:
        list of (col, row) coords filled by the puzzle, or None on error.
    """

    # Must have either a path or explicit seeds
    if seeds is None and not path_coords:
        print("Error: need solution_path or explicit seeds.")
        return None

    # If no explicit seeds, pick two distinct path tiles around midpoint
    if seeds is None:
        mid = len(path_coords) // 2
        i1 = min(max(1, mid - 1), len(path_coords) - 2)
        i2 = min(max(1, mid + 1), len(path_coords) - 2)
        seeds = [path_coords[i1], path_coords[i2]]

    # Dedupe and validate
    seeds = list(dict.fromkeys(seeds))
    if len(seeds) < 2:
        print(f"Error: need ≥2 seeds, got {len(seeds)}")
        return None

    print(f"Injecting Sokoban puzzle with seeds {seeds}")

    # 0) Convert any adjacent trees into Sokoban walls (ID=5)
    Config.SOKOBAN_WALL_ID = 5
    for (r, c) in seeds:
        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < world.rows and 0 <= nc < world.cols:
                tid = world.getType(nc, nr)
                if tid not in Config.FOREST_FLOOR_TILES:
                    t = world.get_tile(nc, nr)
                    t.possibilities   = [Config.SOKOBAN_WALL_ID]
                    t.entropy         = 0
                    t.is_sokoban_area = True
                    print(f"Converted tree at ({nr},{nc}) into Sokoban wall")

    # 1) Build the tiny cross-region: each seed + its orthogonal neighbors (floor-only)
    tiles_to_reset = set()
    for (r, c) in seeds:
        tiles_to_reset.add((r, c))
        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < world.rows and 0 <= nc < world.cols:
                if world.getType(nc, nr) in Config.FOREST_FLOOR_TILES:
                    tiles_to_reset.add((nr, nc))

    if not tiles_to_reset:
        print("Error: no valid floor tiles around seeds; aborting.")
        return None

    region_coords = [(c, r) for (r, c) in tiles_to_reset]
    print(f"Injection region (cross) size: {len(region_coords)} tiles")

    # 2) Reset those tiles to Sokoban domain
    domain = [
        Config.SOKOBAN_WALL_ID,
        Config.SOKOBAN_FLOOR_ID,
        Config.SOKOBAN_BOX_ID,
        *Config.TILE_BOULDER_SPOTS
    ]
    for (r, c) in tiles_to_reset:
        t = world.get_tile(c, r)
        t.possibilities   = domain.copy()
        t.entropy         = len(domain)
        t.is_sokoban_area = True

    # 3) Place exactly one hole/stone pair (adjust num_pairs if desired)
    num_pairs = 1
    print(f"Creating {num_pairs} hole-stone pair")
    available = list(tiles_to_reset)
    random.shuffle(available)

    # hole
    hole_r, hole_c = available.pop()
    hole_tile = world.get_tile(hole_c, hole_r)
    hole_id   = random.choice(list(Config.TILE_BOULDER_SPOTS))
    hole_tile.possibilities = [hole_id]
    hole_tile.entropy       = 0
    print(f" Seeded hole at ({hole_r},{hole_c})")

    # stone
    if not available:
        print("Error: no tile left to place stone; aborting.")
        return None
    stone_r, stone_c = available.pop()
    stone_tile = world.get_tile(stone_c, stone_r)
    stone_tile.possibilities = [Config.SOKOBAN_BOX_ID]
    stone_tile.entropy       = 0
    print(f" Seeded box at ({stone_r},{stone_c})")

    # 4) Run WFC only over that minimal region
    world.runWFC(
        adjacency_rules = Config.adjacency_rules_sokoban,
        weights         = Config.tile_weights_sokoban,
        region          = region_coords
    )

    print("Sokoban WFC complete.")
    return region_coords

def world_to_sokoban_level(world, region_coords):
    # Find all boxes and holes in the region
    boxes = []
    holes = []
    for (c, r) in region_coords:
        tile = world.get_tile(c, r)
        if tile.entropy == 0:
            if tile.possibilities[0] == Config.SOKOBAN_BOX_ID:
                boxes.append((c, r))
            elif tile.possibilities[0] in Config.TILE_BOULDER_SPOTS:
                holes.append((c, r))
    
    # Create SokobanLevel with correct box count
    level = SokobanLevel(world.cols, world.rows, len(boxes))
    
    # Clear default walls and set actual walls
    for y in range(world.rows):
        for x in range(world.cols):
            tile = world.get_tile(x, y)
            level.nodes[x][y].wall = False  # Clear default walls
            if tile and tile.entropy == 0:
                tid = tile.possibilities[0]
                level.nodes[x][y].wall = (tid == Config.SOKOBAN_WALL_ID)
    
    # Add boxes and their target holes
    for box, hole in zip(boxes, holes):
        button = Button(hole[0], hole[1])
        level.boxes.append(Box(box[0], box[1], button))
        level.nodes[hole[0]][hole[1]].button = True
    
    # Set player start position (nearest floor to first box)
    if boxes:
        player_pos = find_nearest_floor(world, boxes[0][0], boxes[0][1])
        level.setPlayerPos(player_pos[0], player_pos[1])
    
    return level

def find_nearest_floor(world, start_x, start_y):
    from collections import deque
    
    visited = set()
    queue = deque([(start_x, start_y, [])])
    
    while queue:
        x, y, path = queue.popleft()
        
        # Check if current tile is a valid floor
        tile = world.get_tile(x, y)
        if (tile and tile.entropy == 0 and
            tile.possibilities[0] == Config.SOKOBAN_FLOOR_ID):
            return (x, y)
            
        # Mark as visited
        visited.add((x, y))
        
        # Check neighbors
        for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
            nx, ny = x + dx, y + dy
            if (0 <= nx < world.cols and 0 <= ny < world.rows and
                (nx, ny) not in visited):
                queue.append((nx, ny, path + [(nx, ny)]))
    
    # Fallback: return the original position if no floor found
    return (start_x, start_y)

def validate_and_make_solvable(world, region_coords):
    """Converts the puzzle to a SokobanLevel and runs generatePaths()"""
    level = world_to_sokoban_level(world, region_coords)
    generatePaths(level)
    
    if level.trash:
        return None
    
    # Only modify tiles in the original region_coords
    for (c, r) in region_coords:
        tile = world.get_tile(c, r)
        if level.nodes[c][r].wall:
            tile.possibilities = [Config.SOKOBAN_WALL_ID]
        else:
            tile.possibilities = [Config.SOKOBAN_FLOOR_ID]
        tile.entropy = 0
    
    return region_coords

def get_push_position(box_pos, target_pos):
    """Returns where player needs to stand to push box toward target."""
    bx, by = box_pos
    tx, ty = target_pos
    if tx > bx: return (bx-1, by)  # Push right
    if tx < bx: return (bx+1, by)  # Push left
    if ty > by: return (bx, by-1)  # Push down
    return (bx, by+1)             # Push up
