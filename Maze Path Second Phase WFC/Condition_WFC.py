import pygame
import numpy as np
import tkinter as tk
from ConditionalWorld import ConditionalWorld
from ClassDrawWorld import DrawWorld
from Config import *
from MazeGenerator import generate_maze, upscale_maze
import sys

# Use Config values for grid size and tile rendering
ROWS = WORLD_Y
COLS = WORLD_X
CELL_SIZE = TILESIZE * SCALETILE
BUTTON_HEIGHT = 40

# Zoom factor (0.5 means 50% scaled down)
DISPLAY_SCALE = 0.5

# Maze generation scale
SCALE = 4
BASE_ROWS = ROWS // SCALE
BASE_COLS = COLS // SCALE

# Colors
COLOR_BG = (30, 30, 30)
COLOR_SOLUTION = (0, 255, 0)
COLOR_BUTTON = (70, 70, 200)
COLOR_BUTTON_ALT = (20, 150, 20)
COLOR_BUTTON_TEXT = (255, 255, 255)
COLOR_BLOCKER = (200, 50, 50) 

START = (0, 0)
END = (BASE_ROWS - 1, BASE_COLS - 1)

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

        txt_maze = font.render("Generate New Maze", True, COLOR_BUTTON_TEXT)
        txt_wfc = font.render("Run WFC", True, COLOR_BUTTON_TEXT)

        screen.blit(txt_maze, txt_maze.get_rect(center=btn_maze.center))
        screen.blit(txt_wfc, txt_wfc.get_rect(center=btn_wfc.center))

        return btn_maze, btn_wfc

    def generate_new_world():
        nonlocal world, drawWorld, wfc_done, wfc_running
        maze, solution = generate_maze(BASE_ROWS, BASE_COLS)
        while len(solution) == 0:
            maze, solution = generate_maze(BASE_ROWS, BASE_COLS)
        upscaled_maze, upscaled_path = upscale_maze(maze, solution, SCALE)
        solution_mask = np.zeros((ROWS, COLS), dtype=bool)
        blocker_mask = np.zeros((ROWS, COLS), dtype=bool)
        for y, x in upscaled_path:
            if 0 <= y < ROWS and 0 <= x < COLS:
                solution_mask[y][x] = True

        for y in range(ROWS):
            for x in range(COLS):
                if upscaled_maze[y][x] == 2:
                    blocker_mask[y][x] = True

        world = ConditionalWorld(COLS, ROWS, solution_mask, blocker_mask)
        world.solution_path = upscaled_path
        world.blocker_mask = blocker_mask
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

        drawWorld.update(show_solution_path=not wfc_running, show_entropy=wfc_running)
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
                    print("Generated new maze.")
                elif btn_wfc.collidepoint(event.pos):
                    wfc_running = True
                    print("Started WFC process.")

        clock.tick(30)

    pygame.quit()
    sys.exit()

visualize_maze_pygame()
