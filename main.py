# michael/main.py

import pygame
import sys
import numpy as np
import Config  # your updated Config.py
from ClassWorld import World
from ClassDrawWorld import DrawWorld
from MazeGenerator import generate_maze_and_path  # returns (maze_grid, solution_path, tag_grid)

# Import the agent function (now takes an existing World + tag_grid + carved path)
try:
    from agent_before_phase_2 import prepare_puzzle_world
except ImportError:
    print("ERROR: Cannot import 'prepare_puzzle_world'.")
    prepare_puzzle_world = None

# --- Constants for mapping ---
GRASS_ID   = Config.TILE_GRASS
WALL_ID    = Config.TILE_TREE_MID_MID
BOX_ID     = Config.SOKOBAN_GRID_TO_TILE_MAP[3]
HOLE_ID    = Config.SOKOBAN_GRID_TO_TILE_MAP[2]
PLAYER_ID  = Config.PLAYER_ID
END_HILITE = Config.END_HILITE

# --- Pygame setup ---
pygame.init()
pygame.font.init()
WINDOW_WIDTH  = int(Config.WORLD_X * Config.TILESIZE * Config.SCALETILE)
WINDOW_HEIGHT = int(Config.WORLD_Y * Config.TILESIZE * Config.SCALETILE + 40)
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Forest + Sokoban WFC Generator")
clock = pygame.time.Clock()
status_font = pygame.font.Font(pygame.font.get_default_font(), 18)

# --- State ---
world         = None
draw_world    = None
maze_grid     = None   # 0=path,1=wall
tile_id_mask  = None   # GRASS_ID/WALL_ID per cell
tag_grid      = None   # 0=walk,1=wall,2=path,5=start,6=end,3=box,4=hole
solution_path = None
binary_maze   = None   # last printed binary map
tile_id_maze  = None   # last printed tile-ID map
current_phase = "FOREST_READY"
wfc_running   = False
show_binary_view = False
show_tag_view    = False

# --- Player state & Sokoban reset tracking ---
player_pos = None  # (r,c)
start_pos  = None
end_pos    = None
initial_box_positions = []  # remember where the agent put its boxes

def initialize_world():
    """Phase 0: reset everything."""
    global world, draw_world, maze_grid, tile_id_mask, tag_grid, solution_path
    global binary_maze, tile_id_maze, wfc_running, show_binary_view, show_tag_view
    global current_phase, player_pos, start_pos, end_pos, initial_box_positions

    world = World(Config.WORLD_X, Config.WORLD_Y)
    world.tile_map = np.zeros((world.rows, world.cols), dtype=int)
    draw_world = DrawWorld(world)
    maze_grid = tile_id_mask = tag_grid = solution_path = None
    binary_maze = tile_id_maze = None
    wfc_running = False
    show_binary_view = show_tag_view = False

    # seed every tile with the full forest domain
    for y in range(world.rows):
        for x in range(world.cols):
            t = world.get_tile(x, y)
            if t:
                t.possibilities = list(Config.FOREST_DOMAIN)
                t.entropy = len(Config.FOREST_DOMAIN)
                t.is_path = t.is_left_boundary = t.is_right_boundary = False

    current_phase = "FOREST_READY"
    player_pos = start_pos = end_pos = None
    initial_box_positions.clear()
    print("Initialized. Press [F] to carve maze & generate forest.")

def set_tree_boundary_rules(path_coords):
    """Mark east/west neighbours of the carved path so the corridor stays clear."""
    path_set = set(path_coords)
    for (r, c) in path_coords:
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r+dr, c+dc
            if not (0 <= nr < world.rows and 0 <= nc < world.cols): continue
            if (nr, nc) in path_set: continue
            t = world.get_tile(nc, nr)
            if not t: continue
            if dc == -1: t.is_left_boundary = True
            if dc ==  1: t.is_right_boundary = True

def display_maze_matrices(world):
    """Print binary & tile‐ID maps to console."""
    rows, cols = world.rows, world.cols
    binary = np.zeros((rows, cols), dtype=int)
    tile_ids = np.zeros((rows, cols), dtype=int)

    for r in range(rows):
        for c in range(cols):
            tid = world.getType(c, r)
            if tid is None:
                binary[r,c] = tile_ids[r,c] = -1
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
    """Draws the binary maze on‐screen."""
    if binary is None: return
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
    """Draws the tag grid representation on‐screen."""
    if tag_grid is None: return
    rows, cols = tag_grid.shape
    cw = WINDOW_WIDTH // cols
    ch = (WINDOW_HEIGHT-40) // rows
    for r in range(rows):
        for c in range(cols):
            tg = tag_grid[r,c]
            if   tg==0: color=(128,128,128)
            elif tg==1: color=(0,128,0)
            elif tg==2: color=(255,255,0)
            elif tg==3: color=(139,69,19)
            elif tg==4: color=(0,0,255)
            elif tg==5: color=(255,0,0)
            elif tg==6: color=(128,0,128)
            else:       color=(255,255,255)
            rect = pygame.Rect(c*cw, r*ch, cw, ch)
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (50,50,50), rect, 1)
    if solution_path:
        for r,c in solution_path:
            rect = pygame.Rect(c*cw, r*ch, cw, ch)
            pygame.draw.rect(surface, (255,255,0), rect, 2)

def sync_tile_map_with_world():
    """Force world.tile_map, cell.possibilities & tag_grid to agree."""
    BOX   = Config.SOKOBAN_GRID_TO_TILE_MAP[3]
    HOLE  = Config.SOKOBAN_GRID_TO_TILE_MAP[2]
    WALK  = set(Config.WALKABLE_TILES)
    for r in range(world.rows):
        for c in range(world.cols):
            cell = world.get_tile(c,r)
            if cell is None: continue
            raw_tid = int(world.tile_map[r,c])
            if cell.entropy==0 and cell.possibilities:
                tid = cell.possibilities[0]
            else:
                tg = tag_grid[r,c]
                if   tg==3: tid=BOX
                elif tg==4: tid=HOLE
                elif tg==1: tid=Config.SHORT_BUSH
                else:       tid=raw_tid if raw_tid not in (-1,0) else Config.TILE_GRASS
            cell.possibilities=[tid]
            cell.entropy=0
            world.tile_map[r,c]=tid
            old_tg = tag_grid[r,c]
            if old_tg not in (2,3,4,5,6):
                if   tid==BOX:     tag_grid[r,c]=3
                elif tid==HOLE:    tag_grid[r,c]=4
                elif tid in WALK:  tag_grid[r,c]=0
                else:              tag_grid[r,c]=1

def run_forest_wfc():
    """Phase 1: generate maze, tag path, then WFC on the rest."""
    global maze_grid, tile_id_mask, tag_grid, solution_path, binary_maze, tile_id_maze
    global current_phase, wfc_running

    if not world:
        current_phase="FAILED"
        return

    current_phase="FOREST_RUNNING"
    wfc_running=True
    pygame.display.set_caption("Running Forest WFC…")

    maze_grid, solution_path, tag_grid = generate_maze_and_path(world.rows,world.cols)
    if solution_path is None:
        print("MazeGenerator failed.")
        current_phase="FAILED"
        wfc_running=False
        return

    tile_id_mask = np.where(maze_grid==0, GRASS_ID, WALL_ID)
    for r,c in solution_path:
        t=world.get_tile(c,r)
        if t:
            t.possibilities=[GRASS_ID]
            t.entropy=0
            t.is_path=True

    set_tree_boundary_rules(solution_path)
    region=[(c,r) for r in range(world.rows) for c in range(world.cols)
            if (r,c) not in solution_path]

    attempt=0
    while True:
        attempt+=1
        print(f"Forest WFC attempt #{attempt}")
        for c,r in region:
            t=world.get_tile(c,r)
            if not t: continue
            base=list(Config.FOREST_DOMAIN)
            if t.is_left_boundary:
                base=[p for p in base if p not in Config.INNER_BOUNDARIES_LEFT_RESTRICT]
            if t.is_right_boundary:
                base=[p for p in base if p not in Config.INNER_BOUNDARIES_RIGHT_RESTRICT]
            t.possibilities=base
            t.entropy=len(base)

        world.runWFC(
            adjacency_rules=Config.adjacency_rules_forest,
            weights=Config.tile_weights_forest,
            region=region
        )

        contradicted=any(
            world.get_tile(c,r).entropy==0
            and not world.get_tile(c,r).possibilities
            for c,r in region
        )
        if not contradicted:
            print("Forest WFC succeeded.")
            binary_maze, tile_id_maze = display_maze_matrices(world)
            world.tile_map = np.array(tile_id_maze)
            sync_tile_map_with_world()

            # repair tag_grid
            for rr in range(tag_grid.shape[0]):
                for cc in range(tag_grid.shape[1]):
                    if tag_grid[rr,cc]==1 and tile_id_maze[rr,cc] in Config.WALKABLE_TILES:
                        tag_grid[rr,cc]=0
                    elif tag_grid[rr,cc]==0 and tile_id_maze[rr,cc] not in Config.WALKABLE_TILES:
                        tag_grid[rr,cc]=1

            print("\n=== TAG GRID (0=walk,1=wall,2=path,5=start,6=end) ===")
            for row in tag_grid:
                print(' '.join(str(v) for v in row))
            break

    wfc_running=False
    current_phase="SOKO_READY"
    pygame.display.set_caption("Forest Ready – Press [S] for Sokoban")

def refresh_tags_from_tilemap(tag_grid, tile_map):
    """Re-derive tags from final tile_map (keep 1,5,6)."""
    for r in range(tag_grid.shape[0]):
        for c in range(tag_grid.shape[1]):
            tid=int(tile_map[r,c])
            if tid==BOX_ID:     tag_grid[r,c]=3
            elif tid==HOLE_ID:  tag_grid[r,c]=4
            elif tag_grid[r,c] in (1,5,6): continue
            elif tid in Config.WALKABLE_TILES: tag_grid[r,c]=0
            else: tag_grid[r,c]=1

def run_sokoban_agent():
    """Phase 2: inject Sokoban, then restore the rest of forest."""
    global world, draw_world, tag_grid, solution_path, binary_maze, tile_id_maze
    global current_phase, wfc_running, player_pos, start_pos, end_pos, initial_box_positions

    if not prepare_puzzle_world:
        current_phase="FAILED"
        return

    current_phase="SOKO_INJECTING"
    wfc_running=True
    pygame.display.set_caption("Running Sokoban Agent…")

    try:
        new_world = prepare_puzzle_world(
            world, tag_grid, solution_path,
            num_boxes_per_puzzle=3
        )
        refresh_tags_from_tilemap(tag_grid, world.tile_map)
    except Exception as e:
        print("Agent error:", e)
        current_phase="FAILED"
        wfc_running=False
        return

    wfc_running=False

    if isinstance(new_world, World):
        world=new_world
        draw_world.world=world
        sync_tile_map_with_world()

        # locate start/end tags
        sy,sx = np.argwhere(tag_grid==5)[0]
        ey,ex = np.argwhere(tag_grid==6)[0]
        start_pos=(sy,sx)
        end_pos  =(ey,ex)

        # mark them in tile_map
        world.tile_map[sy,sx]=PLAYER_ID
        world.tile_map[ey,ex]=END_HILITE
        player_pos=start_pos

        # record initial box positions
        initial_box_positions.clear()
        for br,bc in np.argwhere(tag_grid==3):
            initial_box_positions.append((br,bc))

        print("\n=== TAG GRID AFTER SOKOBAN ===")
        for row in tag_grid:
            print(' '.join(str(v) for v in row))

        binary_maze, tile_id_maze = display_maze_matrices(world)

        # restore original WFC‐chosen tiles outside Sokoban area
        for (r,c),orig in np.ndenumerate(tile_id_maze):
            if tag_grid[r,c] in (3,4): continue
            cell=world.get_tile(c,r)
            cell.possibilities=[int(orig)]
            cell.entropy=0
        sync_tile_map_with_world()

        current_phase="DONE"
        pygame.display.set_caption("Complete – Press [P] to Reset, Arrows to Move")
    else:
        print("Invalid world returned by agent.")
        current_phase="FAILED"
        pygame.display.set_caption("Agent FAILED – Press [R] to Restart")

# --- Main loop ---
running=True
initialize_world()

while running:
    for ev in pygame.event.get():
        if ev.type==pygame.QUIT:
            running=False

        # --- Player movement & reset (NEW) ---
        elif ev.type==pygame.KEYDOWN:
            if current_phase=="DONE":
                # Reset player AND boulders
                if ev.key==pygame.K_p and start_pos:
                    # 1) clear old player, boxes, holes remain
                    for r in range(world.rows):
                        for c in range(world.cols):
                            tg = tag_grid[r,c]
                            if world.tile_map[r,c] in (BOX_ID, PLAYER_ID) or tg==3:
                                world.tile_map[r,c] = GRASS_ID
                                tag_grid[r,c] = 0
                    # 2) re-place boxes
                    for br,bc in initial_box_positions:
                        world.tile_map[br,bc] = BOX_ID
                        tag_grid[br,bc]       = 3
                        cell = world.get_tile(bc, br)
                        cell.possibilities   = [BOX_ID]
                        cell.entropy         = 0
                    # 3) re-place player & end
                    sr,sc = start_pos
                    world.tile_map[sr,sc] = PLAYER_ID
                    er,ec = end_pos
                    world.tile_map[er,ec] = END_HILITE
                    player_pos = start_pos

                # Arrows: move / push
                elif ev.key in (pygame.K_UP,pygame.K_DOWN,pygame.K_LEFT,pygame.K_RIGHT):
                    dr,dc = {
                        pygame.K_UP:    (-1,0),
                        pygame.K_DOWN:  (1,0),
                        pygame.K_LEFT:  (0,-1),
                        pygame.K_RIGHT: (0,1),
                    }[ev.key]
                    r,c = player_pos
                    nr,nc = r+dr, c+dc
                    if 0<=nr<world.rows and 0<=nc<world.cols:
                        tg = tag_grid[nr,nc]
                        # push boulder?
                        if tg==3:
                            nnr,nnc = nr+dr, nc+dc
                            if (0<=nnr<world.rows and 0<=nnc<world.cols
                                and tag_grid[nnr,nnc] in (0,2,4)):
                                pushing_into_hole = (tag_grid[nnr,nnc]==4)
                                # move box
                                world.tile_map[nnr,nnc]=BOX_ID
                                cell_new=world.get_tile(nnc,nnr)
                                cell_new.possibilities=[BOX_ID]; cell_new.entropy=0
                                if not pushing_into_hole:
                                    tag_grid[nnr,nnc]=3
                                # clear old
                                world.tile_map[nr,nc]=GRASS_ID
                                cell_old=world.get_tile(nc,nr)
                                cell_old.possibilities=[GRASS_ID]; cell_old.entropy=0
                                tag_grid[nr,nc]=0
                                # move player
                                world.tile_map[r,c]=GRASS_ID
                                world.tile_map[nr,nc]=PLAYER_ID
                                player_pos=(nr,nc)
                        # walkable
                        elif tg in (0,2,4,5,6):
                            world.tile_map[r,c]=GRASS_ID
                            world.tile_map[nr,nc]=PLAYER_ID
                            player_pos=(nr,nc)

            # --- Other controls ---
            if ev.key==pygame.K_ESCAPE:
                running=False
            elif ev.key==pygame.K_f and current_phase=="FOREST_READY":
                run_forest_wfc()
            elif ev.key==pygame.K_s and current_phase=="SOKO_READY":
                run_sokoban_agent()
            elif ev.key==pygame.K_r and current_phase in ("DONE","FAILED"):
                initialize_world()
            elif ev.key==pygame.K_b and not wfc_running:
                show_binary_view = not show_binary_view
                show_tag_view    = False
            elif ev.key==pygame.K_t and not wfc_running:
                show_tag_view    = not show_tag_view
                show_binary_view = False

        elif ev.type==pygame.MOUSEBUTTONDOWN and not wfc_running:
            if ev.button==1 and world:
                mx,my = ev.pos; tw=Config.TILESIZE*Config.SCALETILE
                col=int(mx//tw); row=int(my//tw)
                if 0<=col<world.cols and 0<=row<world.rows:
                    t=world.get_tile(col,row)
                    tid=world.getType(col,row) if t else None
                    ent=t.entropy if t else None
                    cnt=len(t.possibilities) if t else None
                    print(f"Clicked (c={col},r={row}) → ID={tid}, entropy={ent}, poss={cnt}")
                    if tag_grid is not None:
                        print("Tag:", tag_grid[row,col])

    # Draw
    screen.fill((30,30,30))
    if draw_world and world:
        if show_binary_view and binary_maze is not None:
            draw_binary_maze(screen, binary_maze)
        elif show_tag_view and tag_grid is not None:
            draw_tag_grid(screen, tag_grid)
        else:
            draw_world.update(
                show_entropy=(current_phase=="FOREST_RUNNING"),
                highlight_path=solution_path or None
            )
            draw_world.draw(screen)

            # highlight end tile
            if end_pos:
                er,ec = end_pos
                cw = Config.TILESIZE * Config.SCALETILE
                hl = pygame.Surface((cw,cw), pygame.SRCALPHA)
                hl.fill((255,255,0,80))
                screen.blit(hl,(ec*cw,er*cw))

            # draw player
            if player_pos:
                pr,pc = player_pos
                cw = Config.TILESIZE * Config.SCALETILE
                cx = int(pc*cw + cw/2)
                cy = int(pr*cw + cw/2)
                rad = int(cw*0.4)
                pygame.draw.circle(screen,(0,0,255),(cx,cy),rad)
    else:
        surf = status_font.render("Press F to start", True, (200,200,200))
        screen.blit(surf, surf.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2)))

    # Status & hints
    col = (255,0,0) if "FAILED" in current_phase else (200,200,200)
    status = f"Phase: {current_phase}{' (Running)' if wfc_running else ''}"
    txt    = status_font.render(status, True, col)
    screen.blit(txt,(10,WINDOW_HEIGHT-30))

    hints = {
        "FOREST_READY":"[F] Generate Forest",
        "SOKO_READY":  "[S] Inject Sokoban | [B] Binary | [T] Tag",
        "DONE":        "[Arrows] Move | [P] Reset | [B] Binary | [T] Tag",
        "FAILED":      "[R] Restart",
    }
    hint = hints.get(current_phase,"")
    surf = status_font.render(hint, True, (150,150,255))
    screen.blit(surf, surf.get_rect(bottomright=(WINDOW_WIDTH-10,WINDOW_HEIGHT-10)))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
