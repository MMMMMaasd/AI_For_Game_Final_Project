from collections import defaultdict
from map_parser import prepare_wfc_input

SPRITESHEET_PATH = "./Pokemon_WFC_map_puzzle/Tanibo_tileset.png"
PLAYER_SPRITE_PATH = "./Pokemon_WFC_map_puzzle/player_sprite.png"
STONE_SPRITE_PATH = "./Pokemon_WFC_map_puzzle/stone(box)_sprite.png"
wfc_input_array, rows, cols, movable_ids, unique_ids_set = prepare_wfc_input("./Pokemon_WFC_map_puzzle/TANIBO (2.35).map", None, None, False)


# Tile Types For Tanoby Key (Rock) Puzzle

TILE_DIRT = 647

TILE_ROCK_EDGE_ANGLED_RIGHT = 695 # Box/Stone
TILE_ROCK_LEDGE_BOTTOM_LEFT = 702 # Floor Edge
TILE_ROCK_LEDGE_BOTTOM_RIGHT = 703 # Floor Edge
TILE_ROCK_LEDGE_BOTTOM_MID = 706 # Floor Edge
TILE_ROCK_DIVOT_LEFT = 740 # Wall
TILE_ROCK_DIVOT_RIGHT = 741 #Wall
TILE_ROCK_LEDGE_TOP_LEFT = 748 #Wall
TILE_ROCK_LEDGE_TOP_RIGHT = 749 #Wall

TILE_DIRT_EDGE_LEFT = 763 # Floor Edge
TILE_LIGHT_DIRT = 764 # Middle Floor
TILE_DIRT_EDGE_RIGHT = 765 #Floor Edge

TILE_LIGHT_DIRT_SPOT_BOTTOM_LEFT = 768 # Floor Edge
TILE_LIGHT_DIRT_SPOT_BOTTOM_RIGHT = 769 # Floor Edge

TILE_ROCK = 770 # Wall
TILE_DIRT_EDGE_BOTTOM_MID = 772 # Floor Edge

TILE_BOULDER_SPOT = 774 # Hole
TILE_ROCK_VERTICAL_DIAGONAL_LEFT = 776 # Wall
TILE_ROCK_VERTICAL_MID = 777 # Wall
TILE_ROCK_VERTICAL_DIAGONAL_RIGHT = 778 # Wall

TILE_ROCK_WALL_LEFT = 779 # Wall
TILE_ROCK_WALL_RIGHT = 780 # Wall
TILE_ROCK_WALL_BOTTOM_LEFT = 781 # Wall
TILE_ROCK_WALL_BOTTOM_MID = 782 # Wall
TILE_ROCK_WALL_BOTTOM_RIGHT = 783 # Wall

TILE_ROCK_VERTICAL_DIAGONAL_LEFT2 = 784 # Wall
TILE_ROCK_VERTICAL_DIAGONAL_MID2 = 785 # Wall
TILE_ROCK_VERTICAL_DIAGONAL_RIGHT2 = 786 # Wall

TILE_ROCK_WALL_LEFT2 = 787 # Wall
TILE_ROCK_WALL_RIGHT2 = 788 # Wall
TILE_ROCK_WALL_BOTTOM_LEFT2 = 789 # Wall
TILE_ROCK_WALL_BOTTOM_MID2 = 790 # Wall
 
TILE_ROCK_VERTICAL_CURVED_TOP_RIGHT = 792 # Wall
TILE_ROCK_VERTICAL_MID_MID = 793 # Wall
TILE_ROCK_VERTICAL_CURVED_TOP_LEFT = 794 # Wall

PLAYER_TILE = 9999
STONE_TILE = 9998

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


floor_set_tiles = {TILE_LIGHT_DIRT}

wall_set_tiles = {
    # Set this only equal to TILE_ROCK for the clean/simple version
    TILE_ROCK,
    TILE_ROCK_VERTICAL_DIAGONAL_LEFT,
    TILE_ROCK_VERTICAL_MID,
    TILE_ROCK_VERTICAL_DIAGONAL_RIGHT,

    TILE_ROCK_WALL_LEFT,
    TILE_ROCK_WALL_RIGHT,
    TILE_ROCK_WALL_BOTTOM_LEFT,
    TILE_ROCK_WALL_BOTTOM_MID,
    TILE_ROCK_WALL_BOTTOM_RIGHT,

    TILE_ROCK_VERTICAL_DIAGONAL_LEFT2,
    TILE_ROCK_VERTICAL_DIAGONAL_MID2,
    TILE_ROCK_VERTICAL_DIAGONAL_RIGHT2,

    TILE_ROCK_WALL_LEFT2,
    TILE_ROCK_WALL_RIGHT2,
    TILE_ROCK_WALL_BOTTOM_LEFT2,
    TILE_ROCK_WALL_BOTTOM_MID2,

    TILE_ROCK_VERTICAL_CURVED_TOP_RIGHT,
    TILE_ROCK_VERTICAL_MID_MID,
    TILE_ROCK_VERTICAL_CURVED_TOP_LEFT,
    
    TILE_ROCK_DIVOT_LEFT,
    TILE_ROCK_DIVOT_RIGHT,
    
    TILE_ROCK_LEDGE_TOP_LEFT,
    TILE_ROCK_LEDGE_TOP_RIGHT
}

wall_on_floor_right_tiles = {
    # Set this only equal to TILE_ROCK for the clean/simple version
    #TILE_ROCK_WALL_LEFT,
    TILE_ROCK_WALL_LEFT2
    #TILE_ROCK_VERTICAL_DIAGONAL_LEFT2,
    #TILE_ROCK_VERTICAL_DIAGONAL_LEFT,
    #TILE_ROCK_DIVOT_RIGHT

}

wall_on_floor_left_tiles = {
    # Set this only equal to TILE_ROCK for the clean/simple version
    #TILE_ROCK_WALL_RIGHT,
    TILE_ROCK_WALL_RIGHT2
    #TILE_ROCK_VERTICAL_DIAGONAL_RIGHT,
    #TILE_ROCK_DIVOT_LEFT
}

wall_on_floor_top_tiles = {
    # Set this only equal to TILE_ROCK for the clean/simple version
    #TILE_ROCK_WALL_BOTTOM_LEFT,
    #TILE_ROCK_WALL_BOTTOM_RIGHT,
    TILE_ROCK_WALL_BOTTOM_MID
    #TILE_ROCK_WALL_BOTTOM_MID2,

}

wall_on_floor_bottom_tiles = {
    # Set this only equal to TILE_ROCK for the clean/simple version
    TILE_ROCK_VERTICAL_MID

}
        
target_set_tiles = {TILE_BOULDER_SPOT}

box_set_tiles = {STONE_TILE}

player_set_tiles = {PLAYER_TILE}


all_tile_ids = {
    value for name, value in globals().items()
    if name.startswith('TILE_') and isinstance(value, int)
}

for direction in [NORTH, EAST, SOUTH, WEST]:
    adjacency_rules[PLAYER_TILE][direction].update(all_tile_ids)
    adjacency_rules[TILE_ROCK_WALL_LEFT2][direction].update(all_tile_ids)
    adjacency_rules[TILE_ROCK_WALL_RIGHT2][direction].update(all_tile_ids)
    adjacency_rules[TILE_ROCK_WALL_BOTTOM_MID][direction].update(all_tile_ids)
    adjacency_rules[TILE_ROCK_VERTICAL_MID][direction].update(all_tile_ids)
    for tile_id in all_tile_ids:
        adjacency_rules[tile_id][direction].add(PLAYER_TILE)
        adjacency_rules[tile_id][direction].add(TILE_ROCK_WALL_RIGHT2)
        adjacency_rules[tile_id][direction].add(TILE_ROCK_WALL_RIGHT2)
        adjacency_rules[tile_id][direction].add(TILE_ROCK_WALL_BOTTOM_MID)
        adjacency_rules[tile_id][direction].add(TILE_ROCK_VERTICAL_MID)
        

for box_tile in box_set_tiles:
    for direction in [NORTH, EAST, SOUTH, WEST]:
        adjacency_rules[box_tile][direction].update(wall_set_tiles)
        adjacency_rules[box_tile][direction].update(floor_set_tiles)
        adjacency_rules[box_tile][direction].update(box_set_tiles)
        adjacency_rules[box_tile][direction].update(target_set_tiles)

for target_tile in target_set_tiles:
    for direction in [NORTH, EAST, SOUTH, WEST]:
        adjacency_rules[target_tile][direction].update(wall_set_tiles)
        adjacency_rules[target_tile][direction].update(floor_set_tiles)
        adjacency_rules[target_tile][direction].update(box_set_tiles)
        adjacency_rules[target_tile][direction].update(target_set_tiles)
        
for floor_tile in floor_set_tiles:
    for direction in [NORTH, EAST, SOUTH, WEST]:
        if direction == NORTH:
            print("yes")
            adjacency_rules[floor_tile][direction].update(wall_on_floor_top_tiles)
        elif direction == EAST:
            adjacency_rules[floor_tile][direction].update(wall_on_floor_right_tiles)
        elif direction == SOUTH:
            adjacency_rules[floor_tile][direction].update(wall_on_floor_bottom_tiles)
        elif direction == WEST:
            adjacency_rules[floor_tile][direction].update(wall_on_floor_left_tiles)
        adjacency_rules[floor_tile][direction].update(floor_set_tiles)
        adjacency_rules[floor_tile][direction].update(box_set_tiles)
        adjacency_rules[floor_tile][direction].update(target_set_tiles)
        
for wall_tile in wall_set_tiles:
    for direction in [NORTH, EAST, SOUTH, WEST]:
        adjacency_rules[wall_tile][direction].update(wall_set_tiles)
        adjacency_rules[wall_tile][direction].update(floor_set_tiles)
        adjacency_rules[wall_tile][direction].update(box_set_tiles)
        adjacency_rules[wall_tile][direction].update(target_set_tiles)
        

tileWeights[PLAYER_TILE] = 10000
tileWeights[STONE_TILE] = 10000
sorted_weights = dict(sorted(tileWeights.items(), key=lambda item: item[1], reverse=True))

