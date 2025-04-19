from collections import defaultdict

SPRITESHEET_PATH = "./example_data_file/punyworld-overworld-tileset.png"
example_tile_map = [
    [30, 9, 8, 9, 5, 8, 0, 19, 22, 27, 23, 30, 0, 24, 2, 2, 2, 2, 2, 2],
    [21, 0, 28, 25, 29, 0, 28, 25, 29, 20, 17, 21, 28, 32, 34, 23, 23, 23, 23, 31],
    [22, 0, 24, 2, 33, 29, 27, 31, 26, 19, 15, 22, 24, 2, 26, 0, 0, 28, 25, 32],
    [10, 7, 24, 34, 31, 26, 28, 32, 26, 0, 10, 7, 24, 2, 33, 29, 0, 27, 23, 23],
    [6, 4, 27, 30, 24, 33, 32, 2, 26, 0, 9, 8, 27, 23, 31, 33, 25, 25, 25, 25],
    [6, 4, 20, 21, 24, 34, 31, 34, 30, 10, 7, 0, 0, 0, 24, 2, 34, 23, 23, 23],
    [14, 4, 19, 22, 24, 26, 24, 33, 29, 6, 4, 20, 17, 21, 24, 2, 33, 29, 0, 0],
    [13, 11, 7, 28, 32, 26, 24, 2, 26, 6, 4, 19, 15, 22, 27, 23, 23, 30, 10, 7],
    [6, 1, 4, 27, 23, 30, 24, 34, 30, 9, 8, 0, 0, 0, 28, 25, 29, 0, 6, 11],
    [9, 5, 8, 0, 0, 0, 24, 26, 10, 3, 3, 3, 3, 7, 27, 23, 30, 0, 6, 1],
    [0, 0, 0, 0, 0, 0, 27, 30, 6, 1, 1, 1, 12, 8, 10, 3, 7, 0, 6, 1],
    [29, 0, 0, 10, 3, 7, 10, 3, 14, 1, 1, 1, 4, 0, 9, 5, 8, 0, 9, 13],
    [33, 29, 0, 9, 5, 8, 6, 1, 1, 1, 12, 5, 8, 0, 10, 3, 7, 0, 0, 9],
    [23, 30, 28, 29, 0, 0, 9, 5, 13, 1, 4, 10, 3, 7, 9, 13, 11, 7, 0, 0],
    [0, 28, 32, 26, 28, 25, 25, 29, 6, 12, 8, 9, 5, 8, 0, 9, 5, 8, 0, 10],
    [0, 24, 34, 30, 24, 2, 2, 26, 6, 11, 3, 7, 0, 0, 28, 25, 29, 0, 0, 9],
    [28, 32, 26, 28, 32, 2, 2, 26, 9, 5, 5, 8, 0, 0, 24, 2, 33, 25, 29, 0],
    [24, 2, 26, 27, 31, 34, 23, 30, 0, 0, 28, 25, 25, 29, 24, 2, 2, 34, 30, 0],
    [27, 31, 26, 0, 27, 30, 0, 28, 29, 0, 24, 34, 23, 30, 24, 2, 2, 33, 25, 29],
    [21, 24, 26, 0, 10, 7, 0, 24, 33, 25, 32, 26, 28, 25, 32, 2, 2, 2, 2, 26]
]

WORLD_X = 20
WORLD_Y = 20

# Spritesheet tile size (original), and upscale factor
TILESIZE = 16
SCALETILE = 2


# Directions
NORTH = 0
EAST  = 1
SOUTH = 2
WEST  = 3


# Tile Types
TILE_GRASS    = 0
TILE_WATER    = 1
TILE_FOREST   = 2
TILE_COASTN   = 3
TILE_COASTE   = 4
TILE_COASTS   = 5
TILE_COASTW   = 6
TILE_COASTNE  = 7
TILE_COASTSE  = 8
TILE_COASTSW  = 9
TILE_COASTNW  = 10
TILE_COASTNE2 = 11
TILE_COASTSE2 = 12
TILE_COASTSW2 = 13
TILE_COASTNW2 = 14
TILE_ROCKN    = 15
TILE_ROCKE    = 16
TILE_ROCKS    = 17
TILE_ROCKW    = 18
TILE_ROCKNE   = 19
TILE_ROCKSE   = 20
TILE_ROCKSW   = 21
TILE_ROCKNW   = 22
TILE_FORESTN   = 23
TILE_FORESTE   = 24
TILE_FORESTS   = 25
TILE_FORESTW   = 26
TILE_FORESTNE  = 27
TILE_FORESTSE  = 28
TILE_FORESTSW  = 29
TILE_FORESTNW  = 30
TILE_FORESTNE2 = 31
TILE_FORESTSE2 = 32
TILE_FORESTSW2 = 33
TILE_FORESTNW2 = 34


# Tile Edges
GRASS    = 0
WATER    = 1
FOREST   = 2
COAST_N  = 3
COAST_E  = 4
COAST_S  = 5
COAST_W  = 6
FOREST_N = 7
FOREST_E = 8
FOREST_S = 9
FOREST_W = 10
ROCK_N   = 11
ROCK_E   = 12
ROCK_S   = 13
ROCK_W   = 14
ROCK     = 15


# Pre-defined weights
tileWeights = {
    TILE_GRASS    : 16,
    TILE_WATER    : 4,
    TILE_FOREST   : 5,
    TILE_COASTN   : 5,
    TILE_COASTE   : 5,
    TILE_COASTS   : 5,
    TILE_COASTW   : 5,
    TILE_COASTNE  : 5,
    TILE_COASTSE  : 5,
    TILE_COASTSW  : 5,
    TILE_COASTNW  : 5,
    TILE_COASTNE2 : 2,
    TILE_COASTSE2 : 2,
    TILE_COASTSW2 : 2,
    TILE_COASTNW2 : 2,
    TILE_FORESTN  : 4,
    TILE_FORESTE  : 4,
    TILE_FORESTS  : 4,
    TILE_FORESTW  : 4,
    TILE_FORESTNE : 4,
    TILE_FORESTSE : 4,
    TILE_FORESTSW : 4,
    TILE_FORESTNW : 4,
    TILE_FORESTNE2: 2,
    TILE_FORESTSE2: 2,
    TILE_FORESTSW2: 2,
    TILE_FORESTNW2: 2,
    TILE_ROCKN    : 4,
    TILE_ROCKE    : 4,
    TILE_ROCKS    : 4,
    TILE_ROCKW    : 4,
    TILE_ROCKNE   : 4,
    TILE_ROCKSE   : 4,
    TILE_ROCKSW   : 4,
    TILE_ROCKNW   : 4,
}


tileSprites = {
    TILE_GRASS : (16, 0),
    TILE_WATER : (128, 176),
    TILE_FOREST: (16, 128),
    TILE_COASTN  : (128, 160),
    TILE_COASTE  : (144, 176),
    TILE_COASTS  : (128, 192),
    TILE_COASTW  : (112, 176),
    TILE_COASTNE : (144, 160),
    TILE_COASTSE : (144, 192),
    TILE_COASTSW : (112, 192),
    TILE_COASTNW : (112, 160),
    TILE_COASTNE2: (176, 160),
    TILE_COASTSE2: (176, 176),
    TILE_COASTSW2: (160, 176),
    TILE_COASTNW2: (160, 160),
    TILE_FORESTN  : (16, 144),
    TILE_FORESTE  : (0, 128),
    TILE_FORESTS  : (16, 112),
    TILE_FORESTW  : (32, 128),
    TILE_FORESTNE : (0, 144),
    TILE_FORESTSE : (0, 112),
    TILE_FORESTSW : (32, 112),
    TILE_FORESTNW : (32, 144),
    TILE_FORESTNE2: (96, 128),
    TILE_FORESTSE2: (96, 112),
    TILE_FORESTSW2: (112, 112),
    TILE_FORESTNW2: (112, 128),
    TILE_ROCKN   : (16, 96),
    TILE_ROCKE   : (0, 80),
    TILE_ROCKS   : (16, 64),
    TILE_ROCKW   : (32, 80),
    TILE_ROCKNE  : (0, 96),
    TILE_ROCKSE  : (0, 64),
    TILE_ROCKSW  : (32, 64),
    TILE_ROCKNW  : (32, 96),
}

# adjacency_rules = defaultdict(lambda: defaultdict(set))
# adjacency_rules = extract_adjacency_rules(example_tile_map)
def extract_adjacency_rules(tile_map):
    from collections import defaultdict
    NORTH, EAST, SOUTH, WEST = 0, 1, 2, 3
    adjacency_rules = defaultdict(lambda: defaultdict(set))

    rows = len(tile_map)
    cols = len(tile_map[0])

    for y in range(rows):
        for x in range(cols):
            center = tile_map[y][x]

            if y > 0:
                adjacency_rules[center][NORTH].add(tile_map[y - 1][x])
            if x < cols - 1:
                adjacency_rules[center][EAST].add(tile_map[y][x + 1])
            if y < rows - 1:
                adjacency_rules[center][SOUTH].add(tile_map[y + 1][x])
            if x > 0:
                adjacency_rules[center][WEST].add(tile_map[y][x - 1])

    return adjacency_rules
adjacency_rules = extract_adjacency_rules(example_tile_map)

def get_tile_weights_from_map(tile_map):
    tile_counts = defaultdict(int)

    # Count frequency of each tile in the map
    for row in tile_map:
        for tile in row:
            tile_counts[tile] += 1

    return dict(tile_counts)
tileWeights = get_tile_weights_from_map(example_tile_map)
