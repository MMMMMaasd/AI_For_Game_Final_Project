import numpy as np
import pygame
import random
import sys

# Maze size
BASE_ROWS, BASE_COLS = 10, 10
SCALE = 4
ROWS, COLS = BASE_ROWS * SCALE, BASE_COLS * SCALE
CELL_SIZE = 20
BUTTON_HEIGHT = 40

# Colors
COLOR_BG = (30, 30, 30)
COLOR_SOLUTION = (0, 255, 0)
COLOR_BUTTON = (70, 70, 200)
COLOR_BUTTON_TEXT = (255, 255, 255)
COLOR_BLOCKER = (200, 50, 50) 

# Start and end points in base grid
START = (0, 0)
END = (BASE_ROWS - 1, BASE_COLS - 1)

def generate_maze(rows, cols):
    maze = np.zeros((rows, cols), dtype=int)
    visited = set()
    path = []

    def count_adjacent_path(x, y):
        count = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and maze[nx][ny] == 1:
                count += 1
        return count

    def backtrack(x, y):
        visited.add((x, y))
        path.append((x, y))
        maze[x, y] = 1

        if (x, y) == END:
            return True

        dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        random.shuffle(dirs)

        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and (nx, ny) not in visited:
                if (nx, ny) == END or count_adjacent_path(nx, ny) <= 1:
                    if backtrack(nx, ny):
                        return True

        path.pop()
        return False

    # Generate the maze
    backtrack(*START)

    # === Deterministic blocker placement ===
    for x in range(rows):
        for y in range(cols):
            if maze[x][y] == 0:  # background
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < rows and 0 <= ny < cols and maze[nx][ny] == 1:
                        maze[x][y] = 2  # convert to blocker
                        break  # no need to check more neighbors

    return maze, path

def upscale_maze(maze, path, scale):
    rows, cols = maze.shape
    new_rows, new_cols = rows * scale, cols * scale
    upscaled = np.zeros((new_rows, new_cols), dtype=int)
    new_path = []

    for r in range(rows):
        for c in range(cols):
            value = maze[r, c]
            for i in range(scale):
                for j in range(scale):
                    upscaled[r * scale + i, c * scale + j] = value

    for r, c in path:
        for i in range(scale):
            for j in range(scale):
                new_path.append((r * scale + i, c * scale + j))

    return upscaled, new_path

def visualize_maze_pygame():
    pygame.init()
    screen = pygame.display.set_mode((COLS * CELL_SIZE, ROWS * CELL_SIZE + BUTTON_HEIGHT))
    pygame.display.set_caption("Maze with Backtracking Path")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    def draw_button():
        button_rect = pygame.Rect(0, ROWS * CELL_SIZE, COLS * CELL_SIZE, BUTTON_HEIGHT)
        pygame.draw.rect(screen, COLOR_BUTTON, button_rect)
        text_surface = font.render("Generate New Maze", True, COLOR_BUTTON_TEXT)
        text_rect = text_surface.get_rect(center=button_rect.center)
        screen.blit(text_surface, text_rect)
        return button_rect

    def generate_valid_maze():
        maze, solution = generate_maze(BASE_ROWS, BASE_COLS)
        while len(solution) == 0:
            maze, solution = generate_maze(BASE_ROWS, BASE_COLS)
        maze, solution = upscale_maze(maze, solution, SCALE)
        return maze, solution

    maze, solution = generate_valid_maze()

    running = True
    while running:
        screen.fill(COLOR_BG)

        for row in range(ROWS):
            for col in range(COLS):
                rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if maze[row][col] == 1:
                    pygame.draw.rect(screen, COLOR_SOLUTION, rect)
                elif maze[row][col] == 2:
                    pygame.draw.rect(screen, COLOR_BLOCKER, rect)

        button_rect = draw_button()
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and button_rect.collidepoint(event.pos):
                maze, solution = generate_valid_maze()
                print("New Maze Generated!")
                print("Solution found! Steps:", len(solution))
                print("Maze matrix:\n", maze)
                print("Path:", solution)

        clock.tick(30)

    pygame.quit()
    sys.exit()

# Run everything
# visualize_maze_pygame()