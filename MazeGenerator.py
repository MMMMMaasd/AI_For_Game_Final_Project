import numpy as np
import random

def generate_maze_and_path(rows, cols, start_coord=None, end_coord=None):
    """
    Generates a maze using backtracking and returns the grid and the solution path.

    Args:
        rows (int): Number of rows for the maze.
        cols (int): Number of columns for the maze.
        start_coord (tuple, optional): (row, col) for the start. Defaults to bottom-center.
        end_coord (tuple, optional): (row, col) for the end. Defaults to top-center.

    Returns:
        tuple: (maze_grid, solution_path)
               maze_grid (np.array): 0 for path, 1 for wall.
               solution_path (list): List of (row, col) tuples for the solution path.
    """
    maze = np.ones((rows, cols), dtype=int)
    visited = set()
    path = []

    start_row, start_col = start_coord if start_coord else (rows - 1, cols // 2)
    end_row, end_col = end_coord if end_coord else (0, cols // 2)

    start_row = max(0, min(rows - 1, start_row))
    start_col = max(0, min(cols - 1, start_col))
    end_row = max(0, min(rows - 1, end_row))
    end_col = max(0, min(cols - 1, end_col))

    start_pos = (start_row, start_col)
    end_pos = (end_row, end_col)

    print(f"Maze generation: Start={start_pos}, End={end_pos}")

    def is_valid(r, c):
        return 0 <= r < rows and 0 <= c < cols

    def backtrack(r, c):
        """Recursive backtracking function."""
        visited.add((r, c))
        path.append((r, c))
        maze[r, c] = 0 

        if (r, c) == end_pos:
            return True

        neighbors = [(r - 1, c), (r, c + 1), (r + 1, c), (r, c - 1)]
        random.shuffle(neighbors)

        for nr, nc in neighbors:
            if is_valid(nr, nc) and (nr, nc) not in visited:
                open_neighbors = 0
                for nnr, nnc in [(nr - 1, nc), (nr, nc + 1), (nr + 1, nc), (nr, nc - 1)]:
                    if is_valid(nnr, nnc) and maze[nnr, nnc] == 0:
                        open_neighbors += 1

                if backtrack(nr, nc):
                    return True 

        path.pop()
        return False

    if not backtrack(start_row, start_col):
        print("Warning: Maze generation failed to reach the end point directly.")
        pass 

    maze[start_row, start_col] = 0
    maze[end_row, end_col] = 0

    queue = [(start_pos, [start_pos])] 
    visited_bfs = {start_pos}
    final_solution_path = []

    while queue:
        (r, c), current_path = queue.pop(0)

        if (r, c) == end_pos:
            final_solution_path = current_path
            break

        for dr, dc in [( -1, 0), ( 1, 0), ( 0, -1), ( 0, 1)]:
            nr, nc = r + dr, c + dc
            if is_valid(nr, nc) and maze[nr, nc] == 0 and (nr, nc) not in visited_bfs:
                visited_bfs.add((nr, nc))
                new_path = list(current_path)
                new_path.append((nr, nc))
                queue.append(((nr, nc), new_path))

    if not final_solution_path:
        print("Warning: Could not find BFS path from start to end in generated maze.")
        final_solution_path = path

    print(f"Generated maze. Solution path length: {len(final_solution_path)}")
    return maze, final_solution_path

