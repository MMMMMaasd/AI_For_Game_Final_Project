import pygame
from ClassWorld import World
from ClassDrawWorld import DrawWorld
from Config import *
from copy import deepcopy
import random
from Config import *

# === Path tile setup ===
""" PATH_TILES = {
TILE_DARK_GROUND_LEFT_MID,
TILE_DARK_GROUND_MID_MID,
TILE_DARK_GROUND_RIGHT_MID,
TILE_DARK_GROUND_LEFT_BOTTOM,
TILE_DARK_GROUND_MID_BOTTOM,
TILE_DARK_GROUND_RIGHT_BOTTOM,
TILE_DARK_GROUND_LEFT_TOP,
TILE_DARK_GROUND_MID_TOP,
TILE_DARK_GROUND_RIGHT_TOP
} """
""" PATH_TILES = {
TILE_GRASS, TILE_GRASS2, TILE_GRASS3, TILE_TALL_GRASS, TILE_GRASS4, TILE_GRASS5
} """

PATH_TILES = {
TILE_DARK_GROUND_MID_MID,
TILE_DARK_GROUND_LEFT_BOTTOM,
TILE_DARK_GROUND_RIGHT_BOTTOM,
TILE_DARK_GROUND_LEFT_TOP,
TILE_DARK_GROUND_RIGHT_TOP}

PATH_TILE = random.choice(list(PATH_TILES))

INTERACTIVE = True
INTERACTIVE_KEYPRESS = False

""" def create_path_only_adjacency_rules(original_rules, path_tile_ids):
    path_rules = deepcopy(original_rules)

    for tile_id in list(path_rules.keys()):
        if tile_id not in path_tile_ids:
            del path_rules[tile_id]
            continue

        for direction in [NORTH, EAST, SOUTH, WEST]:
            path_rules[tile_id][direction] = set(path_tile_ids)

    return path_rules
 """

""" def create_path_only_adjacency_rules(original_rules, path_tile_ids):
    path_rules = {}

    for tile_id in path_tile_ids:
        if tile_id not in original_rules:
            continue  # Skip if the tile doesn't exist in the original

        path_rules[tile_id] = {}

        for direction in [NORTH, EAST, SOUTH, WEST]:
            # Get the original neighbors in this direction
            original_neighbors = original_rules[tile_id].get(direction, set())

            # Keep only those neighbors that are in PATH_TILES
            filtered_neighbors = original_neighbors.intersection(path_tile_ids)

            path_rules[tile_id][direction] = filtered_neighbors

    return path_rules

# === Apply path-only adjacency rules ===
original_adjacency_rules = deepcopy(adjacency_rules)
adjacency_rules = create_path_only_adjacency_rules(adjacency_rules, PATH_TILES) """

""" adjacency_rules = {
    TILE_STRAIGHT_H: {
        NORTH: set(),
        EAST:  {TILE_STRAIGHT_H, TILE_TURN_NW, TILE_TURN_SW},
        SOUTH: set(),
        WEST:  {TILE_STRAIGHT_H, TILE_TURN_NE, TILE_TURN_SE}
    },
    TILE_STRAIGHT_V: {
        NORTH: {TILE_STRAIGHT_V, TILE_TURN_SE, TILE_TURN_SW},
        EAST:  set(),
        SOUTH: {TILE_STRAIGHT_V, TILE_TURN_NE, TILE_TURN_NW},
        WEST:  set()
    },
    TILE_TURN_NE: {
        NORTH: {TILE_STRAIGHT_V, TILE_TURN_SE, TILE_TURN_SW},
        EAST:  {TILE_STRAIGHT_H, TILE_TURN_NW, TILE_TURN_SW},
        SOUTH: set(),
        WEST:  set()
    },
    TILE_TURN_NW: {
        NORTH: {TILE_STRAIGHT_V, TILE_TURN_SE, TILE_TURN_SW},
        WEST:  {TILE_STRAIGHT_H, TILE_TURN_NE, TILE_TURN_SE},
        EAST:  set(),
        SOUTH: set()
    },
    TILE_TURN_SE: {
        SOUTH: {TILE_STRAIGHT_V, TILE_TURN_NE, TILE_TURN_NW},
        EAST:  {TILE_STRAIGHT_H, TILE_TURN_NW, TILE_TURN_SW},
        NORTH: set(),
        WEST:  set()
    },
    TILE_TURN_SW: {
        SOUTH: {TILE_STRAIGHT_V, TILE_TURN_NE, TILE_TURN_NW},
        WEST:  {TILE_STRAIGHT_H, TILE_TURN_NE, TILE_TURN_SE},
        NORTH: set(),
        EAST:  set()
    }
}
 """
# === Initialize pygame ===
pygame.init()
clock = pygame.time.Clock()

displaySurface = pygame.display.set_mode((WORLD_X * TILESIZE * SCALETILE, WORLD_Y * TILESIZE * SCALETILE))
pygame.display.set_caption("Wave Function Collapse")

world = World(WORLD_X, WORLD_Y)
world.set_constrain_mode("path")
drawWorld = DrawWorld(world)

# === Seed path start and end ===
world.seed_path_start(PATH_TILE)
# world.seed_path_end(PATH_TILE)

# === Run WFC to generate path ===
""" done = False
while not done:
    result = world.waveFunctionCollapse(weights_override=uniform_weights)
    #if result == 0:
    #   done = True  """

done = False
while not done:
    result = world.waveFunctionCollapse(weights_override=uniform_weights)
    drawWorld.update()
    drawWorld.draw(displaySurface)
    pygame.display.flip()
    clock.tick(30)
      # Lower FPS to visually observe WF
    if result == 0:
        done = True


print("Finish the first WFC")
#print(adjacency_rules)

# Second WFC
""" print("Start the second WFC")
world.set_constrain_mode("full") 
world.prepare_for_second_pass()
done = False
while not done:
    result = world.waveFunctionCollapse()
    drawWorld.update()
    drawWorld.draw(displaySurface)
    pygame.display.flip()
    clock.tick(30)
    if all(tile.entropy == 0 for row in world.tileRows for tile in row):
        done = True 
print("Finish the second WFC")
world.debug_uncollapsed_tiles()
print(adjacency_rules1) """




# === If you want a second WFC pass to fill surroundings ===
# adjacency_rules = original_adjacency_rules
# run second pass here (optional)

drawWorld.update()
# === Display loop ===
isRunning = True
while isRunning:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                isRunning = False
            if event.key == pygame.K_SPACE:
                if INTERACTIVE and INTERACTIVE_KEYPRESS:
                    world.waveFunctionCollapse()
                    drawWorld.update()

    if INTERACTIVE and not INTERACTIVE_KEYPRESS:
        if not done:
            result = world.waveFunctionCollapse()
            if result == 0:
                done = True
        drawWorld.update()

    drawWorld.draw(displaySurface)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
