import random
import numpy as np
from collections import deque

class MazeGenerator:
    def __init__(self, width, height, num_boxes=3, min_distance=None):
        self.width = width
        self.height = height
        self.grid = np.zeros((height, width), dtype=int)  # 0 = floor
        self.path = []
        self.start = None
        self.end = None
        self.num_boxes = num_boxes
        self.min_distance = min_distance if min_distance else (width + height) // 2

        self.box_positions = []
        self.hole_positions = []
        self.box_to_hole = {}
        self.box_to_hole_paths = {}
        self.tile_grid = None  # 🎯 final WFC integer grid

    def generate(self, max_distance=8):
        self.grid.fill(0)
        self.path = []
        self.box_positions = []
        self.hole_positions = []
        self.box_to_hole_paths = {}
        self.box_to_hole = {}

        self.start, self.end = self.pick_far_start_end()

        self.generate_maze_only()
        self.place_boxes_only()
        self.place_holes_only(max_distance)
        self.generate_sokoban_paths_only()

        self.tile_grid = self.get_tile_grid_for_wfc()  # 🎯 build integer grid

    def pick_far_start_end(self):
        return (0, 0), (self.height - 1, self.width - 1)


    def generate_maze_only(self):
        visited = set()

        def count_adjacent_path(x, y):
            count = 0
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.height and 0 <= ny < self.width and self.grid[nx, ny] == 1:
                    count += 1
            return count

        def backtrack(x, y):
            visited.add((x, y))
            self.path.append((x, y))
            self.grid[x, y] = 1
            if (x, y) == self.end:
                return True
            dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            random.shuffle(dirs)
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.height and 0 <= ny < self.width and (nx, ny) not in visited:
                    if (nx, ny) == self.end or count_adjacent_path(nx, ny) <= 1:
                        if backtrack(nx, ny):
                            return True
            self.path.pop()
            return False

        backtrack(*self.start)

    def place_boxes_only(self):
        self.box_positions = []

        eligible_path = [p for p in self.path if p != self.start and p != self.end]
        random.shuffle(eligible_path)

        for (x, y) in eligible_path:
            too_close = False

            for bx, by in self.box_positions:
                if abs(bx - x) + abs(by - y) <= 1:
                    too_close = True
                    break
            if abs(self.start[0] - x) + abs(self.start[1] - y) <= 1:
                too_close = True
            if abs(self.end[0] - x) + abs(self.end[1] - y) <= 1:
                too_close = True

            if not too_close:
                self.grid[x, y] = 3  # mark box tile temporarily
                self.box_positions.append((x, y))
                if len(self.box_positions) >= self.num_boxes:
                    break

    def place_holes_only(self, max_distance=8):
        self.hole_positions = []
        self.box_to_hole = {}
        used_holes = set()

        for box in self.box_positions:
            x0, y0 = box

            candidates = []
            for x in range(self.height):
                for y in range(self.width):
                    if self.grid[x, y] == 0 and (x, y) not in used_holes:
                        dx = abs(x - x0)
                        dy = abs(y - y0)
                        manhattan_dist = dx + dy
                        if 5 < manhattan_dist <= max_distance:
                            candidates.append((x, y))

            if not candidates:
                for x in range(self.height):
                    for y in range(self.width):
                        if self.grid[x, y] == 0 and (x, y) not in used_holes:
                            dx = abs(x - x0)
                            dy = abs(y - y0)
                            manhattan_dist = dx + dy
                            if 3 < manhattan_dist <= max_distance:
                                candidates.append((x, y))

            if not candidates:
                raise ValueError(f"No valid hole found for box at {box}!")

            hole = random.choice(candidates)
            self.hole_positions.append(hole)
            self.box_to_hole[box] = hole
            used_holes.add(hole)

    def generate_sokoban_paths_only(self):
        self.box_to_hole_paths = {}

        for box, hole in self.box_to_hole.items():
            x0, y0 = box
            x1, y1 = hole
            path = []

            dx = 1 if x1 > x0 else -1
            for x in range(x0, x1, dx):
                path.append((x, y0))
            path.append((x1, y0))

            dy = 1 if y1 > y0 else -1
            for y in range(y0, y1, dy):
                path.append((x1, y))
            path.append((x1, y1))

            self.box_to_hole_paths[box] = path

    def get_tile_grid_for_wfc(self):
        tile_grid = np.zeros((self.height, self.width), dtype=int)

        for x in range(self.height):
            for y in range(self.width):
                pos = (x, y)

                if pos == self.start:
                    tile_grid[x, y] = 5
                elif pos in self.box_positions:
                    tile_grid[x, y] = 2
                elif pos in self.hole_positions:
                    tile_grid[x, y] = 3
                elif any(pos in path for path in self.box_to_hole_paths.values()):
                    tile_grid[x, y] = 4
                elif pos in self.path:
                    tile_grid[x, y] = 1
                else:
                    tile_grid[x, y] = 0

        return tile_grid

    # Utility
    def get_maze_grid(self):
        return self.grid

    def get_solution_path(self):
        return self.path

    def get_start_end(self):
        return self.start, self.end

    def get_box_and_hole_paths(self):
        return self.box_to_hole_paths

def decorate_maze(tile_grid):
    height, width = tile_grid.shape

    # Step 1: Add 6 around box and hole
    for x in range(height):
        for y in range(width):
            if tile_grid[x, y] == 2 or tile_grid[x, y] == 3:  # box or hole
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < height and 0 <= ny < width:
                            if tile_grid[nx, ny] == 0:
                                tile_grid[nx, ny] = 6

    # Step 2: Add 7 around non-floor tiles
    # We make a copy first to avoid interfering during loop
    updated_grid = tile_grid.copy()

    for x in range(height):
        for y in range(width):
            if tile_grid[x, y] != 0:
                for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < height and 0 <= ny < width:
                        if tile_grid[nx, ny] == 0:
                            updated_grid[nx, ny] = 7

    return updated_grid


maze = MazeGenerator(40, 40, num_boxes=5)
maze.generate()
maze.tile_grid = decorate_maze(maze.tile_grid)
print("Tile Grid (for WFC):")
print(maze.tile_grid)
