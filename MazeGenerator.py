# MazeGenerator.py

import numpy as np
import random
from collections import deque

def generate_maze_and_path(rows, cols, start_coord=None, end_coord=None):
    """
    Generates a maze using backtracking and returns:
      - maze:           binary grid (0=path, 1=wall)
      - solution_path:  list of (r,c) from start → end
      - tag_grid:       int8 grid with:
                         0 = generic walkable
                         1 = wall
                         2 = carved solution path
                         5 = start tile
                         6 = end tile

    Args:
        rows (int): Number of rows.
        cols (int): Number of columns.
        start_coord (tuple, optional): (r,c) for start; defaults to bottom-center.
        end_coord   (tuple, optional): (r,c) for end;   defaults to top-center.
    """
    # 1) Initialize all walls
    maze = np.ones((rows, cols), dtype=int)
    visited = set()
    backtrack_path = []

    # 2) Determine start/end, clamp
    sr, sc = start_coord or (rows-1, cols//2)
    er, ec = end_coord   or (0,      cols//2)
    sr = max(0, min(rows-1, sr))
    sc = max(0, min(cols-1, sc))
    er = max(0, min(rows-1, er))
    ec = max(0, min(cols-1, ec))
    start_pos = (sr, sc)
    end_pos   = (er, ec)
    print(f"Maze generation: Start={start_pos}, End={end_pos}")

    def valid(r, c):
        return 0 <= r < rows and 0 <= c < cols

    # 3) Recursive backtracker carving
    def carve(r, c):
        visited.add((r, c))
        backtrack_path.append((r, c))
        maze[r, c] = 0
        if (r, c) == end_pos:
            return True

        nbrs = [(r-1,c),(r,c+1),(r+1,c),(r,c-1)]
        random.shuffle(nbrs)
        for nr, nc in nbrs:
            if valid(nr, nc) and (nr, nc) not in visited:
                # avoid opening too many adjacent corridors
                count = 0
                for ar, ac in [(nr-1,nc),(nr,nc+1),(nr+1,nc),(nr,nc-1)]:
                    if valid(ar, ac) and maze[ar, ac] == 0:
                        count += 1
                if count <= 1 and carve(nr, nc):
                    return True

        backtrack_path.pop()
        return False

    if not carve(sr, sc):
        print("Warning: carve did not reach end directly.")

    # ensure endpoints are open
    maze[sr, sc] = 0
    maze[er, ec] = 0

    # 4) BFS to get actual shortest solution path
    queue = deque([(start_pos, [start_pos])])
    seen = {start_pos}
    solution_path = []
    while queue:
        (r, c), path = queue.popleft()
        if (r, c) == end_pos:
            solution_path = path
            break
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r+dr, c+dc
            if valid(nr, nc) and maze[nr, nc] == 0 and (nr, nc) not in seen:
                seen.add((nr, nc))
                queue.append(((nr, nc), path + [(nr, nc)]))

    if not solution_path:
        print("Warning: BFS failed; using backtrack path.")
        solution_path = backtrack_path

    print(f"Generated maze. Solution path length: {len(solution_path)}")

    # 5) Build tag_grid
    tag_grid = np.ones((rows, cols), dtype=np.int8)

    # mark open ground
    tag_grid[maze == 0] = 0
    # mark solution path
    for (r, c) in solution_path:
        tag_grid[r, c] = 2
    # mark start/end
    tag_grid[sr, sc] = 5
    tag_grid[er, ec] = 6

    return maze, solution_path, tag_grid
