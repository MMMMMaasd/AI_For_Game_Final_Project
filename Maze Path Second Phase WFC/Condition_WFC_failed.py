import pygame
import numpy as np
import tkinter as tk
from ConditionalWorld import ConditionalWorld
from ClassDrawWorld import DrawWorld
from Config import *
from MazeGenerator import generate_maze, upscale_maze

# === Grid & Tile Config ===
BASE_ROWS, BASE_COLS = 10, 10
SCALE = 4
WORLD_X, WORLD_Y = BASE_COLS * SCALE, BASE_ROWS * SCALE
TILESIZE = 1
SCALETILE = 20
BUTTON_HEIGHT = 40
PADDING = 10
BUTTON_WIDTH = 160

# === Get screen size (cross-platform) ===
import tkinter as tk

def get_screen_size():
    root = tk.Tk()
    root.withdraw()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.destroy()
    return width, height

# Real screen size
screen_width, screen_height = get_screen_size()

# Map + buttons size
FULL_WIDTH = WORLD_X * SCALETILE
FULL_HEIGHT = WORLD_Y * SCALETILE + BUTTON_HEIGHT + PADDING * 3

# Try generous padding to account for menu bar, dock, etc.
max_width = screen_width - 200
max_height = screen_height - 200
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 700

# Dynamic display scale
DISPLAY_SCALE = min(WINDOW_WIDTH / FULL_WIDTH, WINDOW_HEIGHT / FULL_HEIGHT)

SCALED_WIDTH = int(FULL_WIDTH * DISPLAY_SCALE)
SCALED_HEIGHT = int(FULL_HEIGHT * DISPLAY_SCALE)
# Fallback if still too large
if DISPLAY_SCALE < 0.3:
    DISPLAY_SCALE = 0.3

""" WINDOW_WIDTH = int(FULL_WIDTH * DISPLAY_SCALE)
WINDOW_HEIGHT = int(FULL_HEIGHT * DISPLAY_SCALE) """

print(f"Screen: {screen_width}x{screen_height}")
print(f"Full surface: {FULL_WIDTH}x{FULL_HEIGHT}")
print(f"Window: {WINDOW_WIDTH}x{WINDOW_HEIGHT} @ scale {DISPLAY_SCALE:.2f}")


# === Pygame init ===
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Maze + WFC")
font = pygame.font.SysFont(None, 24)

# === Maze + WFC generator ===
def generate_wfc_world_from_maze(base_rows=BASE_ROWS, base_cols=BASE_COLS, scale=SCALE):
    maze, solution = generate_maze(base_rows, base_cols)
    while len(solution) == 0:
        maze, solution = generate_maze(base_rows, base_cols)
    upscaled_maze, upscaled_path = upscale_maze(maze, solution, scale)

    world_y, world_x = base_rows * scale, base_cols * scale
    solution_mask = np.zeros((world_y, world_x), dtype=bool)
    for y, x in upscaled_path:
        solution_mask[y][x] = True

    world = ConditionalWorld(world_x, world_y, solution_mask)
    world.solution_path = upscaled_path
    return world

# === Button rendering ===
def draw_buttons_on_surface(surface):
    total_width = 2 * BUTTON_WIDTH + 3 * PADDING
    start_x = (FULL_WIDTH - total_width) // 2
    y_pos = WORLD_Y * SCALETILE + PADDING

    btn_generate = pygame.Rect(start_x, y_pos, BUTTON_WIDTH, BUTTON_HEIGHT)
    btn_wfc = pygame.Rect(start_x + BUTTON_WIDTH + PADDING, y_pos, BUTTON_WIDTH, BUTTON_HEIGHT)

    pygame.draw.rect(surface, (70, 70, 200), btn_generate)
    pygame.draw.rect(surface, (20, 150, 20), btn_wfc)

    txt_generate = font.render("Generate New Maze", True, (255, 255, 255))
    txt_wfc = font.render("WFC Generation", True, (255, 255, 255))
    surface.blit(txt_generate, txt_generate.get_rect(center=btn_generate.center))
    surface.blit(txt_wfc, txt_wfc.get_rect(center=btn_wfc.center))

    return btn_generate, btn_wfc

# === Initial state ===
world = generate_wfc_world_from_maze()
drawWorld = DrawWorld(world)
done = False
running = True
wfc_enabled = False
full_surface = pygame.Surface((FULL_WIDTH, FULL_HEIGHT))

# === Main loop ===
while running:
    full_surface.fill((30, 30, 30))

    if wfc_enabled and not done:
        result = world.waveFunctionCollapse()
        if result == 0:
            done = True

    drawWorld.update(show_solution_path=not wfc_enabled, show_entropy=wfc_enabled)
    drawWorld.draw(full_surface)
    btn_generate, btn_wfc = draw_buttons_on_surface(full_surface)

    scaled_surface = pygame.transform.smoothscale(full_surface, (SCALED_WIDTH, SCALED_HEIGHT))
    x_offset = (WINDOW_WIDTH - SCALED_WIDTH) // 2
    y_offset = (WINDOW_HEIGHT - SCALED_HEIGHT) // 2
    screen.fill((0, 0, 0))  
    screen.blit(scaled_surface, (x_offset, y_offset))
    # screen.blit(scaled_surface, (0, 0))
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            # scaled_pos = (mx / DISPLAY_SCALE, my / DISPLAY_SCALE)
            scaled_pos = ((event.pos[0] - x_offset) / DISPLAY_SCALE, (event.pos[1] - y_offset) / DISPLAY_SCALE)
            if btn_generate.collidepoint(scaled_pos):
                world = generate_wfc_world_from_maze()
                drawWorld = DrawWorld(world)
                done = False
                wfc_enabled = False
                print("New Maze and WFC Input Generated!")
            elif btn_wfc.collidepoint(scaled_pos):
                wfc_enabled = True
                print("WFC Generation Started!")

    clock.tick(60)

pygame.quit()
