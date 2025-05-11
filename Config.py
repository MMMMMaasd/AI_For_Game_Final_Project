# michael/Config.py

from collections import defaultdict
from PIL import Image
import os
import numpy as np
from copy import deepcopy

# --- Paths ---
ASSET_DIR               = os.path.dirname(__file__)
SPRITESHEET_PATH        = os.path.join(ASSET_DIR, "tileset_forest.png")
TANIBO_SPRITESHEET_PATH = os.path.join(ASSET_DIR, "Tanibo_tileset.png")
MAP_PATH                = os.path.join(ASSET_DIR, "VERTANIA-WALD (1.0).jpg")
PLAYER_SPRITE_PATH      = os.path.join(ASSET_DIR, "player_sprite.png")
STONE_SPRITE_PATH       = os.path.join(ASSET_DIR, "stone(box)_sprite.png")



# --- Grid & Display ---
WORLD_X   = 30
WORLD_Y   = 30
TILESIZE  = 16
SCALETILE = 1.5

# --- Directions ---
NORTH, EAST, SOUTH, WEST = 0, 1, 2, 3
DIRECTIONS = (NORTH, EAST, SOUTH, WEST)

# --- Forest Tile IDs (Base Definitions) ---
TILE_GRASS                          = 1       
TILE_GRASS2                         = 8
TILE_GRASS3                         = 9
TILE_TALL_GRASS                     = 13
TILE_GRASS4                         = 16
TILE_GRASS5                         = 17
TILE_DARK_GROUND_LEFT_TOP           = 208
TILE_DARK_GROUND_MID_TOP            = 209
TILE_DARK_GROUND_RIGHT_TOP          = 210
TILE_LIGHT_GROUND_LEFT_TOP          = 211
TILE_LIGHT_GROUND_MID_TOP           = 212
TILE_LIGHT_GROUND_RIGHT_TOP         = 213
TILE_DARK_GROUND_LEFT_MID           = 216
TILE_DARK_GROUND_MID_MID            = 217
TILE_DARK_GROUND_RIGHT_MID          = 218
TILE_DARK_GROUND_LEFT_BOTTOM        = 224
TILE_DARK_GROUND_MID_BOTTOM         = 225
TILE_DARK_GROUND_RIGHT_BOTTOM       = 226
TILE_LIGHT_GROUND_LEFT_BOTTOM       = 227
TILE_LIGHT_GROUND_MID_BOTTOM        = 228
TILE_LIGHT_GROUND_RIGHT_BOTTOM      = 229
TILE_FENCE_BOTTOM_RIGHT             = 234
TILE_FENCE_TOP_BOTTOM_RIGHT         = 241
TILE_FENCE_TOP_RIGHT                = 242
TILE_FENCE_TOP_LEFT                 = 243
TILE_FENCE_TOP                      = 249
TILE_DARK_GROUND_MID_MID2           = 254
TILE_DARK_GROUND_MID_MID3           = 255
TILE_DARK_GROUND_MID_MID4           = 262
TILE_DARK_GROUND_MID_MID5           = 263
TILE_TREE_TOP_TOP_GRASS             = 641
TILE_FLOWER                         = 642
TILE_TREE_TOP_TOP_WALL              = 643
TILE_TREE_TOP_TOP_TALL_GRASS        = 644
TILE_TREE_TOP_TOP_LIGHT_GROUND_MID  = 646
TILE_TREE_TOP_TOP_LIGHT_GROUND_RIGHT= 647
TILE_TREE_LEFT_MID                  = 648
TILE_TREE_MID_MID                   = 649
TILE_TREE_RIGHT_MID                 = 650
TILE_TREE_LEFT_BOTTOM               = 654
TILE_TREE_RIGHT_BOTTOM              = 655
TILE_TREE_LEFT_BOTTOM2              = 656
TILE_TREE_CONNECTOR                 = 657
TILE_TREE_RIGHT_BOTTOM2             = 658
TILE_TREE_MID_MID2                  = 662
TILE_TREE_LEFT_MID2                 = 664
TILE_TREE_MID_MID3                  = 665
TILE_TREE_RIGHT_MID2                = 666
TILE_TREE_LEFT_BOTTOM3              = 670
TILE_TREE_LEFT_BOTTOM4              = 672
TILE_TREE_MID_BOTTOM                = 673
TILE_TREE_LEFT_BOTTOM_TO_GROUND     = 675
TILE_TREE_MID_BOTTOM_TO_GROUND      = 676
TILE_TREE_RIGHT_BOTTOM_TO_GROUND    = 677
TILE_FENCE_MID                      = 678
TILE_FENCE_MID2                     = 679

# --- Extra bush for Sokoban walls ---
SHORT_BUSH = 5
PLAYER_ID   = 900          # <= NEW
END_HILITE  = 901

# --- User-Defined Blacklist + Original Building Blacklist ---
USER_BLACKLIST = {
    6, 7, 24, 25,26, 32, 33, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51,
    52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
    70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87,
    88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99,100,101,102,103,104,107,108,109,
    113,116,118,119,120,123,128,130,135,136,137,140,141,142,143,145,166,167,168,169,172,173,174,176,177,180,184,185,189,190,191,
    192,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,221,227,228,229,
    231,232,233,256,257,260,261,264,265,268,312,313,314,315,316,320,321,322,323,324,328,329,330,
    331,332,333,336,337,338,339,340,341,342,344,345,346,347,348,349,350,351,
    376,377,378,379,380,381,382,383,384,385,386,387,388,389,390,392,393,394,
    395,396,397,398,400,401,402,403,404,405, 406,407,408,409,410,411,412,313, 414,415,419,420,
    421,422,423,425,426,427,430,431,435,436,437,438,651,652,653,659,660,661,668,669,671, 683, 685
}
ORIGINAL_BUILDING_BLACKLIST = {68, 76, 77, 78, 94, 102, 439, 643, 659}
FULL_BLACKLIST = USER_BLACKLIST | ORIGINAL_BUILDING_BLACKLIST

# --- Additional Walkable IDs ---
ADDITIONAL_WALKABLE = {
    4, 10, 188, 189, 219, 220, 221, 680, 681, 682
}
PATH_TILES = {TILE_GRASS}

# --- Sokoban holes (Tanibo IDs) and boulder spots ---
TILE_BOULDER_SPOTS = {719, 727}


# ----------------------------------------------------------------------------
# Build FOREST_DOMAIN from spritesheet, then apply blacklist
# ----------------------------------------------------------------------------
try:
    img  = Image.open(SPRITESHEET_PATH)
    cols = img.width  // TILESIZE
    rows = img.height // TILESIZE
    img.close()
    FOREST_TILE_IDS = {
        r*cols + c: (c, r)
        for r in range(rows)
        for c in range(cols)
    }

    # define which rows are floor vs wall
    floor_rows = (
        0,1,6,7,10,11,12,13,16,17,21,22,23,24,
        26,27,28,31,32,33,41,47,48,49,50,51,
        52,54,80,81,82,83,84,85
    )
    wall_rows = (
        2,3,4,8,9,11,14,15,20,25,29,30,42,43,
        53,80,81,82,83,84
    )

    INITIAL_FLOOR_TILES = {
        tid for tid,(c,r) in FOREST_TILE_IDS.items()
        if r in floor_rows
    }
    INITIAL_WALL_TILES = {
        tid for tid,(c,r) in FOREST_TILE_IDS.items()
        if r in wall_rows
    }
    INITIAL_FLOOR_TILES.add(TILE_GRASS)
    INITIAL_WALL_TILES.add(TILE_TREE_MID_MID)

except Exception as e:
    print(f"Warning: spritesheet load failed ({e}). Using minimal domain.")
    INITIAL_FLOOR_TILES = {TILE_GRASS}
    INITIAL_WALL_TILES  = {TILE_TREE_MID_MID}
    FOREST_TILE_IDS     = {}

INITIAL_FOREST_DOMAIN = INITIAL_FLOOR_TILES | INITIAL_WALL_TILES
FOREST_DOMAIN         = (INITIAL_FOREST_DOMAIN - FULL_BLACKLIST) | {SHORT_BUSH}

TREES = {
    TILE_TREE_TOP_TOP_WALL, TILE_TREE_TOP_TOP_TALL_GRASS,
    TILE_TREE_TOP_TOP_LIGHT_GROUND_MID, TILE_TREE_TOP_TOP_LIGHT_GROUND_RIGHT,
    TILE_TREE_TOP_TOP_GRASS, TILE_TREE_CONNECTOR,
    TILE_TREE_MID_MID, TILE_TREE_MID_MID3,
    TILE_TREE_LEFT_MID2, TILE_TREE_RIGHT_MID2,
    TILE_TREE_MID_BOTTOM, TILE_TREE_MID_BOTTOM_TO_GROUND
} & FOREST_DOMAIN

INNER_BOUNDARIES_RIGHT_RESTRICT = {
    TILE_TREE_TOP_TOP_WALL, TILE_TREE_TOP_TOP_TALL_GRASS,
    TILE_TREE_TOP_TOP_LIGHT_GROUND_MID, TILE_TREE_TOP_TOP_LIGHT_GROUND_RIGHT,
    TILE_TREE_TOP_TOP_GRASS, TILE_TREE_MID_MID,
    TILE_TREE_RIGHT_MID, TILE_TREE_RIGHT_BOTTOM,
    TILE_TREE_CONNECTOR, TILE_TREE_RIGHT_BOTTOM2,
    TILE_TREE_MID_MID2, TILE_TREE_MID_MID3,
    TILE_TREE_RIGHT_MID2, TILE_TREE_MID_BOTTOM,
    TILE_TREE_MID_BOTTOM_TO_GROUND,
    TILE_TREE_RIGHT_BOTTOM_TO_GROUND
} & FOREST_DOMAIN

INNER_BOUNDARIES_LEFT_RESTRICT = {
    TILE_TREE_TOP_TOP_WALL, TILE_TREE_TOP_TOP_TALL_GRASS,
    TILE_TREE_TOP_TOP_LIGHT_GROUND_MID, TILE_TREE_TOP_TOP_LIGHT_GROUND_RIGHT,
    TILE_TREE_TOP_TOP_GRASS, TILE_TREE_LEFT_MID,
    TILE_TREE_MID_MID, TILE_TREE_LEFT_BOTTOM,
    TILE_TREE_LEFT_BOTTOM2, TILE_TREE_CONNECTOR,
    TILE_TREE_MID_MID2, TILE_TREE_LEFT_MID2,
    TILE_TREE_MID_MID3, TILE_TREE_LEFT_BOTTOM3,
    TILE_TREE_LEFT_BOTTOM4, TILE_TREE_MID_BOTTOM,
    TILE_TREE_LEFT_BOTTOM_TO_GROUND,
    TILE_TREE_MID_BOTTOM_TO_GROUND,
    TILE_FENCE_MID, TILE_FENCE_MID2
} & FOREST_DOMAIN

# ----------------------------------------------------------------------------
# Build adjacency rules from map image (MATCH → FILTER → CLEAN)
# ----------------------------------------------------------------------------
def _build_adjacency_from_map():
    try:
        map_img = Image.open(MAP_PATH).convert("RGBA")
        ts_img  = Image.open(SPRITESHEET_PATH).convert("RGBA")
    except FileNotFoundError as e:
        print(f"Adjacency load error: {e}")
        return defaultdict(lambda: defaultdict(set))

    rows_map, cols_map = map_img.height // TILESIZE, map_img.width // TILESIZE
    rows_ts, cols_ts   = ts_img.height // TILESIZE, ts_img.width // TILESIZE

    tile_arrays = {}
    for ry in range(rows_ts):
        for rx in range(cols_ts):
            tid = ry * cols_ts + rx
            tile_arrays[tid] = np.array(
                ts_img.crop((rx*TILESIZE, ry*TILESIZE,
                             (rx+1)*TILESIZE, (ry+1)*TILESIZE))
            )

    grid = np.zeros((rows_map, cols_map), dtype=int)
    fallback = TILE_GRASS if TILE_GRASS in FOREST_DOMAIN else next(iter(FOREST_DOMAIN), 0)
    candidate_ids = FOREST_DOMAIN & set(tile_arrays.keys())

    for r in range(rows_map):
        for c in range(cols_map):
            if (c+1)*TILESIZE > map_img.width or (r+1)*TILESIZE > map_img.height:
                grid[r,c] = fallback
                continue
            region = np.array(
                map_img.crop((c*TILESIZE, r*TILESIZE,
                              (c+1)*TILESIZE, (r+1)*TILESIZE))
            )
            best, best_err = None, float("inf")
            for tid in candidate_ids:
                arr = tile_arrays[tid]
                if arr.shape != region.shape:
                    continue
                err = ((region.astype(np.float32) - arr.astype(np.float32))**2).mean()
                if err < best_err:
                    best, best_err = tid, err
            grid[r,c] = best if best in FOREST_DOMAIN else fallback

    adj = defaultdict(lambda: defaultdict(set))
    for r in range(rows_map):
        for c in range(cols_map):
            me = int(grid[r,c])
            if me not in FOREST_DOMAIN:
                continue
            for (nr,nc,dir_) in ((r-1,c,NORTH),(r,c+1,EAST),
                                 (r+1,c,SOUTH),(r,c-1,WEST)):
                if 0 <= nr < rows_map and 0 <= nc < cols_map:
                    nb = int(grid[nr,nc])
                    if nb in FOREST_DOMAIN:
                        adj[me][dir_].add(nb)

    cleaned = defaultdict(lambda: defaultdict(set))
    for tid, dirs in adj.items():
        for d, neighs in dirs.items():
            valid = {n for n in neighs if n in FOREST_DOMAIN}
            if valid:
                cleaned[tid][d] = valid

    return cleaned

adjacency_rules_forest = _build_adjacency_from_map()

# --- Weights ---
tile_weights_forest = {tid: 1 for tid in FOREST_DOMAIN}
for tid in (TREES & FOREST_DOMAIN):
    tile_weights_forest[tid] = 20

# --- WALKABLE TILES ---
potential_walkable = {
    TILE_GRASS, TILE_GRASS2, TILE_GRASS3, TILE_TALL_GRASS, TILE_GRASS4,
    TILE_GRASS5, TILE_DARK_GROUND_LEFT_TOP, TILE_DARK_GROUND_MID_TOP,
    TILE_DARK_GROUND_RIGHT_TOP, TILE_LIGHT_GROUND_LEFT_TOP,
    TILE_LIGHT_GROUND_MID_TOP, TILE_LIGHT_GROUND_RIGHT_TOP,
    TILE_DARK_GROUND_LEFT_MID, TILE_DARK_GROUND_MID_MID,
    TILE_DARK_GROUND_RIGHT_MID, TILE_DARK_GROUND_LEFT_BOTTOM,
    TILE_DARK_GROUND_MID_BOTTOM, TILE_DARK_GROUND_RIGHT_BOTTOM,
    TILE_LIGHT_GROUND_LEFT_BOTTOM, TILE_LIGHT_GROUND_MID_BOTTOM,
    TILE_LIGHT_GROUND_RIGHT_BOTTOM, TILE_FLOWER, TILE_FENCE_MID,
    TILE_FENCE_MID2, TILE_DARK_GROUND_MID_MID2, TILE_DARK_GROUND_MID_MID3,
    TILE_DARK_GROUND_MID_MID4, TILE_DARK_GROUND_MID_MID5
} | ADDITIONAL_WALKABLE

WALKABLE_TILES = potential_walkable & FOREST_DOMAIN

# --- Sokoban mapping & hole integration ---

# 1) Load Tanibo sheet and grab one ID as our “hole” sprite
TANIBO_HOLE_ID = 727
if os.path.exists(TANIBO_SPRITESHEET_PATH):
    timg = Image.open(TANIBO_SPRITESHEET_PATH)
    ntx, nty = timg.width // TILESIZE, timg.height // TILESIZE
    TANIBO_IDS = {r*ntx + c: (c, r) for r in range(nty) for c in range(ntx)}
    timg.close()
    # pick the first valid Tanibo tile as the hole
    # TANIBO_HOLE_ID = next(iter(TANIBO_IDS))
else:
    TANIBO_IDS = {}

# 2) Define Sokoban grid→tile map
SOKOBAN_BOX_ID = 9998
soko_floor = TILE_GRASS
soko_wall  = SHORT_BUSH if SHORT_BUSH in FOREST_DOMAIN else TILE_TREE_MID_MID

SOKOBAN_GRID_TO_TILE_MAP = {
    0: soko_floor,
    1: soko_wall,
    2: TANIBO_HOLE_ID,
    3: SOKOBAN_BOX_ID,
    4: soko_floor,
}

# 3) Integrate box + hole into WFC domain, adjacency, weights, sprites
# Define separate domains
SOKOBAN_DOMAIN = {SOKOBAN_BOX_ID, TANIBO_HOLE_ID} if TANIBO_HOLE_ID else {SOKOBAN_BOX_ID}

# FOREST_DOMAIN |= {SOKOBAN_BOX_ID}
# if TANIBO_HOLE_ID:
#     FOREST_DOMAIN.add(TANIBO_HOLE_ID)

# clone adjacency + weights from floor
base_adj = adjacency_rules_forest[soko_floor]
adjacency_rules_forest[SOKOBAN_BOX_ID] = {d: set(base_adj[d]) for d in base_adj}
tile_weights_forest[SOKOBAN_BOX_ID]  = tile_weights_forest[soko_floor]

if TANIBO_HOLE_ID:
    adjacency_rules_forest[TANIBO_HOLE_ID] = {d: set(base_adj[d]) for d in base_adj}
    tile_weights_forest[TANIBO_HOLE_ID]    = tile_weights_forest[soko_floor]

# --- Sprite mapping ---
tile_sprites = {}
# forest tiles …
for tid, (cx, cy) in FOREST_TILE_IDS.items():
    tile_sprites[tid] = ("forest", cx*TILESIZE, cy*TILESIZE)

# box sprite
if os.path.exists(STONE_SPRITE_PATH):
    tile_sprites[SOKOBAN_BOX_ID] = ("stone", 0, 0)

# hole sprite
if TANIBO_HOLE_ID and TANIBO_HOLE_ID in TANIBO_IDS:
    cx, cy = TANIBO_IDS[TANIBO_HOLE_ID]
    tile_sprites[TANIBO_HOLE_ID] = ("tanibo", cx*TILESIZE, cy*TILESIZE)


# --- Player & end-highlight sprites (NEW) ---
if os.path.exists(PLAYER_SPRITE_PATH):
    tile_sprites[PLAYER_ID]   = ("player", 0, 0)   # whole image 16×16
tile_sprites[END_HILITE]     = ("forest", 0, 0)   # transparent overlay

# --- Summary ---
print(f"FOREST_DOMAIN: {len(FOREST_DOMAIN)} tiles")
print(f"WALKABLE_TILES: {len(WALKABLE_TILES)} tiles")
print(f"Adjacency rules: {len(adjacency_rules_forest)} tiles")
print(f"Sprite mappings: {len(tile_sprites)} entries")
