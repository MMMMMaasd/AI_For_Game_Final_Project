from collections import defaultdict
from PIL import Image
import os
import numpy as np

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

# --- Forest Tile IDs (natural/world) ---
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
TILE_TREE_RIGHT_BOTTOM              = 674
TILE_TREE_LEFT_BOTTOM_TO_GROUND     = 675
TILE_TREE_MID_BOTTOM_TO_GROUND      = 676
TILE_TREE_RIGHT_BOTTOM_TO_GROUND    = 677
TILE_FENCE_MID                      = 678
TILE_FENCE_MID2                     = 679

# --- Sokoban holes (Tanibo sheet) ---
TILE_BOULDER_SPOTS = {719, 727}

# ----------------------------------------------------------------------------
# Phase 1 → Build forest domain from your forest spritesheet
# ----------------------------------------------------------------------------
FOREST_TILE_IDS    = {}
FOREST_FLOOR_TILES = set()
FOREST_WALL_TILES  = set()

TREES = {
    TILE_TREE_TOP_TOP_WALL,
    TILE_TREE_TOP_TOP_TALL_GRASS,
    TILE_TREE_TOP_TOP_LIGHT_GROUND_MID,
    TILE_TREE_TOP_TOP_LIGHT_GROUND_RIGHT,
    TILE_TREE_TOP_TOP_GRASS,
    TILE_TREE_CONNECTOR,
    TILE_TREE_MID_MID,
    TILE_TREE_MID_MID3,
    TILE_TREE_LEFT_MID2,
    TILE_TREE_RIGHT_MID2,
    TILE_TREE_MID_BOTTOM,
    TILE_TREE_MID_BOTTOM_TO_GROUND
    
}

TREE_TOP_MIDS = {
    TILE_TREE_TOP_TOP_WALL,
    TILE_TREE_TOP_TOP_TALL_GRASS,
    TILE_TREE_TOP_TOP_LIGHT_GROUND_MID,
    TILE_TREE_TOP_TOP_LIGHT_GROUND_RIGHT,
    TILE_TREE_TOP_TOP_GRASS,
    TILE_TREE_CONNECTOR
}


TREE_MIDS_MIDS = {
    TILE_TREE_MID_MID,
    TILE_TREE_MID_MID3
}

TREE_LEFT_MIDS = {TILE_TREE_LEFT_MID2}
TREE_RIGHT_MIDS = {TILE_TREE_RIGHT_MID2}

TREE_BOTTOMS_MIDS = {
    TILE_TREE_MID_BOTTOM,
    TILE_TREE_CONNECTOR
}

TREE_BOTTOMS_TO_GROUND = {
    TILE_TREE_MID_BOTTOM_TO_GROUND
}

INNER_BOUNDARIES_RIGHT_RESTRICT = {
    TILE_TREE_TOP_TOP_WALL,
    TILE_TREE_TOP_TOP_TALL_GRASS,
    TILE_TREE_TOP_TOP_LIGHT_GROUND_MID,
    TILE_TREE_TOP_TOP_LIGHT_GROUND_RIGHT,
    TILE_TREE_TOP_TOP_GRASS,
    TILE_TREE_TOP_TOP_LIGHT_GROUND_MID,
    TILE_TREE_MID_MID,
    TILE_TREE_RIGHT_MID,
    TILE_TREE_RIGHT_BOTTOM,
    TILE_TREE_CONNECTOR,
    TILE_TREE_RIGHT_BOTTOM2,
    TILE_TREE_MID_MID2,
    TILE_TREE_MID_MID3,
    TILE_TREE_RIGHT_MID2,
    TILE_TREE_MID_BOTTOM,
    TILE_TREE_RIGHT_BOTTOM,
    TILE_TREE_MID_BOTTOM_TO_GROUND,
    TILE_TREE_RIGHT_BOTTOM_TO_GROUND
}

INNER_BOUNDARIES_LEFT_RESTRICT = {
    TILE_TREE_TOP_TOP_WALL,
    TILE_TREE_TOP_TOP_TALL_GRASS,
    TILE_TREE_TOP_TOP_LIGHT_GROUND_MID,
    TILE_TREE_TOP_TOP_LIGHT_GROUND_RIGHT,
    TILE_TREE_TOP_TOP_GRASS,
    TILE_TREE_TOP_TOP_LIGHT_GROUND_MID,
    TILE_TREE_LEFT_MID,
    TILE_TREE_MID_MID,
    TILE_TREE_LEFT_BOTTOM,
    TILE_TREE_LEFT_BOTTOM2,
    TILE_TREE_CONNECTOR,
    TILE_TREE_MID_MID2,
    TILE_TREE_LEFT_MID2,
    TILE_TREE_MID_MID3,
    TILE_TREE_LEFT_BOTTOM3,
    TILE_TREE_LEFT_BOTTOM4,
    TILE_TREE_MID_BOTTOM,
    TILE_TREE_LEFT_BOTTOM_TO_GROUND,
    TILE_TREE_MID_BOTTOM_TO_GROUND,
    TILE_FENCE_MID,
    TILE_FENCE_MID2,
}

WALKABLE_TILES = {
    TILE_GRASS,
    TILE_GRASS2,
    TILE_GRASS3,
    TILE_TALL_GRASS,
    TILE_GRASS4,
    TILE_GRASS5,
    TILE_DARK_GROUND_LEFT_TOP,
    TILE_DARK_GROUND_MID_TOP,
    TILE_DARK_GROUND_RIGHT_TOP,
    TILE_LIGHT_GROUND_LEFT_TOP,
    TILE_LIGHT_GROUND_MID_TOP,
    TILE_LIGHT_GROUND_RIGHT_TOP,
    TILE_DARK_GROUND_LEFT_MID,
    TILE_DARK_GROUND_MID_MID,
    TILE_DARK_GROUND_RIGHT_MID,
    TILE_DARK_GROUND_LEFT_BOTTOM,
    TILE_DARK_GROUND_MID_BOTTOM,
    TILE_DARK_GROUND_RIGHT_BOTTOM,
    TILE_LIGHT_GROUND_LEFT_BOTTOM,
    TILE_LIGHT_GROUND_MID_BOTTOM,
    TILE_LIGHT_GROUND_RIGHT_BOTTOM,
    TILE_DARK_GROUND_MID_MID2,
    TILE_DARK_GROUND_MID_MID3,
    TILE_DARK_GROUND_MID_MID4,
    TILE_DARK_GROUND_MID_MID5,
    TILE_FLOWER
}


try:
    img  = Image.open(SPRITESHEET_PATH)
    cols = img.width  // TILESIZE
    rows = img.height // TILESIZE
    img.close()

    # map tile_id → (col,row)
    FOREST_TILE_IDS = {
        r*cols + c: (c, r)
        for r in range(rows)
        for c in range(cols)
    }

    # designate which sheet‐rows are floor vs wall
    floor_rows = (0,1,6,7,10,11,12,13,16,17,21,22,23,24,26,27,28,31,32,33,41,47,48,49,50,51,52,54,80,81,82,83,84,85)
    wall_rows  = (2,3,4,8,9,11,14,15,20,25,29,30,42,43,53,80,81,82,83,84)

    FOREST_FLOOR_TILES = { tid for tid,(c,r) in FOREST_TILE_IDS.items() if r in floor_rows }
    FOREST_WALL_TILES  = { tid for tid,(c,r) in FOREST_TILE_IDS.items() if r in wall_rows }

    # always ensure these fallbacks exist
    FOREST_FLOOR_TILES.add(TILE_GRASS)
    FOREST_WALL_TILES.add(TILE_TREE_MID_MID)

except Exception:
    FOREST_FLOOR_TILES = {TILE_GRASS}
    FOREST_WALL_TILES  = {TILE_TREE_MID_MID}

# ----------------------------------------------------------------------------
# BLACKLIST any unwanted building/steel IDs you clicked on
# ----------------------------------------------------------------------------
BUILDING_BLACKLIST = {68, 76, 77, 78, 94, 102, 439, 643, 659}
FOREST_FLOOR_TILES -= BUILDING_BLACKLIST
FOREST_WALL_TILES  -= BUILDING_BLACKLIST

# ----------------------------------------------------------------------------
# combine final domain
# ----------------------------------------------------------------------------
FOREST_DOMAIN = FOREST_FLOOR_TILES | FOREST_WALL_TILES

# ----------------------------------------------------------------------------
# adjacency based on your real map image
# ----------------------------------------------------------------------------
def _build_adjacency_from_map():
    map_img = Image.open(MAP_PATH).convert("RGBA")
    ts_img  = Image.open(SPRITESHEET_PATH).convert("RGBA")

    rows_map = map_img.height // TILESIZE
    cols_map = map_img.width  // TILESIZE
    rows_ts  = ts_img.height // TILESIZE
    cols_ts  = ts_img.width  // TILESIZE

    # slice the spritesheet → arrays
    tile_arrays = {}
    for ry in range(rows_ts):
        for rx in range(cols_ts):
            tid = ry*cols_ts + rx
            patch = ts_img.crop((rx*TILESIZE, ry*TILESIZE,
                                 (rx+1)*TILESIZE, (ry+1)*TILESIZE))
            tile_arrays[tid] = np.array(patch)

    # match map → grid of tile‐IDs
    grid = np.zeros((rows_map, cols_map), dtype=int)
    for r in range(rows_map):
        for c in range(cols_map):
            region = np.array(map_img.crop((c*TILESIZE, r*TILESIZE,
                                            (c+1)*TILESIZE, (r+1)*TILESIZE)))
            best,be = None,1e20
            for tid,arr in tile_arrays.items():
                err = ((region - arr)**2).mean()
                if err < be:
                    best,be = tid,err
            grid[r,c] = best
    
    wfc_input_array = grid.tolist()
    from collections import defaultdict
    adjacency_rules = defaultdict(lambda: defaultdict(set))

    rows = len(wfc_input_array)
    cols = len(wfc_input_array[0])

    for y in range(rows):
        for x in range(cols):
            center = wfc_input_array[y][x]

            if y > 0:
                adjacency_rules[center][NORTH].add(wfc_input_array[y - 1][x])
            if x < cols - 1:
                adjacency_rules[center][EAST].add(wfc_input_array[y][x + 1])
            if y < rows - 1:
                adjacency_rules[center][SOUTH].add(wfc_input_array[y + 1][x])
            if x > 0:
                adjacency_rules[center][WEST].add(wfc_input_array[y][x - 1])
    
    """
    # build adjacency rules N/E/S/W
    adj = defaultdict(lambda: defaultdict(set))
    deltas = [(-1,0), (0,1), (1,0), (0,-1)]
    for r in range(rows_map):
        for c in range(cols_map):
            me = int(grid[r,c])
            for d,(dr,dc) in enumerate(deltas):
                nr,nc = r+dr, c+dc
                if 0 <= nr < rows_map and 0 <= nc < cols_map:
                    adj[me][d].add(int(grid[nr,nc]))
    """
    return adjacency_rules

adjacency_rules_forest = _build_adjacency_from_map()

"""
def _enhance_tree_rules(adjacency_rules):
    
    for tid in (TREE_MIDS_MIDS):
        for d in DIRECTIONS:
            adjacency_rules[tid][d] = set()
    
    for tid in TREE_TOP_MIDS:
        adjacency_rules[tid][SOUTH] = set(TREE_MIDS_MIDS)
    
    # Tree mids must have tree tops above OR other mids below
    for tid in TREE_MIDS_MIDS:
        adjacency_rules[tid][NORTH] = set(TREE_TOP_MIDS)
        adjacency_rules[tid][WEST] = set(TREE_LEFT_MIDS)
        adjacency_rules[tid][EAST] = set(TREE_RIGHT_MIDS)
        adjacency_rules[tid][SOUTH] = set(TREE_BOTTOMS_MIDS)
        
    for tid in TREE_LEFT_MIDS:
        adjacency_rules[tid][EAST] = set(TREE_MIDS_MIDS)
    
    for tid in TREE_RIGHT_MIDS:
        adjacency_rules[tid][WEST] = set(TREE_MIDS_MIDS)
    
    ground_top = set()
    ground_top.add(TILE_TREE_MID_BOTTOM)
    

        
    adjacency_rules[TILE_TREE_MID_BOTTOM][SOUTH] = set(TREE_BOTTOMS_TO_GROUND)
    adjacency_rules[TILE_TREE_MID_BOTTOM_TO_GROUND][NORTH] = set()
    adjacency_rules[TILE_TREE_MID_BOTTOM_TO_GROUND][NORTH] = ground_top
    adjacency_rules[TILE_TREE_CONNECTOR][SOUTH] = set(TREE_MIDS_MIDS)
    
    
    
    return adjacency_rules
"""
#adjacency_rules_forest = _enhance_tree_rules(adjacency_rules_forest)
# uniform positive weights (no zero‐weight collapse errors)
tile_weights_forest = { tid:1 for tid in FOREST_DOMAIN }

for id in TREES:
    tile_weights_forest[id] = 20

# ----------------------------------------------------------------------------
# Phase 2 → Sokoban injection definitions
# ----------------------------------------------------------------------------
SOKOBAN_BOX_ID    = 9998
SOKOBAN_FLOOR_ID  = TILE_GRASS
SOKOBAN_WALL_ID   = 5

SOKOBAN_ALLOWED_TILES = {
    SOKOBAN_BOX_ID,
    SOKOBAN_FLOOR_ID,
    SOKOBAN_WALL_ID,
} | TILE_BOULDER_SPOTS

# Sokoban adjacency:
adjacency_rules_sokoban = defaultdict(lambda: defaultdict(set))
for d in DIRECTIONS:
    adjacency_rules_sokoban[SOKOBAN_WALL_ID][d] = set(SOKOBAN_ALLOWED_TILES)
    for t in SOKOBAN_ALLOWED_TILES:
        if t != SOKOBAN_WALL_ID:
            adjacency_rules_sokoban[t][d].add(SOKOBAN_WALL_ID)

for a in (SOKOBAN_FLOOR_ID, *TILE_BOULDER_SPOTS):
    for b in (SOKOBAN_FLOOR_ID, *TILE_BOULDER_SPOTS, SOKOBAN_BOX_ID):
        for d in DIRECTIONS:
            adjacency_rules_sokoban[a][d].add(b)
            adjacency_rules_sokoban[b][d].add(a)

# ensure every key exists
for t in SOKOBAN_ALLOWED_TILES:
    for d in DIRECTIONS:
        _ = adjacency_rules_sokoban[t][d]

# Sokoban weights
tile_weights_sokoban = {
    SOKOBAN_FLOOR_ID: 10,
    SOKOBAN_WALL_ID:   5,
    SOKOBAN_BOX_ID:    1,
}
for hid in TILE_BOULDER_SPOTS:
    tile_weights_sokoban[hid] = 1

# ----------------------------------------------------------------------------
# Sprite mapping
# ----------------------------------------------------------------------------
tile_sprites = {}

# forest spritesheet entries
for tid,(cx,cy) in FOREST_TILE_IDS.items():
    tile_sprites[tid] = ('forest', cx*TILESIZE, cy*TILESIZE)

# box sprite
tile_sprites[SOKOBAN_BOX_ID] = ('stone', 0, 0)

# hole sprites from Tanibo spritesheet
TANIBO_TILE_IDS = {}
try:
    timg = Image.open(TANIBO_SPRITESHEET_PATH)
    ntx, nty = timg.width//TILESIZE, timg.height//TILESIZE
    timg.close()
    TANIBO_TILE_IDS = { r*ntx + c: (c, r)
                        for r in range(nty)
                        for c in range(ntx) }
except:
    TANIBO_TILE_IDS = {}

for hid in TILE_BOULDER_SPOTS:
    if hid in TANIBO_TILE_IDS:
        cx, cy = TANIBO_TILE_IDS[hid]
        tile_sprites[hid] = ('tanibo', cx*TILESIZE, cy*TILESIZE)
    else:
        # fallback to plain grass if missing
        tile_sprites[hid] = ('forest', TILE_GRASS, TILE_GRASS)

print("Config loaded — forest domain cleaned, blacklist applied, Tanibo holes mapped.")
