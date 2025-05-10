# michael/main.py

import pygame
import sys
import numpy as np
import Config # your updated Config.py
from ClassWorld import World
from ClassDrawWorld import DrawWorld
from MazeGenerator import generate_maze_and_path # returns (maze_grid, solution_path, tag_grid)

# Import the agent function (now takes an existing World + tag_grid + carved path)
try:
    from agent_before_phase_2 import prepare_puzzle_world
except ImportError:
    print("ERROR: Cannot import 'prepare_puzzle_world'.")
    prepare_puzzle_world = None

# --- Constants for mapping ---
GRASS_ID = Config.TILE_GRASS
WALL_ID = Config.TILE_TREE_MID_MID

# --- Pygame setup ---
pygame.init()
pygame.font.init()
WINDOW_WIDTH = int(Config.WORLD_X * Config.TILESIZE * Config.SCALETILE)
WINDOW_HEIGHT = int(Config.WORLD_Y * Config.TILESIZE * Config.SCALETILE + 40)
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Forest + Sokoban WFC Generator")
clock = pygame.time.Clock()
status_font = pygame.font.Font(pygame.font.get_default_font(), 18)

# --- State ---
world = None
draw_world = None
maze_grid = None # 0=path,1=wall
tile_id_mask = None # GRASS_ID/WALL_ID per cell
tag_grid = None # 0=walk,1=wall,2=path,5=start,6=end,3=box,4=hole
solution_path = None
binary_maze = None # last printed binary map
tile_id_maze = None # last printed tile-ID map
current_phase = "FOREST_READY"
wfc_running = False
show_binary_view = False # toggle for binary drawing
show_tag_view = False # toggle for tag grid visualization

def initialize_world():
    """Phase 0: reset everything."""
    global world, draw_world, maze_grid, tile_id_mask, tag_grid, solution_path
    global binary_maze, tile_id_maze, wfc_running, show_binary_view, show_tag_view, current_phase
    
    world = World(Config.WORLD_X, Config.WORLD_Y)
    world.tile_map= np.zeros((world.rows, world.cols), dtype=int)
    draw_world = DrawWorld(world)
    maze_grid = None
    tile_id_mask = None
    tag_grid = None
    solution_path = None
    binary_maze = None
    tile_id_maze = None
    wfc_running = False
    show_binary_view = False
    show_tag_view = False
    
    # seed every tile with the full forest domain
    for y in range(world.rows):
        for x in range(world.cols):
            t = world.get_tile(x, y)
            if t:
                t.possibilities = list(Config.FOREST_DOMAIN)
                t.entropy = len(Config.FOREST_DOMAIN)
                t.is_path = False
                t.is_left_boundary = False
                t.is_right_boundary = False
    
    current_phase = "FOREST_READY"
    print("Initialized. Press [F] to carve maze & generate forest.")

def set_tree_boundary_rules(path_coords):
    """Mark east/west neighbours of the carved path so the corridor stays clear."""
    path_set = set(path_coords)
    for (r, c) in path_coords:
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r+dr, c+dc
            if not (0 <= nr < world.rows and 0 <= nc < world.cols):
                continue
            if (nr, nc) in path_set:
                continue
            t = world.get_tile(nc, nr)
            if not t:
                continue
            if dc == -1:
                t.is_left_boundary = True
            elif dc == 1:
                t.is_right_boundary = True

def display_maze_matrices(world):
    """
    Extracts and displays:
    1) binary map (0=walkable,1=wall)
    2) full tile-ID map
    """
    rows, cols = world.rows, world.cols
    binary = np.zeros((rows, cols), dtype=int)
    tile_ids = np.zeros((rows, cols), dtype=int)
    
    for r in range(rows):
        for c in range(cols):
            tid = world.getType(c, r)
            if tid is None:
                binary[r,c] = -1
                tile_ids[r,c] = -1
            else:
                binary[r,c] = 0 if tid in Config.WALKABLE_TILES else 1
                tile_ids[r,c] = tid
    
    print("\n=== BINARY MAZE (0=walkable, 1=wall) ===")
    for row in binary:
        print(''.join('█' if v==1 else ' ' if v==0 else '?' for v in row))
    
    print("\n=== TILE ID MAZE ===")
    for row in tile_ids:
        print(' '.join(f"{v:4d}" for v in row))
    
    return binary, tile_ids

def draw_binary_maze(surface, binary):
    """Draws the binary maze on-screen."""
    if binary is None:
        return
        
    rows, cols = binary.shape
    cw = WINDOW_WIDTH // cols
    ch = (WINDOW_HEIGHT-40) // rows
    
    for r in range(rows):
        for c in range(cols):
            color = (0,0,0) if binary[r,c]==1 else (255,255,255)
            rect = pygame.Rect(c*cw, r*ch, cw, ch)
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (100,100,100), rect, 1)

def draw_tag_grid(surface, tag_grid):
    """Draws the tag grid representation on-screen."""
    if tag_grid is None:
        return
        
    rows, cols = tag_grid.shape
    cw = WINDOW_WIDTH // cols
    ch = (WINDOW_HEIGHT-40) // rows
    
    for r in range(rows):
        for c in range(cols):
            # Set color based on tag value
            tag = tag_grid[r, c]
            if tag == 0:  # Walkable
                color = (128, 128, 128)  # Gray
            elif tag == 1:  # Wall
                color = (0, 128, 0)      # Green
            elif tag == 2:  # Path
                color = (255, 255, 0)    # Yellow
            elif tag == 3:  # Boulder
                color = (139, 69, 19)    # Brown
            elif tag == 4:  # Hole
                color = (0, 0, 255)      # Blue
            elif tag == 5:  # Start
                color = (255, 0, 0)      # Red
            elif tag == 6:  # End
                color = (128, 0, 128)    # Purple
            else:
                color = (255, 255, 255)  # White (unknown)
                
            rect = pygame.Rect(c * cw, r * ch, cw, ch)
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (50, 50, 50), rect, 1)  # Grid lines
    
    # Highlight solution path if available
    if solution_path:
        for r, c in solution_path:
            rect = pygame.Rect(c * cw, r * ch, cw, ch)
            pygame.draw.rect(surface, (255, 255, 0), rect, 2)  # Yellow outline

# Add this function to main.py to update the tile_map when needed
# --- main.py ------------------------------------------------------
# --- main.py -------------------------------------------------------------
def sync_tile_map_with_world():
    """
    Make world.getType(), world.tile_map and tag_grid agree 100 %.

    After this runs you should never see -1 or '?' in a debug dump.
    """
    BOX_ID   = Config.SOKOBAN_GRID_TO_TILE_MAP[3]   # Tanibo stone / box
    HOLE_ID  = Config.SOKOBAN_GRID_TO_TILE_MAP[2]   # Tanibo hole
    WALKABLE = set(Config.WALKABLE_TILES)

    for r in range(world.rows):
        for c in range(world.cols):
            cell = world.get_tile(c, r)
            if cell is None:
                continue

            # read the raw map id before we overwrite it
            raw_tid = int(world.tile_map[r, c])

            # ------------------------------------------------------------------
            # 1) Pick a *definitive* tile-id for this location
            # ------------------------------------------------------------------
            if cell.entropy == 0 and cell.possibilities:
                # Already collapsed by WFC or Sokoban → keep it
                tid = cell.possibilities[0]
            else:
                tg = tag_grid[r, c]
                if   tg == 3:            # boulder
                    tid = BOX_ID
                elif tg == 4:            # hole
                    tid = HOLE_ID
                elif tg == 1:            # wall / bush
                    tid = Config.SHORT_BUSH
                else:
                    # walkable (0), path (2), start/end (5/6):
                    # preserve whatever was in the map, fallback to grass
                    if raw_tid not in (-1, 0):
                        tid = raw_tid
                    else:
                        tid = Config.TILE_GRASS

            # ------------------------------------------------------------------
            # 2) Write the decision everywhere
            # ------------------------------------------------------------------
            cell.possibilities = [tid]
            cell.entropy       = 0
            world.tile_map[r, c] = tid

            # ------------------------------------------------------------------
            # 3) Keep tag_grid in sync (but preserve 2/3/4/5/6)
            # ------------------------------------------------------------------
            old_tg = tag_grid[r, c]
            if old_tg not in (2, 3, 4, 5, 6):
                if   tid == BOX_ID:
                    tag_grid[r, c] = 3
                elif tid == HOLE_ID:
                    tag_grid[r, c] = 4
                elif tid in WALKABLE:
                    tag_grid[r, c] = 0
                else:
                    tag_grid[r, c] = 1

def run_forest_wfc():
    """Phase 1: carve maze, tag & collapse the path, then WFC until stable."""
    global maze_grid, tile_id_mask, tag_grid, solution_path, binary_maze, tile_id_maze
    global current_phase, wfc_running
    
    if not world:
        current_phase = "FAILED"
        return
    
    current_phase = "FOREST_RUNNING"
    wfc_running = True
    pygame.display.set_caption("Running Forest WFC…")
    
    # 1) carve + tag
    maze_grid, solution_path, tag_grid = generate_maze_and_path(world.rows, world.cols)
    if solution_path is None:
        print("MazeGenerator failed.")
        current_phase = "FAILED"
        wfc_running = False
        return
    
    # 2) corridor vs wall mask
    tile_id_mask = np.where(maze_grid==0, GRASS_ID, WALL_ID)
    
    # 3) collapse solution path to grass
    for (r,c) in solution_path:
        t = world.get_tile(c,r)
        if t:
            t.possibilities = [GRASS_ID]
            t.entropy = 0
            t.is_path = True
    
    set_tree_boundary_rules(solution_path)
    
    # 4) region outside the path
    region = [(c,r)
              for r in range(world.rows)
              for c in range(world.cols)
              if (r,c) not in solution_path]
    
    # 5) WFC retry until no contradictions
    attempt = 0
    while True:
        attempt += 1
        print(f"Forest WFC attempt #{attempt}")
        
        for (c,r) in region:
            t = world.get_tile(c,r)
            if not t: continue
            
            base = list(Config.FOREST_DOMAIN)
            if getattr(t, "is_left_boundary", False):
                base = [p for p in base if p not in Config.INNER_BOUNDARIES_LEFT_RESTRICT]
            if getattr(t, "is_right_boundary", False):
                base = [p for p in base if p not in Config.INNER_BOUNDARIES_RIGHT_RESTRICT]
            
            t.possibilities = base
            t.entropy = len(base)
        
        world.runWFC(
            adjacency_rules = Config.adjacency_rules_forest,
            weights = Config.tile_weights_forest,
            region = region
        )
        
        contradicted = any(
            world.get_tile(c,r).entropy==0
            and not world.get_tile(c,r).possibilities
            for (c,r) in region
        )
        
        if not contradicted:
            print("Forest WFC succeeded.")
            binary_maze, tile_id_maze = display_maze_matrices(world)
            world.tile_map = np.array(tile_id_maze)
            sync_tile_map_with_world()  # Add this line

            # patch tag_grid: any wall→walkable becomes 0
            for rr in range(tag_grid.shape[0]):
                for cc in range(tag_grid.shape[1]):
                    if tag_grid[rr,cc]==1 and tile_id_maze[rr,cc] in Config.WALKABLE_TILES:
                        tag_grid[rr,cc] = 0
                    # If marked as walkable but has non-walkable tile ID
                    elif tag_grid[rr,cc]==0 and tile_id_maze[rr,cc] not in Config.WALKABLE_TILES:
                        tag_grid[rr,cc] = 1
            
            # show the tag grid (0,1,2,5,6)
            print("\n=== TAG GRID (0=walk,1=wall,2=path,5=start,6=end) ===")
            for row in tag_grid:
                print(' '.join(str(v) for v in row))
            
            break
    
    wfc_running = False
    current_phase = "SOKO_READY"
    pygame.display.set_caption("Forest Ready – Press [S] for Sokoban")

def refresh_tags_from_tilemap(tag_grid, tile_map):
    """
    Re-derive tags from the final tile map so logic == visuals.
    Only start(5), end(6) and walls(1) are kept as is.
    """
    for r in range(tag_grid.shape[0]):
        for c in range(tag_grid.shape[1]):
            tid = int(tile_map[r, c])

            if tid == Config.SOKOBAN_GRID_TO_TILE_MAP[3]:      # box
                tag_grid[r, c] = 3
            elif tid == Config.SOKOBAN_GRID_TO_TILE_MAP[2]:    # hole
                tag_grid[r, c] = 4
            elif tag_grid[r, c] in (1, 5, 6):                  # keep walls, start, end
                continue
            elif tid in Config.WALKABLE_TILES:
                tag_grid[r, c] = 0
            else:
                tag_grid[r, c] = 1


def run_sokoban_agent():
    """Phase 2: inject Sokoban, print maps, then restore forest outside puzzle."""
    global world, draw_world, tag_grid, solution_path, binary_maze, tile_id_maze
    global current_phase, wfc_running
    
    if not prepare_puzzle_world:
        current_phase = "FAILED"
        return
    
    current_phase = "SOKO_INJECTING"
    wfc_running = True
    pygame.display.set_caption("Running Sokoban Agent…")
    
    try:
        new_world = prepare_puzzle_world(
            world,
            tag_grid,
            solution_path,
            num_boxes_per_puzzle=3
        )
        refresh_tags_from_tilemap(tag_grid, world.tile_map)

    except Exception as e:
        print("Agent error:", e)
        current_phase = "FAILED"
        wfc_running = False
        return
    
    wfc_running = False
    
    if isinstance(new_world, World):
        world = new_world
        draw_world.world = world
        sync_tile_map_with_world()  # Add this line

        
        # print tag_grid including any 3/4
        print("\n=== TAG GRID AFTER SOKOBAN ===")
        for row in tag_grid:
            print(' '.join(str(v) for v in row))
        
        # print final binary & tile-ID maps
        binary_maze, tile_id_maze = display_maze_matrices(world)
        
        # restore original WFC-chosen tiles outside Sokoban area
        for (r,c), orig in np.ndenumerate(tile_id_maze):
            if tag_grid[r,c] in (3,4):
                continue
            cell = world.get_tile(c,r)
            cell.possibilities = [int(orig)]
            cell.entropy = 0
        sync_tile_map_with_world()          #  ← ADD THIS

        current_phase = "DONE"
        pygame.display.set_caption("Complete – Press [R] to Restart")
    else:
        print("Invalid world returned by agent.")
        current_phase = "FAILED"
        pygame.display.set_caption("Agent FAILED – Press [R] to Restart")

# --- Main loop ---
running = True
initialize_world()

while running:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                running = False
            elif ev.key == pygame.K_f and current_phase == "FOREST_READY":
                run_forest_wfc()
            elif ev.key == pygame.K_s and current_phase == "SOKO_READY":
                run_sokoban_agent()
            elif ev.key == pygame.K_r and current_phase in ("DONE", "FAILED"):
                initialize_world()
            elif ev.key == pygame.K_b and current_phase not in ("INIT","FOREST_RUNNING"):
                show_binary_view = not show_binary_view
                show_tag_view = False  # Turn off tag view when binary view is enabled
            elif ev.key == pygame.K_t and current_phase not in ("INIT","FOREST_RUNNING"):
                show_tag_view = not show_tag_view
                show_binary_view = False  # Turn off binary view when tag view is enabled
        elif ev.type == pygame.MOUSEBUTTONDOWN and current_phase not in ("INIT","FOREST_RUNNING","SOKO_INJECTING"):
            if ev.button == 1 and world:
                mx, my = ev.pos
                tile_w = Config.TILESIZE * Config.SCALETILE
                col = int(mx // tile_w)
                row = int(my // tile_w)
                if 0 <= col < world.cols and 0 <= row < world.rows:
                    t = world.get_tile(col, row)
                    tid = world.getType(col, row) if t else None
                    ent = t.entropy if t else None
                    cnt = len(t.possibilities) if t else None
                    print(f"Clicked (c={col},r={row}) → ID={tid}, entropy={ent}, poss={cnt}")
                    if tag_grid is not None:
                        tag_val = tag_grid[row, col]
                        print(f"Tag value: {tag_val}")
    
    # Draw
    screen.fill((30,30,30))
    if draw_world and world:
        if show_binary_view and binary_maze is not None:
            draw_binary_maze(screen, binary_maze)
        elif show_tag_view and tag_grid is not None:
            draw_tag_grid(screen, tag_grid)
        else:
            draw_world.update(
                show_entropy=(current_phase == "FOREST_RUNNING"),
                highlight_path=solution_path or None
            )
            draw_world.draw(screen)
    else:
        surf = status_font.render("Press F to start", True, (200,200,200))
        screen.blit(surf, surf.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2)))
    
    # Status & hints
    col = (255,0,0) if "FAILED" in current_phase else (200,200,200)
    status = f"Phase: {current_phase}{' (Running)' if wfc_running else ''}"
    txt = status_font.render(status, True, col)
    screen.blit(txt, (10, WINDOW_HEIGHT-30))
    
    hints = {
        "FOREST_READY": "[F] Generate Forest",
        "SOKO_READY": "[S] Inject Sokoban | [B] Binary View | [T] Tag View",
        "DONE": "[R] Restart | [B] Binary View | [T] Tag View",
        "FAILED": "[R] Restart",
    }
    
    hint = hints.get(current_phase, "")
    surf = status_font.render(hint, True, (150,150,255))
    screen.blit(surf, surf.get_rect(bottomright=(WINDOW_WIDTH-10, WINDOW_HEIGHT-10)))
    
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
