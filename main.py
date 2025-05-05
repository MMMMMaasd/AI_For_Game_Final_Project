import pygame
import sys
import random

import Config                      # your updated Config.py
from ClassWorld       import World
from ClassDrawWorld   import DrawWorld
from MazeGenerator    import generate_maze_and_path
from SokobanInjector  import *
from agent_before_phase2 import agent_runner


# --- Pygame setup ---
pygame.init()
pygame.font.init()
WINDOW_WIDTH  = Config.WORLD_X * Config.TILESIZE * Config.SCALETILE
WINDOW_HEIGHT = Config.WORLD_Y * Config.TILESIZE * Config.SCALETILE + 40
screen        = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Forest + Sokoban WFC Generator")
clock         = pygame.time.Clock()
status_font   = pygame.font.Font(pygame.font.get_default_font(), 18)

# --- State ---
world          = None
draw_world     = None
solution_path  = None  # list of (row, col)
sokoban_region = None  # list of (x, y)
current_phase  = "INIT"  # INIT, FOREST_READY, FOREST_RUNNING, SOKO_READY, SOKO_RUNNING, DONE, FAILED
wfc_running    = False
soko_regions = None

def initialize_world_for_forest_wfc():
    """Phase 0: fresh World, reset everything."""
    global world, draw_world, solution_path, sokoban_region, current_phase, wfc_running

    print("\n--- Phase 0: Initializing World ---")
    world = World(Config.WORLD_X, Config.WORLD_Y)
    draw_world = DrawWorld(world)
    solution_path = None
    sokoban_region = None

    # Seed ALL tiles with the full forest domain (we'll collapse next step)
    for y in range(world.rows):
        for x in range(world.cols):
            t = world.get_tile(x, y)
            t.possibilities = list(Config.FOREST_DOMAIN)
            t.entropy       = len(t.possibilities)
            t.is_path       = False
            t.is_sokoban_area = False

    print("Ready to carve solution path. Press [F].")
    current_phase = "FOREST_READY"
    wfc_running = False

def set_tree_boundary_rules(world, solution_path):
    path_set = {(r, c) for (r, c) in solution_path}
    
    for r, c in solution_path:
        # Check all 4-directional neighbors
        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            nr, nc = r + dr, c + dc
            if (0 <= nr < world.rows and 0 <= nc < world.cols and 
                (nr, nc) not in path_set):
                
                t = world.get_tile(nc, nr)
                if t and not t.is_path:
                    # Mark left boundaries (tiles to the west of path)
                    if dc == -1:  # West neighbor
                        t.is_left_boundary = True
                        t.possibilities = [
                            p for p in t.possibilities
                            if p not in Config.INNER_BOUNDARIES_LEFT_RESTRICT
                        ]
                    # Mark right boundaries (tiles to the east of path)
                    elif dc == 1:  # East neighbor
                        t.is_right_boundary = True
                        t.possibilities = [
                            p for p in t.possibilities
                            if p not in Config.INNER_BOUNDARIES_RIGHT_RESTRICT
                        ]
                    
                    t.entropy = len(t.possibilities)
                    t.is_boundary = True  # General boundary marker

def run_forest_wfc():
    """
    Phase 1:
      1) carve a single solution path via MazeGenerator,
      2) fix those path tiles to grass,
      3) repeatedly run WFC on the rest of the map until no contradictions occur.
    """
    global solution_path, current_phase, wfc_running

    if not world:
        print("Error: world not initialized.")
        current_phase = "FAILED"
        return

    print("\n--- Phase 1: Carving Path & WFC on Remainder ---")
    current_phase = "FOREST_RUNNING"
    wfc_running   = True

    # 1) carve maze & get solution coords
    _, solution_path = generate_maze_and_path(world.rows, world.cols)
    print(f"Solution path length = {len(solution_path)}")

    # 2) collapse (fix) the path‐tiles to grass
    for (r, c) in solution_path:
        t = world.get_tile(c, r)
        t.possibilities = [Config.TILE_GRASS]
        t.entropy       = 0
        t.is_path       = True
    set_tree_boundary_rules(world, solution_path)

    # 3) prepare region = all coords not on the path
    region = [(c, r)
              for r in range(world.rows)
              for c in range(world.cols)
              if (r, c) not in solution_path]
    
    # 4) retry WFC until no contradictions
    attempt = 0
    while True:
        attempt += 1
        print(f" WFC attempt #{attempt} on {len(region)} tiles…")
        world.runWFC(
            adjacency_rules = Config.adjacency_rules_forest,
            weights         = Config.tile_weights_forest,
            region          = region
        )

        # detect contradiction in region
        contradicted = False
        for (c, r) in region:
            t = world.get_tile(c, r)
            if t.entropy == 0 and not t.possibilities:
                contradicted = True
                print(f"  → Contradiction at ({r},{c}) on attempt {attempt}")
                break

        if not contradicted:
            print(f" WFC succeeded on attempt #{attempt}.")
            break

        # reset non-path tiles back to full domain
        print("Resetting region and retrying WFC...")
        for (c, r) in region:
            t = world.get_tile(c, r)
            if not hasattr(t, 'is_boundary'):
                t.possibilities = list(Config.FOREST_DOMAIN)
                t.entropy = len(t.possibilities)
            elif t.is_left_boundary:
                t.possibilities = [
                    p for p in Config.FOREST_DOMAIN
                    if p not in Config.INNER_BOUNDARIES_LEFT_RESTRICT
                ]
                t.entropy = len(t.possibilities)
            elif t.is_right_boundary:
                t.possibilities = [
                    p for p in Config.FOREST_DOMAIN
                    if p not in Config.INNER_BOUNDARIES_RIGHT_RESTRICT
                ]
                t.entropy = len(t.possibilities)
    global soko_regions
    print("Solution path")
    print(solution_path)
    soko_regions = find_sokoban_regions(world, solution_path)
    print("Found Soko region:")
    print(soko_regions)
    generate_sokoban_levels(world, soko_regions)
    wfc_running = False
    current_phase = "SOKO_READY"
    print("Forest WFC complete without contradictions. Ready for Sokoban. Press [S].")


def run_sokoban_injection():
    """Phase 2: inject Sokoban puzzle onto the pre‐carved path."""
    global sokoban_region, current_phase, wfc_running

    if not world or not solution_path:
        print("Error: forest maze path missing.")
        current_phase = "FAILED"
        return

    print("\n--- Phase 2: Injecting Sokoban Puzzle ---")
    current_phase = "SOKO_RUNNING"
    wfc_running = True
    
    attempts = 0
    max_attempts = 10
    while attempts < 1:
        attempts += 1
        sokoban_region = inject_sokoban_puzzle(world, solution_path, size=7)
        if sokoban_region:
            solvable_region = validate_and_make_solvable(world, sokoban_region)
            if solvable_region:
                print(f"Created solvable puzzle in attempt {attempts}")

    wfc_running = False


    if sokoban_region:
        print("Sokoban injection complete!")
        current_phase = "DONE"
    else:
        print("ERROR: Sokoban injection failed.")
        current_phase = "FAILED"


# --- Main Loop ---
running = True
initialize_world_for_forest_wfc()

while running:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                running = False
            elif ev.key == pygame.K_r:
                initialize_world_for_forest_wfc()
            elif ev.key == pygame.K_f and current_phase == "FOREST_READY":
                run_forest_wfc()
            elif ev.key == pygame.K_s and current_phase == "SOKO_READY":
                print("\n--- Phase 2: Agent‐driven Sokoban injection ---")
                agent_runner(world, solution_path, size=3, max_iterations=10)
                current_phase = "DONE"
                run_sokoban_injection()
        elif ev.type == pygame.MOUSEBUTTONDOWN and current_phase not in ("INIT", "FOREST_RUNNING"):
            mx, my = ev.pos
            # convert screen pixels → tile coords
            tile_w = Config.TILESIZE * Config.SCALETILE
            col = int(mx // tile_w)
            row = int(my // tile_w)
            # bounds check
            if 0 <= col < world.cols and 0 <= row < world.rows:
                tid = world.getType(col, row)
                print(f"Clicked on tile at (col={col}, row={row}) → ID = {tid}")
            else:
                print("Clicked outside the map area.")

    # Render
    screen.fill((30,30,30))
    if draw_world:
        draw_world.update(
            show_entropy      = False,
            highlight_path    = solution_path   if current_phase in ("SOKO_READY","SOKO_RUNNING","DONE") else None,
            highlight_sokoban = sokoban_region  if current_phase in ("SOKO_RUNNING","DONE")       else None,
            highlight_regions=soko_regions if current_phase == "SOKO_READY" else None
        )
        draw_world.draw(screen)
    else:
        txt = status_font.render("Press R to initialize", True, (200,200,200))
        screen.blit(txt, (20, WINDOW_HEIGHT//2 - 20))

    # Status bar
    status = f"Phase: {current_phase}" + (" (Running...)" if wfc_running else "")
    col    = (255,0,0) if "FAILED" in current_phase else (200,200,200)
    surf   = status_font.render(status, True, col)
    screen.blit(surf, (10, WINDOW_HEIGHT - 30))

    # Controls hint
    hints = {
        "INIT":         "[R] Initialize",
        "FOREST_READY": "[F] Carve Path & WFC",
        "FOREST_RUNNING": "Running WFC…",
        "SOKO_READY":   "[S] Inject Sokoban",
        "SOKO_RUNNING": "Injecting Sokoban…",
        "DONE":         "[R] Restart",
        "FAILED":       "[R] Restart",
    }
    hint = hints.get(current_phase, "[R] Restart")
    hs   = status_font.render(hint, True, (150,150,255))
    rs   = hs.get_rect(bottomright=(WINDOW_WIDTH-10, WINDOW_HEIGHT-10))
    screen.blit(hs, rs)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
