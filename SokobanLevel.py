import random
import numpy as np
from collections import deque
from SokobanLevelGenerator import *
#from SokobanTester import *
from generator import *
from MapTester import *
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
        self.generate_sokoban_puzzle()

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


    def generate_sokoban_puzzle(self, num_regions=8):
        # Track used areas to prevent overlapping regions
        used_areas = []
        regions_found = 0
        
        def get_random_size_and_boxes():
            rand = random.random()
            if rand <= 0.1:
                size = random.randint(7, 9)
                boxes = random.randint(2, 4)
            elif rand <= 0.3:
                size = random.randint(8, 12)
                boxes = random.randint(3, 5)
            elif rand <= 0.7:
                size = random.randint(9, 13)
                boxes = random.randint(3, 6)
            elif rand <= 0.9:
                size = random.randint(9, 14)
                boxes = random.randint(2, 6)
            elif rand <= 0.96:
                size = random.randint(16, 20)
                boxes = random.randint(5, 10)
            else:
                size = random.randint(9, 16)
                boxes = random.randint(5, 10)
            return max(6, min(size, 20)), boxes
        
        # We'll make multiple passes through the path
        for pass_num in range(3):  # Try up to 3 passes to find regions
            for path_idx in range(1, len(self.path)-1):  # Walk along the path
                if regions_found >= num_regions:
                    break
                
                center_x, center_y = self.path[path_idx]
            
                # Skip if this path tile is too close to existing regions
                too_close = False
                for (sx, sy, ex, ey) in used_areas:
                    if (center_x >= sx-6 and center_x <= ex+6 and
                        center_y >= sy-6 and center_y <= ey+6):
                        too_close = True
                        break
                if too_close:
                    continue
                    
                region_size, box_count = get_random_size_and_boxes()
                # Determine the boundaries of the puzzle area based on available space
                left_space = 0
                right_space = 0
                top_space = 0
                bottom_space = 0
    
                # Find how much space we have in each direction
                # Left
                x, y = center_x, center_y
                while y > 0 and (x, y-1) not in self.path:
                    left_space += 1
                    y -= 1
    
                # Right
                x, y = center_x, center_y
                while y < self.width-1 and (x, y+1) not in self.path:
                    right_space += 1
                    y += 1
    
                # Up
                x, y = center_x, center_y
                while x > 0 and (x-1, y) not in self.path:
                    top_space += 1
                    x -= 1
    
                # Down
                x, y = center_x, center_y
                while x < self.height-1 and (x+1, y) not in self.path:
                    bottom_space += 1
                    x += 1
    
                # Determine puzzle dimensions (minimum 3x3)
                width = max(6, min(region_size, left_space + right_space + 1))
                height = max(6, min(region_size, top_space + bottom_space + 1))
        
                if width < 3 or height < 3:
                    continue  # Not enough space
        
                # Calculate the actual bounds of our puzzle area
                start_y = center_y - min(left_space, width//2)
                start_y = max(0, start_y)
                end_y = start_y + width - 1
                if end_y >= self.width:
                    end_y = self.width - 1
                    start_y = end_y - width + 1
        
                start_x = center_x - min(top_space, height//2)
                start_x = max(0, start_x)
                end_x = start_x + height - 1
                if end_x >= self.height:
                    end_x = self.height - 1
                    start_x = end_x - height + 1
                
                # Check if this region overlaps with any used areas
                overlap = False
                for (sx, sy, ex, ey) in used_areas:
                    if not (end_x < sx or start_x > ex or end_y < sy or start_y > ey):
                        overlap = True
                        break
                if overlap:
                    continue
                
                # Collect all path tiles within this area as boundaries
                print("region detected")
                print(start_x, start_y)
                print(end_x, end_y)

                boundaries = []
                for x in range(start_x, end_x + 1):
                    for y in range(start_y, end_y + 1):
                        if (x, y) in self.path:
                            # Convert to relative coordinates
                            rel_x = x - start_x
                            rel_y = y - start_y
                            boundaries.append((rel_x, rel_y))
            
                # We need at least one boundary tile (the path we're connecting to)
                if not boundaries:
                    continue
        
                # Determine player start position - should be on a boundary tile
                player_pos = None
                candidate_positions = []
                for (rel_x, rel_y) in boundaries:
                    abs_x = start_x + rel_x
                    abs_y = start_y + rel_y
        
                    # Check if this boundary tile has adjacent floor tiles
                    for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                        nx, ny = abs_x + dx, abs_y + dy
                        if (nx >= start_x and nx <= end_x and
                            ny >= start_y and ny <= end_y and
                            (nx, ny) not in self.path):
                            candidate_positions.append((rel_x, rel_y))
                            break
    
                
                if not candidate_positions:
                    continue  # No suitable player position
                
                 # Sort candidates by their distance to center (closest first)
                center_x = (end_x - start_x) // 2
                center_y = (end_y - start_y) // 2
                candidate_positions.sort(
                    key=lambda pos: abs(pos[0]-center_x) + abs(pos[1]-center_y)
                )
    
                # Select from top 25-75% of positions (avoid closest and farthest)
                selection_range = len(candidate_positions) // 2
                start_idx = selection_range // 4
                end_idx = start_idx + selection_range
                player_pos = random.choice(candidate_positions[start_idx:end_idx])
                # Mark this region
                used_areas.append((start_x, start_y, end_x, end_y))
                #sokoban_areas.append((start_x, start_y, end_x, end_y))
                regions_found += 1
            
                # Mark the region in the grid
                for x in range(start_x, end_x + 1):
                    for y in range(start_y, end_y + 1):
                        if (x, y) in self.path:
                            self.grid[x, y] = 9  # Boundary wall
                        else:
                            self.grid[x, y] = 8  # Playable floor
            
                # Mark player position
                px, py = start_x + player_pos[0], start_y + player_pos[1]
                self.grid[px, py] = 10
            
                print(f"Found region {regions_found} at ({start_x},{start_y})-({end_x},{end_y})")
                max_attempts = 5
                for attempt in range(max_attempts):
                    try:
                        # Generate the Sokoban puzzle
                        sokoban_level = SokobanLevel(
                            width=end_y - start_y + 1,
                            height=end_x - start_x + 1,
                            num_boxes=box_count,
                            boundaries=boundaries,
                            start_pos=player_pos
                        )
                        sokoban_level.rip(random.randint(-2, 5))
                        generatePaths(sokoban_level)
                    
                        # Check if level is trash
                        if sokoban_level.trash:
                            print(f"Attempt {attempt+1}: Generated trash level, retrying...")
                            continue
                    
                        # Check minimum dimension requirements
                        if (end_y - start_y + 1) < 6 or (end_x - start_x + 1) < 6:
                            print("Region too small, retrying...")
                            continue
                    
                        # Get the generated grid
                        sokoban_grid = sokoban_level.get_tile_grid()

                        print(sokoban_grid)

                        print(sokoban_level.trash)
                        # Process the generated grid
                        for x in range(sokoban_level.height):
                            for y in range(sokoban_level.width):
                                abs_x = start_x + x
                                abs_y = start_y + y
                                tile = sokoban_grid[x][y]
                        
                                if tile == 1:    # Wall in Sokoban
                                    if (abs_x, abs_y) not in self.path:  # Only mark new walls
                                        self.grid[abs_x][abs_y] = 11
                                elif tile == 0:  # Floor
                                    self.grid[abs_x][abs_y] = 12
                                    print(abs_x, abs_y)
                                elif tile == 4:  # Player
                                    self.grid[abs_x][abs_y] = 5
                                elif tile == 3:  # Box
                                    self.grid[abs_x][abs_y] = 2
                                    self.box_positions.append((abs_x, abs_y))
                                elif tile == 2:   # Hole
                                    self.grid[abs_x][abs_y] = 3
                                    self.hole_positions.append((abs_x, abs_y))
                    
                        regions_found += 1
                        sokoban_areas.append(sokoban_grid)
                        sokoban_starts.append((start_x, start_y))
                        sokoban_ends.append((end_x, end_y))
                        sokoban_players.append(player_pos)
                        print(f"Generated valid region {regions_found} with {box_count} boxes at ({start_x},{start_y})-({end_x},{end_y})")
                        break  # Success - exit retry loop
                    
                    except Exception as e:
                        print(f"Sokoban generation failed: {e}")
                        if attempt == max_attempts - 1:
                            print("Max attempts reached, skipping this region")
                        continue
        
        # Fallback if we didn't find enough regions
        if regions_found < num_regions:
            remaining = num_regions - regions_found
            print(f"Only found {regions_found} regions, adding {remaining} random boxes")

        
        
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
                current_val = self.grid[x, y]
                if current_val in [8, 9, 10, 11, 12, 2, 3, 5]:
                    tile_grid[x, y] = current_val
                    continue
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
