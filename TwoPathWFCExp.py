import random
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

# Tile types
PATH = "P"
EMPTY = "."

# Grid dimensions
WIDTH = 10
HEIGHT = 10

def initialize_grid():
    return [[set([PATH, EMPTY]) for _ in range(WIDTH)] for _ in range(HEIGHT)]

def collapse_tile(grid, x, y, value):
    grid[y][x] = set([value])
    return propagate_constraints(grid, x, y)

def get_neighbors(x, y):
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    return [(x+dx, y+dy) for dx, dy in directions if 0 <= x+dx < WIDTH and 0 <= y+dy < HEIGHT]

def propagate_constraints(grid, x, y):
    stack = [(x, y)]
    while stack:
        cx, cy = stack.pop()
        tile = grid[cy][cx]
        if len(tile) != 1:
            continue
        value = next(iter(tile))

        for nx, ny in get_neighbors(cx, cy):
            neighbor = grid[ny][nx]
            if len(neighbor) == 1:
                continue

            before = neighbor.copy()

            if value == PATH:
                neighbor.intersection_update([PATH, EMPTY])
            else:
                neighbor.intersection_update([EMPTY])

            if not neighbor:
                raise ValueError("Contradiction detected in propagation.")

            if before != neighbor:
                stack.append((nx, ny))
    return grid

def run_path_wfc():
    grid = initialize_grid()

    start_x = random.randint(0, WIDTH - 1)
    grid = collapse_tile(grid, start_x, HEIGHT - 1, PATH)

    current = (start_x, HEIGHT - 1)
    visited = {current}

    while current[1] > 0:
        x, y = current
        options = [(x+dx, y-1) for dx in [-1, 0, 1] if 0 <= x+dx < WIDTH and y-1 >= 0]
        random.shuffle(options)

        next_cell = None
        for nx, ny in options:
            if (nx, ny) not in visited:
                next_cell = (nx, ny)
                break

        if not next_cell:
            break

        visited.add(next_cell)
        collapse_tile(grid, next_cell[0], next_cell[1], PATH)
        current = next_cell

    return grid

def run_surroundings_wfc(grid):
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if isinstance(grid[y][x], set) and len(grid[y][x]) > 1:
                grid[y][x] = set([random.choice([EMPTY, "#"])])
    return grid

def render_grid(grid):
    for row in grid:
        print("".join(next(iter(cell)) if isinstance(cell, set) else cell for cell in row))

def extract_path_nodes(grid):
    return [(x, y) for y in range(HEIGHT) for x in range(WIDTH)
            if isinstance(grid[y][x], set) and next(iter(grid[y][x])) == PATH]

def build_path_graph(nodes):
    G = nx.Graph()
    for (x, y) in nodes:
        G.add_node((x, y))
        for nx_, ny_ in get_neighbors(x, y):
            if (nx_, ny_) in nodes:
                G.add_edge((x, y), (nx_, ny_))
    return G

def draw_graph(G):
    pos = {node: (node[0], -node[1]) for node in G.nodes()}
    plt.figure(figsize=(6, 6))
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=500)
    plt.title("Path Graph from WFC Maze")
    plt.grid(True)
    plt.show()

# MAIN
grid = run_path_wfc()
grid = run_surroundings_wfc(grid)
render_grid(grid)

# Graph visualization
path_nodes = extract_path_nodes(grid)
path_graph = build_path_graph(path_nodes)
draw_graph(path_graph)
