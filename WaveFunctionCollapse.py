import pygame
import sys
from SokobanLevel import *
from ClassWorld import World
from ClassDrawWorld import DrawWorld
from Config import *
from MapTester import *

# === Pygame Constants ===
TILE_SIZE = 32
FPS = 60
LABEL_HEIGHT = 120


# === Colors ===
COLOR_FLOOR = (230, 230, 230)
COLOR_PATH = (255, 255, 150)
COLOR_BOX = (160, 82, 45)
COLOR_HOLE = (138, 43, 226)
COLOR_SOKOBAN_PATH = (255, 200, 200)
COLOR_PLAYER = (50, 200, 50)
COLOR_GRID_LINE = (200, 200, 200)
COLOR_BUTTON = (70, 130, 180)
COLOR_BUTTON_TEXT = (255, 255, 255)

# === Settings ===
INTERACTIVE = True  # ✅ Set False for instant collapse

# === Initialize Pygame ===
pygame.init()
pygame.font.init()
font = pygame.font.SysFont('Arial', 18)

# === Maze Setup ===
maze = MazeGenerator(20, 20, num_boxes=5)
maze.generate()
maze.tile_grid = decorate_maze(maze.tile_grid)
tile_grid = maze.tile_grid

grid_width = maze.width
grid_height = maze.height

# === Set up screen ===
width_px = grid_width * TILE_SIZE
height_px = grid_height * TILE_SIZE + LABEL_HEIGHT
screen = pygame.display.set_mode((width_px, height_px))
pygame.display.set_caption("Maze + WFC Visualizer")
PLAYER_SPRITE_IMG = pygame.image.load("./player_sprite.png").convert_alpha()
HOLE_SPRITE_IMG = pygame.image.load("./hole_grass.png").convert_alpha()
STONE_SPRITE_IMG = pygame.image.load("./boulder_grass.png").convert_alpha()

clock = pygame.time.Clock()

# === Buttons ===
button_maze = pygame.Rect(width_px // 4 - 80, grid_height * TILE_SIZE + 10, 160, 40)
button_wfc = pygame.Rect(3 * width_px // 4 - 80, grid_height * TILE_SIZE + 10, 160, 40)
button_solve = pygame.Rect(width_px // 2 - 80, grid_height * TILE_SIZE + 60, 160, 40)


# === WFC Setup ===
wfc_world = None
wfc_drawer = None
current_mode = "Maze"
wfc_done = False

# === Draw functions ===
def draw_grid():
    for x in range(grid_height):
        for y in range(grid_width):
            rect = pygame.Rect(y * TILE_SIZE, x * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            value = tile_grid[x, y]

            if value == 0:
                pygame.draw.rect(screen, COLOR_FLOOR, rect)
            elif value == 1:
                pygame.draw.rect(screen, COLOR_PATH, rect)
            elif value == 2:
                pygame.draw.rect(screen, COLOR_BOX, rect)
            elif value == 3:
                pygame.draw.rect(screen, COLOR_HOLE, rect)
            elif value == 4:
                pygame.draw.rect(screen, COLOR_SOKOBAN_PATH, rect)
            elif value == 5:
                pygame.draw.rect(screen, COLOR_PLAYER, rect)
            elif value == 6:
                # pygame.draw.rect(screen, (100, 149, 237), rect)  # 🎯 Blue (Cornflower Blue)
                pygame.draw.rect(screen, COLOR_FLOOR, rect)
            elif value == 7:
                # pygame.draw.rect(screen, (220, 20, 60), rect)    # 🎯 Red (Crimson)
                pygame.draw.rect(screen, COLOR_FLOOR, rect)
            elif value == 8:  # Region floor
                pygame.draw.rect(screen, (200, 230, 255), rect)  # Light blue
            elif value == 9:  # Region wall
                pygame.draw.rect(screen, (100, 100, 150), rect)  # Dark blue
            elif value == 10: # Region player start
                pygame.draw.rect(screen, (50, 200, 50), rect)  # Bright green
            elif value == 11:
                pygame.draw.rect(screen, (200, 200, 200), rect)
            elif value == 12:
                pygame.draw.rect(screen, (50, 50, 1), rect)

            pygame.draw.rect(screen, COLOR_GRID_LINE, rect, 1)

def draw_buttons():
    pygame.draw.rect(screen, COLOR_BUTTON, button_maze)
    pygame.draw.rect(screen, COLOR_BUTTON, button_wfc)
    pygame.draw.rect(screen, COLOR_BUTTON, button_solve)

    text_surface1 = font.render("Maze View", True, COLOR_BUTTON_TEXT)
    text_surface2 = font.render("Run WFC", True, COLOR_BUTTON_TEXT)
    text_surface3 = font.render("A* Solve", True, COLOR_BUTTON_TEXT)

    text_rect1 = text_surface1.get_rect(center=button_maze.center)
    text_rect2 = text_surface2.get_rect(center=button_wfc.center)
    text_rect3 = text_surface3.get_rect(center=button_solve.center)

    screen.blit(text_surface1, text_rect1)
    screen.blit(text_surface2, text_rect2)
    screen.blit(text_surface3, text_rect3)

# === Main loop ===
running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if button_maze.collidepoint(event.pos):
                # Regenerate Maze
                sokoban_areas = []
                maze.generate()
                maze.tile_grid = decorate_maze(maze.tile_grid)
                tile_grid = maze.tile_grid

                wfc_world = None
                wfc_drawer = None
                current_mode = "Maze"
                wfc_done = False


            if button_wfc.collidepoint(event.pos):
                # Switch to WFC mode
                wfc_world = World(grid_width, grid_height, maze_tile_grid=tile_grid)
                wfc_drawer = DrawWorld(wfc_world, PLAYER_SPRITE_IMG, HOLE_SPRITE_IMG, STONE_SPRITE_IMG)

                current_mode = "WFC"
                wfc_done = False

                if not INTERACTIVE:
                    while not wfc_done:
                        result = wfc_world.waveFunctionCollapse()
                        if result == 0:
                            wfc_done = True
                    wfc_drawer.update()

            if button_solve.collidepoint(event.pos):
                if current_mode == "WFC" and wfc_done:
                    search_input = []
                    for row in wfc_world.tileRows:
                        row_values = [int(tile.possibilities[0]) for tile in row]
                        search_input.append(row_values)
                    tile_grid_list = tile_grid.tolist()
                    solved_map = solveMap(search_input, tile_grid_list, maze)
                    #draw solution
                    for i, row in enumerate(wfc_world.tileRows):
                        for j, tile in enumerate(row):
                            tile.possibilities = [solved_map[i][j]]
                            tile.entropy = 0
                            tile.collapsed = True
                    wfc_drawer.update()



    # === Update screen ===
    screen.fill(COLOR_FLOOR)

    if current_mode == "Maze":
        draw_grid()
        draw_buttons()

    else:
        draw_buttons()
        for x in range(grid_height):
            for y in range(grid_width):
                if tile_grid[y, x] == 2:  # 2 = box in maze
                    wfc_world.addStoneTile(x, y, TILE_GRASS_STONE)
                if tile_grid[y,x] == 5: # 5 = player
                    wfc_world.addStoneTile(x, y, TILE_PLAYER)
                if tile_grid[y,x] == 3: # 3 = holes
                    wfc_world.addStoneTile(x, y, TILE_GRASS_HOLE)
                if tile_grid[y,x] == 11:
                    wfc_world.addStoneTile(x, y, TILE_SOKO_BLOCKER)
                if tile_grid[y, x] == 12:
                    wfc_world.addStoneTile(x, y, TILE_GRASS)
        if wfc_world and wfc_drawer:
            if INTERACTIVE:
                if not wfc_done:
                    result = wfc_world.waveFunctionCollapse()
                    if result == 0:
                        wfc_done = True
                        print("\tTILES HERE: ")
                        print(tile_grid)
                        search_input = []
                        """for row in wfc_world.tileRows:
                            row_values = [int(tile.possibilities[0]) for tile in row]
                            search_input.append(row_values)
                        solveMap(search_input)"""


                wfc_drawer.update()
            wfc_drawer.draw(screen)
    pygame.display.flip()
pygame.quit()
sys.exit()
