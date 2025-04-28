from collections import defaultdict
from map_parser import prepare_wfc_input

SPRITESHEET_PATH = "./Pokemon_WFC_map_puzzle/tileset_forest.png"

wfc_input_array, rows, cols, movable_ids, unique_ids_set = prepare_wfc_input("./Pokemon_WFC_map_puzzle/VERTANIA-WALD (1.0).map", None, None, True)

# Tile Types For Forest Puzzle
TILE_GRASS                 = 1
TILE_ROAD_SIGN_SPECIAL     = 2
TILE_ROAD_SIGN             = 3
TILE_GRASS2                = 8
TILE_GRASS3                = 9
TILE_TALL_GRASS            = 13
TILE_GRASS4                = 16
TILE_GRASS5                = 17
TILE_ROOF = 68
TILE_ROOF2 = 69
TILE_ROOF3 = 70
TILE_ROOF4 = 76
TILE_ROOF5 = 77
TILE_ROOF6 = 78
TILE_HOUSE_WALL_LEFT_MID = 92
TILE_HOUSE_WALL_MID_MID = 93
TILE_HOUSE_WALL_RIGHT_MID = 94
TILE_HOUSE_WALL_LEFT_BOTTOM = 100
TILE_HOUSE_WALL_MID_BOTTOM = 101
TILE_HOUSE_WALL_RIGHT_BOTTOM = 102
TILE_DARK_GROUND_LEFT_TOP = 208
TILE_DARK_GROUND_MID_TOP = 209
TILE_DARK_GROUND_RIGHT_TOP = 210
TILE_LIGHT_GROUND_LEFT_TOP = 211
TILE_LIGHT_GROUND_MID_TOP = 212
TILE_LIGHT_GROUND_RIGHT_TOP = 213
TILE_DARK_GROUND_LEFT_MID = 216
TILE_DARK_GROUND_MID_MID = 217
TILE_DARK_GROUND_RIGHT_MID = 218
TILE_DARK_GROUND_LEFT_BOTTOM = 224
TILE_DARK_GROUND_MID_BOTTOM = 225
TILE_DARK_GROUND_RIGHT_BOTTOM = 226
TILE_LIGHT_GROUND_LEFT_BOTTOM = 227
TILE_LIGHT_GROUND_MID_BOTTOM = 228
TILE_LIGHT_GROUND_RIGHT_BOTTOM = 229
# Here the name is Fence, follow by the edge it connect with are also fences
TILE_FENCE_BOTTOM_RIGHT = 234
TILE_FENCE_TOP_BOTTOM_RIGHT = 241
TILE_FENCE_TOP_RIGHT = 242
TILE_FENCE_TOP_LEFT = 243
TILE_FENCE_TOP = 249
TILE_DARK_GROUND_MID_MID2 = 254
TILE_DARK_GROUND_MID_MID3 = 255
TILE_DARK_GROUND_MID_MID4 = 262
TILE_DARK_GROUND_MID_MID5 = 263
TILE_LIGHT_GROUND_BOTTOM_HOUSE = 377
TILE_ROOF_BOTTOM_HOUSE_BODY1 = 387
TILE_ROOF_BOTTOM_HOUSE_BODY2 = 388
TILE_ROOF_BOTTOM_HOUSE_BODY1 = 389
TILE_ENTER_DOOR_LEFT_TOP = 392
TILE_ENTER_DOOR_MID_TOP  = 393
TILE_ENTER_DOOR_RIGHT_TOP = 394
TILE_ENTER_DOOR_LEFT_MID = 400
TILE_ENTER_DOOR_MID_MID  = 401
TILE_ENTER_DOOR_RIGHT_MID = 402
TILE_ENTER_DOOR_MID_BOTTOM = 409
TILE_WINDOW = 437
TILE_WINDOW_LEFT_BORDER = 438
TILE_WINDOW_RIGHT_BORDER = 439
TILE_TREE_TOP_TOP_GRASS = 641
TILE_FLOWER = 642
TILE_TREE_TOP_TOP_WALL = 643
TILE_TREE_TOP_TOP_TALL_GRASS = 644
TILE_TREE_TOP_TOP_LIGHT_GROUND_MID = 646
TILE_TREE_TOP_TOP_LIGHT_GROUND_RIGHT = 647
TILE_TREE_LEFT_MID = 648
TILE_TREE_MID_MID = 649
TILE_TREE_RIGHT_MID = 650
TILE_FENCE_DOOR_LEFT = 651
TILE_FENCE_DOOR_MID = 652
TILE_FENCE_DOOR_RIGHT = 653
TILE_TREE_LEFT_BOTTOM = 654
TILE_TREE_RIGHT_BOTTOM = 655
TILE_TREE_LEFT_BOTTOM2 = 656
TILE_TREE_MID_BOTTOM_OTHER_TREE = 657
TILE_TREE_RIGHT_BOTTOM = 658
TILE_LIGHT_GROUND_TOP_HOUSE = 659
TILE_GRASS_BOTTOM_HOUSE_ON_RIGHT = 660
TILE_LIGHT_GROUND_LEFT_BOTTOM_HOUSE = 661
TILE_TREE_MID_MID2 = 662
TILE_TREE_LEFT_MID2 = 664
TILE_TREE_MID_MID3 = 665
TILE_TREE_RIGHT_MID2 = 666
TILE_LIGHT_GROUND_RIGHT_BOTTOM_HOUSE = 668
TILE_GRASS_BOTTOM_HOUSE_ON_LEFT = 669
TILE_TREE_LEFT_BOTTOM3 = 670
TILE_TREE_LEFT_BOTTOM4 = 672
TILE_TREE_MID_BOTTOM = 673
TILE_TREE_RIGHT_BOTTOM2 = 674
TILE_TREE_LEFT_BOTTOM_TO_GROUND = 675
TILE_TREE_MID_BOTTOM_TO_GROUND = 676
TILE_TREE_RIGHT_BOTTOM_TO_GROUND = 677
TILE_FENCE_MID = 678
TILE_FENCE_MID = 679

TILE_PLAYER = 900
TILE_GRASS_HOLE = 901
TILE_GRASS_STONE = 902

TILE_GRASS_BLOCKER = 5


# Defined the size of the WFC generated graph here
WORLD_X = 20
WORLD_Y = 20

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
tileWeights[TILE_PLAYER] = 1
tileWeights[TILE_GRASS_HOLE] = 1
tileWeights[TILE_GRASS_STONE] = 1

list2 = [TILE_TREE_LEFT_MID, TILE_TREE_MID_MID, TILE_TREE_RIGHT_MID, TILE_TREE_LEFT_BOTTOM, TILE_TREE_RIGHT_BOTTOM,
         TILE_TREE_RIGHT_BOTTOM, TILE_TREE_LEFT_BOTTOM2, TILE_TREE_MID_BOTTOM_OTHER_TREE, TILE_TREE_RIGHT_BOTTOM, 
         TILE_TREE_RIGHT_BOTTOM2, TILE_TREE_MID_MID3, TILE_TREE_LEFT_BOTTOM_TO_GROUND, TILE_TREE_MID_BOTTOM_TO_GROUND, 
         TILE_TREE_RIGHT_BOTTOM_TO_GROUND]



solution_set_tiles = {TILE_GRASS, 
                      TILE_GRASS2,
TILE_GRASS3,
TILE_TALL_GRASS,
TILE_GRASS4,
TILE_GRASS5,
TILE_DARK_GROUND_LEFT_TOP,
TILE_DARK_GROUND_MID_TOP,
TILE_DARK_GROUND_RIGHT_TOP,
TILE_DARK_GROUND_LEFT_MID,
TILE_DARK_GROUND_MID_MID,
TILE_DARK_GROUND_RIGHT_MID,
TILE_DARK_GROUND_LEFT_BOTTOM,
TILE_DARK_GROUND_MID_BOTTOM,
TILE_DARK_GROUND_RIGHT_BOTTOM,
}

solution_set_tiles2 = {TILE_GRASS, 
                      TILE_GRASS2,
TILE_GRASS3,
TILE_TALL_GRASS,
TILE_GRASS4,
TILE_GRASS5,
}

solution_set_tiles3 = {
TILE_DARK_GROUND_LEFT_TOP,
TILE_DARK_GROUND_MID_TOP,
TILE_DARK_GROUND_RIGHT_TOP,
TILE_DARK_GROUND_LEFT_MID,
TILE_DARK_GROUND_MID_MID,
TILE_DARK_GROUND_RIGHT_MID,
TILE_DARK_GROUND_LEFT_BOTTOM,
TILE_DARK_GROUND_MID_BOTTOM,
TILE_DARK_GROUND_RIGHT_BOTTOM,
}

blocker_set_tiles = {TILE_TREE_LEFT_MID,
TILE_TREE_MID_MID,
TILE_TREE_RIGHT_MID,
TILE_TREE_LEFT_BOTTOM,
TILE_TREE_RIGHT_BOTTOM,
TILE_TREE_LEFT_BOTTOM2,
TILE_TREE_MID_BOTTOM_OTHER_TREE,
TILE_TREE_RIGHT_BOTTOM,
TILE_TREE_RIGHT_BOTTOM2,
TILE_TREE_MID_MID3,
TILE_TREE_TOP_TOP_GRASS,
TILE_TREE_TOP_TOP_WALL,
TILE_TREE_TOP_TOP_TALL_GRASS,
TILE_TREE_TOP_TOP_LIGHT_GROUND_MID,
TILE_TREE_TOP_TOP_LIGHT_GROUND_RIGHT,
TILE_TREE_LEFT_BOTTOM_TO_GROUND,
TILE_TREE_MID_BOTTOM_TO_GROUND,
TILE_TREE_RIGHT_BOTTOM_TO_GROUND,
TILE_ROAD_SIGN_SPECIAL,
TILE_ROAD_SIGN }

tileWeights[13] = 200
""" tileWeights[665] = 100000
tileWeights[TILE_TREE_LEFT_MID] = 100000
tileWeights[TILE_TREE_MID_MID] = 100000
tileWeights[TILE_TREE_RIGHT_MID] = 100000
tileWeights[TILE_TREE_LEFT_BOTTOM] = 100000
tileWeights[TILE_TREE_RIGHT_BOTTOM] = 100000
tileWeights[TILE_TREE_LEFT_BOTTOM2] = 100000 """

for i in blocker_set_tiles:
    tileWeights[i] = 100000000000
tileWeights[TILE_TREE_MID_BOTTOM_OTHER_TREE] = 100000000000


sorted_weights = dict(sorted(tileWeights.items(), key=lambda item: item[1], reverse=True))
""" TILE_TREE_LEFT_MID = 648
TILE_TREE_MID_MID = 649
TILE_TREE_RIGHT_MID
TILE_TREE_LEFT_BOTTOM = 654
TILE_TREE_RIGHT_BOTTOM = 655
TILE_TREE_LEFT_BOTTOM2 = 656
TILE_TREE_MID_BOTTOM_OTHER_TREE = 657
TILE_TREE_RIGHT_BOTTOM = 658 """

expanded_blocker_set = set(blocker_set_tiles)  # start with original

for tile in blocker_set_tiles:
    if tile in adjacency_rules:
        neighbors = adjacency_rules[tile]
        for direction in neighbors:
            expanded_blocker_set.update(neighbors[direction])

blocker_set_tiles = expanded_blocker_set
blocker_set_tiles.remove(1)
blocker_set_tiles.remove(13)
remove_list = [209, 216, 217, 218, 93, 224, 225, 226, 9, 16, 17, 660, 642, 229]
# 209, 216, 217, 218, 93, 224, 225, 226, 8, 9, 16, 17, 660, 642, 229
for i in remove_list:
    blocker_set_tiles.remove(i)

# adjacency_rules = extract_adjacency_rules(wfc_input_array)
    # Very permissive: allow player, hole, stone to connect to grass and path

allowed_neighbors = adjacency_rules.keys()

for special_tile in [TILE_PLAYER]:
    for dir in [NORTH, EAST, SOUTH, WEST]:
        adjacency_rules[special_tile][dir] = set(allowed_neighbors)
        for neighbor in allowed_neighbors:
            adjacency_rules[neighbor][dir].add(special_tile)

for special_tile in [TILE_GRASS_HOLE, TILE_GRASS_STONE]:
    for dir in [NORTH, EAST, SOUTH, WEST]:
        adjacency_rules[special_tile][dir] = set(solution_set_tiles2)
        for neighbor in allowed_neighbors:
            adjacency_rules[neighbor][dir].add(special_tile)

""" for special_tile in [TILE_PLAYER, TILE_GRASS_HOLE, TILE_GRASS_STONE]:
    for dir in [NORTH, EAST, SOUTH, WEST]:
        adjacency_rules[special_tile][dir] -= set(list2) """

for special_tile in [TILE_PLAYER, TILE_GRASS_HOLE, TILE_GRASS_STONE]:
    for dir in [NORTH, EAST, SOUTH, WEST]:
         adjacency_rules[special_tile][dir].add(3)
         adjacency_rules[3][dir].add(special_tile)

for dir in [NORTH, EAST, SOUTH, WEST]:
    adjacency_rules[3][dir].update(solution_set_tiles)  # ✅ CORRECT
    for neighbor in solution_set_tiles:
        adjacency_rules[neighbor][dir].add(3)
    
for dir in [NORTH, EAST, SOUTH, WEST]:
    adjacency_rules[3][dir].add(3)

# Disallow collapsing into special tiles
for tile_id, neighbors in adjacency_rules.items():
    for direction, allowed_set in neighbors.items():
        allowed_set.difference_update({TILE_PLAYER, TILE_GRASS_HOLE, TILE_GRASS_STONE})
        for neighbor in allowed_neighbors:
            adjacency_rules[neighbor][dir].add(special_tile)


blocker_set_tiles = {TILE_TREE_LEFT_MID,
TILE_TREE_MID_MID,
TILE_TREE_RIGHT_MID,
TILE_TREE_LEFT_BOTTOM,
TILE_TREE_RIGHT_BOTTOM,
TILE_TREE_LEFT_BOTTOM2,
TILE_TREE_MID_BOTTOM_OTHER_TREE,
TILE_TREE_RIGHT_BOTTOM,
TILE_TREE_RIGHT_BOTTOM2,
TILE_TREE_MID_MID3,
TILE_TREE_TOP_TOP_GRASS,
TILE_TREE_TOP_TOP_WALL,
TILE_TREE_TOP_TOP_TALL_GRASS,
TILE_TREE_TOP_TOP_LIGHT_GROUND_MID,
TILE_TREE_TOP_TOP_LIGHT_GROUND_RIGHT,
TILE_TREE_LEFT_BOTTOM_TO_GROUND,
TILE_TREE_MID_BOTTOM_TO_GROUND,
TILE_TREE_RIGHT_BOTTOM_TO_GROUND,
TILE_ROAD_SIGN_SPECIAL,
TILE_ROAD_SIGN,
TILE_GRASS_BLOCKER }

tileWeights[3] = 10
tileWeights[5] = 200
for dir in [NORTH, EAST, SOUTH, WEST]:
    adjacency_rules[3][dir] -= set(solution_set_tiles3)

for i in solution_set_tiles3:
    for dir in [NORTH, EAST, SOUTH, WEST]:
        adjacency_rules[i][dir] -= set([3])

adjacency_rules[5] = adjacency_rules[3]
for dir in [NORTH, EAST, SOUTH, WEST]:
    for neighbor in adjacency_rules[5][dir]:
        adjacency_rules[neighbor][(dir + 2) % 4].add(5)


print(tileWeights[TILE_TREE_RIGHT_MID])


