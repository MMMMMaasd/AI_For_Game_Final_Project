from collections import defaultdict
from map_parser import prepare_wfc_input

SPRITESHEET_PATH = "./Pokemon_WFC_map_puzzle/tileset_cave.png"

wfc_input_array, rows, cols, movable_ids, unique_ids_set = prepare_wfc_input("./Pokemon_WFC_map_puzzle/TANIBO (2.35).map", None, None, False)

# Tile Types For Tanoby Key (Rock) Puzzle

TILE_DIRT = 647

TILE_ROCK_EDGE_ANGLED_RIGHT = 695
TILE_ROCK_LEDGE_BOTTOM_LEFT = 702
TILE_ROCK_LEDGE_BOTTOM_RIGHT = 703
TILE_ROCK_LEDGE_BOTTOM_MID = 706
TILE_ROCK_DIVOT_LEFT = 740
TILE_ROCK_DIVOT_RIGHT = 741
TILE_ROCK_LEDGE_TOP_LEFT = 748
TILE_ROCK_LEDGE_TOP_RIGHT = 749

TILE_DIRT_EDGE_LEFT = 763
TILE_DIRT_EDGE_RIGHT = 764
TILE_LIGHT_DIRT = 765

TILE_LIGHT_DIRT_SPOT_BOTTOM_LEFT = 768
TILE_LIGHT_DIRT_SPOT_BOTTOM_RIGHT = 769

TILE_ROCK = 770
TILE_DIRT_EDGE_BOTTOM_MID = 772

TILE_BOULDER_SPOT = 774
TILE_ROCK_VERTICAL_DIAGONAL_LEFT = 776
TILE_ROCK_VERTICAL_MID = 777
TILE_ROCK_VERTICAL_DIAGONAL_RIGHT = 778

TILE_ROCK_WALL_LEFT = 779
TILE_ROCK_WALL_RIGHT = 780
TILE_ROCK_WALL_BOTTOM_LEFT = 781
TILE_ROCK_WALL_BOTTOM_MID = 782
TILE_ROCK_WALL_BOTTOM_RIGHT = 783

TILE_ROCK_VERTICAL_DIAGONAL_LEFT2 = 784
TILE_ROCK_VERTICAL_DIAGONAL_MID2 = 785
TILE_ROCK_VERTICAL_DIAGONAL_RIGHT2 = 786

TILE_ROCK_WALL_LEFT2 = 787
TILE_ROCK_WALL_RIGHT2 = 788
TILE_ROCK_WALL_BOTTOM_LEFT2 = 789
TILE_ROCK_WALL_BOTTOM_MID2 = 790

TILE_ROCK_VERTICAL_CURVED_TOP_RIGHT = 792
TILE_ROCK_VERTICAL_MID_MID = 793
TILE_ROCK_VERTICAL_CURVED_TOP_LEFT = 794

# Defined the size of the WFC generated graph here
WORLD_X = 10
WORLD_Y = 10

# Spritesheet tile size (original), and upscale factor
# Pokemon ROM map png is 16 pixel per block
TILESIZE = 16
SCALETILE = 2


# Directions
NORTH = 0
EAST  = 1
SOUTH = 2
WEST  = 3

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
adjacency_rules = extract_adjacency_rules(wfc_input_array)

def get_tile_weights_from_map(tile_map):
    tile_counts = defaultdict(int)

    # Count frequency of each tile in the map
    for row in tile_map:
        for tile in row:
            tile_counts[tile] += 1

    return dict(tile_counts)

def assign_tile_sprite(unique_ids_set):
    tileSprites = {}
    tile_constants = {name: value for name, value in globals().items() if name.startswith('TILE_') and isinstance(value, int)}
    for name, tile_id in tile_constants.items():
        x = (tile_id % 8) * 16
        y = (tile_id // 8) * 16
        tileSprites[tile_id] = (x, y)
    
    return tileSprites
        

tileWeights = get_tile_weights_from_map(wfc_input_array)
tileSprites = assign_tile_sprite(unique_ids_set)
print(tileSprites)
