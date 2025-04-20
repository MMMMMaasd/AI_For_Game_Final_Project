import pygame
import numpy as np
import tkinter as tk
from ConditionalWorld import ConditionalWorld
from ClassDrawWorld import DrawWorld
from Config import *
import sys
from SokobanIndex import *

# Floor = 0
# Wall = 1
# Target = 2
# Box = 3
# Player = 4
# Use Config values for grid size and tile rendering
ROWS = WORLD_Y
COLS = WORLD_X
CELL_SIZE = TILESIZE * SCALETILE
BUTTON_HEIGHT = 40

# Zoom factor (0.5 means 50% scaled down)
DISPLAY_SCALE = 2

# Maze generation scale
SCALE = 1
BASE_ROWS = ROWS // SCALE
BASE_COLS = COLS // SCALE

# Colors
COLOR_BG = (30, 30, 30)
COLOR_SOLUTION = (0, 255, 0)
COLOR_BUTTON = (70, 70, 200)
COLOR_BUTTON_ALT = (20, 150, 20)
COLOR_BUTTON_TEXT = (255, 255, 255)
COLOR_BLOCKER = (200, 50, 50)
COLOR_WALL = (100, 100, 100)    # Dark gray
COLOR_FLOOR = (200, 200, 180)   # Light beige
COLOR_BOX = (200, 120, 50)      # Orange/brown
COLOR_TARGET = (50, 200, 50)    # Green
COLOR_PLAYER = (50, 50, 200)    # Blue

def visualize_maze_pygame():
    pygame.init()

    # Full resolution
    FULL_WIDTH = COLS * CELL_SIZE
    FULL_HEIGHT = ROWS * CELL_SIZE

    # Scaled down window
    WINDOW_WIDTH = int(FULL_WIDTH * DISPLAY_SCALE)
    WINDOW_HEIGHT = int(FULL_HEIGHT * DISPLAY_SCALE + BUTTON_HEIGHT)

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Maze + WFC (Zoomed Out)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    render_surface = pygame.Surface((FULL_WIDTH, FULL_HEIGHT))

    world = None
    drawWorld = None
    wfc_running = False
    wfc_done = False

    def draw_buttons():
        btn_width = WINDOW_WIDTH // 2
        btn_y = WINDOW_HEIGHT - BUTTON_HEIGHT

        btn_maze = pygame.Rect(0, btn_y, btn_width, BUTTON_HEIGHT)
        btn_wfc = pygame.Rect(btn_width, btn_y, btn_width, BUTTON_HEIGHT)

        pygame.draw.rect(screen, COLOR_BUTTON, btn_maze)
        pygame.draw.rect(screen, COLOR_BUTTON_ALT, btn_wfc)

        txt_maze = font.render("Generate New Puzzle", True, COLOR_BUTTON_TEXT)
        txt_wfc = font.render("Run WFC", True, COLOR_BUTTON_TEXT)

        screen.blit(txt_maze, txt_maze.get_rect(center=btn_maze.center))
        screen.blit(txt_wfc, txt_wfc.get_rect(center=btn_wfc.center))

        return btn_maze, btn_wfc

    def generate_new_world():
        nonlocal world, drawWorld, wfc_done, wfc_running
        
        if_crash, maze = newLevel(10, 10, 5)
        while if_crash:
            if_crash, maze = newLevel(10, 10, 5)
        upscaled_maze = upscale_maze(maze, SCALE)
        
        wall_mask = np.zeros((ROWS, COLS), dtype=bool)
        floor_mask = np.zeros((ROWS, COLS), dtype=bool)
        box_mask = np.zeros((ROWS, COLS), dtype=bool)
        target_mask = np.zeros((ROWS, COLS), dtype=bool)
        player_mask = np.zeros((ROWS, COLS), dtype=bool)

        for y in range(ROWS):
            for x in range(COLS):
                if upscaled_maze[y][x] == 0:
                    floor_mask[y][x] = True
                elif upscaled_maze[y][x] == 1:
                    wall_mask[y][x] = True
                elif upscaled_maze[y][x] == 2:
                    target_mask[y][x] = True
                elif upscaled_maze[y][x] == 3:
                    box_mask[y][x] = True
                elif upscaled_maze[y][x] == 4:
                    player_mask[y][x] = True

        world = ConditionalWorld(COLS, ROWS, floor_mask, wall_mask, target_mask, box_mask, player_mask)
        world.wall_mask = wall_mask
        world.floor_mask = floor_mask
        world.target_mask = target_mask
        world.box_mask = box_mask
        world.player_mask = player_mask
        drawWorld = DrawWorld(world)
        wfc_done = False
        wfc_running = False

    # Initialize world
    generate_new_world()

    running = True
    while running:
        render_surface.fill(COLOR_BG)

        if wfc_running and not wfc_done:
            result = world.waveFunctionCollapse()
            if result == 0:
                wfc_done = True

        drawWorld.update(show_entropy=wfc_running)
        drawWorld.draw(render_surface)

        # Scale full render to fit screen
        scaled_surface = pygame.transform.smoothscale(render_surface, (WINDOW_WIDTH, WINDOW_HEIGHT - BUTTON_HEIGHT))
        screen.blit(scaled_surface, (0, 0))

        btn_maze, btn_wfc = draw_buttons()
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if btn_maze.collidepoint(event.pos):
                    generate_new_world()
                    print("Generated New Sokoban Puzzle.")
                elif btn_wfc.collidepoint(event.pos):
                    wfc_running = True
                    print("Started WFC process.")

        clock.tick(30)

    pygame.quit()
    sys.exit()

visualize_maze_pygame()
