import numpy as np
from collections import deque
import generator
from SokobanLevel import SokobanLevel
import Config
from polygon_tools import marching_squares, flood_fill_polygon

# ------------------------------------------------------------------------
# Phase 2 agent: takes a carved forest world + tag_grid + solution_path,
# finds chokepoints, extracts polygonal side‐path regions, injects
# Sokoban puzzles via generator.py, does a local WFC pass in each region.
# ------------------------------------------------------------------------

# Constraints for deciding when a region is worth a puzzle
MIN_REGION_CELLS = 3
MAX_REGION_CELLS = 25  # Increased to allow for larger puzzle regions
MIN_BOXES        = 1
MAX_BOXES        = 3   # Increased to 3 but will be reduced for small regions

# ------------------------------------------------------------------------
# Simple Sokoban solver for post-generation verification
# ------------------------------------------------------------------------
def verify_sokoban_solvable(grid):
    """
    Verify that a Sokoban puzzle is solvable using BFS.
    Limited to simple puzzles to avoid excessive processing time.
    
    Args:
        grid: Grid representation where 0=floor, 1=wall, 2=hole, 3=box, 4=player
    
    Returns:
        bool: True if solvable, False if unsolvable or too complex
    """
    rows, cols = grid.shape
    
    # Find player, boxes, and holes
    player_pos = None
    boxes = []
    holes = []
    
    for r in range(rows):
        for c in range(cols):
            if grid[r, c] == 4:  # Player
                player_pos = (r, c)
            elif grid[r, c] == 3:  # Box
                boxes.append((r, c))
            elif grid[r, c] == 2:  # Hole
                holes.append((r, c))
    
    # Basic deadlock detection - check for boxes in corners
    for r, c in boxes:
        walls = 0
        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            nr, nc = r + dr, c + dc
            if nr < 0 or nr >= rows or nc < 0 or nc >= cols or grid[nr, nc] == 1:
                walls += 1
        
        # Box is in corner or against 3+ walls (unmovable)
        if walls >= 2:
            adjacent_walls = []
            if r > 0 and grid[r-1, c] == 1: adjacent_walls.append("up")
            if r < rows-1 and grid[r+1, c] == 1: adjacent_walls.append("down")
            if c > 0 and grid[r, c-1] == 1: adjacent_walls.append("left")
            if c < cols-1 and grid[r, c+1] == 1: adjacent_walls.append("right")
            
            # Check for corner configurations that create deadlocks
            if ("up" in adjacent_walls and "left" in adjacent_walls) or \
               ("up" in adjacent_walls and "right" in adjacent_walls) or \
               ("down" in adjacent_walls and "left" in adjacent_walls) or \
               ("down" in adjacent_walls and "right" in adjacent_walls):
                return False  # Box is in an unsolvable corner
    
    # For complex puzzles (3+ boxes), do a simple reachability check 
    # rather than a full solve which could be too expensive
    if len(boxes) >= 3:
        # Check if all holes are reachable from boxes
        for hole in holes:
            reachable = False
            for box in boxes:
                if abs(box[0] - hole[0]) + abs(box[1] - hole[1]) <= 5:
                    reachable = True
                    break
            
            if not reachable:
                return False  # Hole is too far from any box
    
    # For simple puzzles (1-2 boxes), do a limited BFS search
    elif len(boxes) > 0:
        # Only attempt to solve very simple puzzles
        max_steps = 300  # Limit search depth
        
        # State = (player_pos, frozen_boxes)
        initial_state = (player_pos, frozenset(boxes))
        visited = {initial_state}
        queue = deque([(initial_state, 0)])  # (state, steps)
        
        while queue:
            ((pr, pc), current_boxes), steps = queue.popleft()
            
            # Check if solved (all boxes on holes)
            if all(box in holes for box in current_boxes):
                return True
                
            # Limit search depth
            if steps >= max_steps:
                break
                
            # Try each direction
            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                nr, nc = pr + dr, pc + dc
                
                # Check if move is valid
                if not (0 <= nr < rows and 0 <= nc < cols) or grid[nr, nc] == 1:
                    continue  # Hit wall or out of bounds
                    
                if (nr, nc) in current_boxes:
                    # Try to push box
                    box_r, box_c = nr + dr, nc + dc
                    if not (0 <= box_r < rows and 0 <= box_c < cols) or \
                       grid[box_r, box_c] == 1 or \
                       (box_r, box_c) in current_boxes:
                        continue  # Can't push box
                        
                    # Move is valid - push box
                    new_boxes = set(current_boxes)
                    new_boxes.remove((nr, nc))
                    new_boxes.add((box_r, box_c))
                    new_state = ((nr, nc), frozenset(new_boxes))
                    
                    if new_state not in visited:
                        visited.add(new_state)
                        queue.append((new_state, steps + 1))
                else:
                    # Just move player
                    new_state = ((nr, nc), frozenset(current_boxes))
                    if new_state not in visited:
                        visited.add(new_state)
                        queue.append((new_state, steps + 1))
        
        # If we've exhausted the queue without finding a solution,
        # the puzzle is either unsolvable or too complex
        return False
    
    # If we reach here, the puzzle passed basic checks
    return True

# ------------------------------------------------------------------------
# Find points on the yellow path for puzzle placement
# ------------------------------------------------------------------------
def find_path_blockers(tag_grid, solution_path):
    """Find strategic locations directly on the yellow path for puzzles"""
    path_blockers = []
    rows, cols = tag_grid.shape
    
    # Convert solution_path to a set of tuples for faster lookup
    solution_set = set(tuple(pos) for pos in solution_path)
    
    # Find points directly on the yellow path (tag=2)
    for r in range(rows):
        for c in range(cols):
            if tag_grid[r, c] == 2:  # Yellow path
                # Check if there's enough open space for a puzzle
                open_neighbors = sum(1 for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)] 
                                  if 0 <= r+dr < rows and 0 <= c+dc < cols
                                  and tag_grid[r+dr, c+dc] != 1)
                
                # Good spots have multiple open directions
                if open_neighbors >= 2:
                    # Higher priority for spots on both paths
                    is_on_solution = (r, c) in solution_set
                    score = 70 if is_on_solution else 25  # Bigger gap in priority
                    path_blockers.append(((r, c), score))
    
    return path_blockers

# ------------------------------------------------------------------------
# Find strategic points near solution path
# ------------------------------------------------------------------------
def find_strategic_blockers(tag_grid, solution_path, max_distance=3):
    """Find points near solution path that could be blocked by puzzles"""
    rows, cols = tag_grid.shape
    solution_set = set(tuple(pos) for pos in solution_path)
    blockers = []
    
    # Check areas adjacent to solution path
    for r, c in solution_path:
        # Look for open areas near this path point
        for dist in range(1, max_distance+1):
            for dr, dc in [(dist,0), (-dist,0), (0,dist), (0,-dist)]:
                nr, nc = r + dr, c + dc
                
                if not (0 <= nr < rows and 0 <= nc < cols) or tag_grid[nr, nc] == 1:
                    continue
                    
                if tag_grid[nr, nc] == 0 and (nr, nc) not in solution_set:
                    # Count open neighbors
                    open_count = sum(1 for dr2, dc2 in [(-1,0),(1,0),(0,-1),(0,1)] 
                                    if 0 <= nr+dr2 < rows and 0 <= nc+dc2 < cols
                                    and tag_grid[nr+dr2, nc+dc2] != 1)
                    
                    if open_count >= 2:
                        # Score based on strategic value
                        score = open_count
                        if dist == 1 and (r, c) == solution_path[-1]:  # Near end
                            score += 10
                        if dist == 1 and (r, c) == solution_path[0]:   # Near start
                            score += 5
                        blockers.append(((nr, nc), score))
    
    # Sort by score (highest first)
    blockers.sort(key=lambda x: x[1], reverse=True)
    return blockers

# ------------------------------------------------------------------------
# Find open region around a seed point
# ------------------------------------------------------------------------
def find_open_region(tag_grid, seed, max_size=25):
    """Find a connected region of open cells around seed point"""
    rows, cols = tag_grid.shape
    visited = set()
    region = []
    queue = deque([seed])
    
    # Count cells with multiple open neighbors
    open_cells = 0
    path_cells = 0
    
    while queue and len(region) < max_size:
        r, c = queue.popleft()
        
        if (r, c) in visited:
            continue
            
        visited.add((r, c))
        
        # Only include non-wall cells
        if tag_grid[r, c] != 1:
            region.append((r, c))
            
            # Count open neighbors
            open_neighbors = 0
            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                nr, nc = r + dr, c + dc
                if (0 <= nr < rows and 0 <= nc < cols and 
                    tag_grid[nr, nc] != 1):
                    open_neighbors += 1
            
            # If cell has 3+ open neighbors, it's good for puzzles
            if open_neighbors >= 3:
                open_cells += 1

            # Bonus for path cells - they're strategic
            if tag_grid[r, c] == 2:
                open_cells += 2  # Double bonus for yellow path
                path_cells += 1
            
            # Add neighbors to queue - prioritize path cells
            path_neighbors = []
            other_neighbors = []
            
            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                nr, nc = r + dr, c + dc
                if (0 <= nr < rows and 0 <= nc < cols and 
                    (nr, nc) not in visited and 
                    tag_grid[nr, nc] != 1):
                    if tag_grid[nr, nc] == 2:  # Path cell
                        path_neighbors.append((nr, nc))
                    else:
                        other_neighbors.append((nr, nc))
            
            # Add path neighbors first
            for neighbor in path_neighbors:
                queue.appendleft(neighbor)  # Use appendleft to prioritize
            
            # Then add other neighbors
            for neighbor in other_neighbors:
                queue.append(neighbor)
    
    # Return region and a "quality" score based on open cells and path cells
    quality = open_cells + (path_cells * 2)  # Bonus for path inclusion
    return region, quality

# ------------------------------------------------------------------------
# Chokepoints detection
# ------------------------------------------------------------------------
def detect_chokepoints(tag_grid: np.ndarray, solution_path):
    rows, cols = tag_grid.shape
    start = tuple(solution_path[0])
    end = tuple(solution_path[-1])
    chokepoints = set()

    seen = {(start[0], start[1], 0)}
    q = deque([(start[0], start[1], 0)])
    dirs = [(-1,0), (1,0), (0,-1), (0,1)]

    while q:
        r, c, hits = q.popleft()
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if not (0 <= nr < rows and 0 <= nc < cols): 
                continue
            if tag_grid[nr, nc] == 1:  # wall
                continue
            new_hits = hits + (1 if tag_grid[nr, nc] == 2 else 0)
            if new_hits > 1:
                continue
            state = (nr, nc, new_hits)
            if state in seen:
                continue
            seen.add(state)
            q.append(state)
            if (nr, nc) not in (start, end) and tag_grid[nr, nc] == 2:
                chokepoints.add((nr, nc))

    print(f"  → {len(chokepoints)} chokepoints found.")
    return list(chokepoints)

# ------------------------------------------------------------------------
# Find critical chokepoints that must be blocked
# ------------------------------------------------------------------------
def find_critical_chokepoints(tag_grid, start_pos, end_pos):
    """Find points that all paths must pass through to reach the end"""
    rows, cols = tag_grid.shape
    
    # Create walkable grid (0=walkable, 1=blocked)
    walkable = np.zeros_like(tag_grid)
    for r in range(rows):
        for c in range(cols):
            # Walls and boulders are not walkable
            if tag_grid[r, c] in (1, 3):
                walkable[r, c] = 1
    
    # Run BFS from start to identify all reachable cells
    reachable = np.zeros_like(tag_grid)
    queue = deque([start_pos])
    reachable[start_pos[0], start_pos[1]] = 1
    
    while queue:
        r, c = queue.popleft()
        for dr, dc in [(0,1), (1,0), (0,-1), (-1,0)]:
            nr, nc = r + dr, c + dc
            if (0 <= nr < rows and 0 <= nc < cols and 
                walkable[nr, nc] == 0 and 
                reachable[nr, nc] == 0):
                reachable[nr, nc] = 1
                queue.append((nr, nc))
    
    # If end isn't reachable, no path exists
    if reachable[end_pos[0], end_pos[1]] == 0:
        return []
    
    # For each potential blocker, check if removing it disconnects end from start
    chokepoints = []
    
    # Only consider cells that are regular walkable tiles (tag 0)
    for r in range(rows):
        for c in range(cols):
            # Skip non-walkable cells, start/end, and any tiles that aren't plain walkable (tag 0)
            if (walkable[r, c] == 1 or 
                (r, c) == start_pos or 
                (r, c) == end_pos or 
                tag_grid[r, c] != 0):  # ONLY consider regular walkable tiles
                continue
            
            # Create a temporary grid with this cell blocked
            temp_grid = walkable.copy()
            temp_grid[r, c] = 1
            
            # Run BFS to check if end is still reachable
            temp_reachable = np.zeros_like(tag_grid)
            queue = deque([start_pos])
            temp_reachable[start_pos[0], start_pos[1]] = 1
            
            while queue:
                tr, tc = queue.popleft()
                for dr, dc in [(0,1), (1,0), (0,-1), (-1,0)]:
                    nr, nc = tr + dr, tc + dc
                    if (0 <= nr < rows and 0 <= nc < cols and 
                        temp_grid[nr, nc] == 0 and 
                        temp_reachable[nr, nc] == 0):
                        temp_reachable[nr, nc] = 1
                        queue.append((nr, nc))
            
            # If end is no longer reachable, this is a critical chokepoint
            if temp_reachable[end_pos[0], end_pos[1]] == 0:
                # Calculate strategic value
                path_distance = min(
                    abs(r - pos[0]) + abs(c - pos[1]) 
                    for pos in [(start_pos[0], start_pos[1]), (end_pos[0], end_pos[1])]
                )
                score = 1000 - path_distance  # Higher score = closer to start/end
                chokepoints.append(((r, c), score))
    
    # Sort by score
    chokepoints.sort(key=lambda x: x[1], reverse=True)
    return chokepoints

# ------------------------------------------------------------------------
# Enhanced path detection using flood fill algorithm - IMPROVED VERSION
# ------------------------------------------------------------------------
def find_bypass_areas(tag_grid, solution_path, start_pos, end_pos):
    """Use flood fill to identify areas that bypass Sokoban puzzles"""
    rows, cols = tag_grid.shape
    
    # Create a reachability grid
    reachable = np.zeros_like(tag_grid)
    
    # Use a queue for proper breadth-first flood fill
    queue = deque([start_pos])
    reachable[start_pos[0], start_pos[1]] = 1  # Mark start as reachable
    
    while queue:
        r, c = queue.popleft()
        
        # Try all four directions
        for dr, dc in [(0,1), (1,0), (0,-1), (-1,0)]:
            nr, nc = r + dr, c + dc
            
            # Skip if out of bounds
            if not (0 <= nr < rows and 0 <= nc < cols):
                continue
                
            # Skip if already filled
            if reachable[nr, nc] == 1:
                continue
                
            # Skip walls and boulders (these are solid obstacles)
            # Note: Holes (4) are walkable, so we don't block on them
            if tag_grid[nr, nc] in (1, 3):
                continue
            
            # Mark as reachable and add to queue
            reachable[nr, nc] = 1
            queue.append((nr, nc))
    
    # Check if end is reachable
    end_reachable = reachable[end_pos[0], end_pos[1]] == 1
    
    # Find potential blocking points
    blocking_points = []
    if end_reachable:
        for r in range(rows):
            for c in range(cols):
                # Only consider reachable regular walkable tiles (not holes, boulders, or special tiles)
                if (reachable[r, c] == 1 and 
                    tag_grid[r, c] == 0):  # ONLY regular walkable tiles (tag 0)
                    
                    # Count connections to identify chokepoints
                    connections = 0
                    for dr, dc in [(0,1), (1,0), (0,-1), (-1,0)]:
                        nr, nc = r + dr, c + dc
                        if (0 <= nr < rows and 0 <= nc < cols and 
                            reachable[nr, nc] == 1):
                            connections += 1
                    
                    # Higher connections = better blocking point
                    if connections >= 2:
                        # Calculate distance to path (lower = better)
                        path_distance = min(
                            abs(r - pos[0]) + abs(c - pos[1]) 
                            for pos in solution_path
                        )
                        
                        # Score = connections + closeness to path
                        score = connections + (10 / (path_distance + 1))
                        blocking_points.append(((r, c), score))
    
    # Sort by score (highest first)
    blocking_points.sort(key=lambda x: x[1], reverse=True)
    
    return end_reachable, blocking_points, reachable

# ------------------------------------------------------------------------
# Check if a blocking point would affect Sokoban solvability - SIMPLIFIED
# ------------------------------------------------------------------------
def check_block_safety(tag_grid, point):
    """Verify that placing a blocker won't affect Sokoban puzzle solvability"""
    rows, cols = tag_grid.shape
    r, c = point
    
    # ONLY allow placing blockers on regular walkable tiles (tag 0)
    # Explicitly exclude holes (tag 4), boulders (tag 3), start/end (tag 5/6), walls (tag 1)
    if tag_grid[r, c] != 0:
        return False
        
    # Only check immediately adjacent cells for box pushing issues
    for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols:
            # Don't place blockers immediately adjacent to boulders
            if tag_grid[nr, nc] == 3:
                return False
    
    return True

# ------------------------------------------------------------------------
# Enhanced path blocker placement with critical point analysis and no limit
# ------------------------------------------------------------------------
def place_path_blockers(world, tag_grid, solution_path):
    """Place blockers to force players to solve Sokoban puzzles"""
    rows, cols = tag_grid.shape
    
    # Find start and end positions
    start_pos = end_pos = None
    for r in range(rows):
        for c in range(cols):
            if tag_grid[r, c] == 5:  # Start
                start_pos = (r, c)
            elif tag_grid[r, c] == 6:  # End
                end_pos = (r, c)
    
    if not start_pos or not end_pos:
        print("  Cannot place blockers: start or end position not found")
        return tag_grid, world
    
    # First check if any critical chokepoints exist
    print("Finding critical chokepoints...")
    critical_points = find_critical_chokepoints(tag_grid, start_pos, end_pos)
    
    if critical_points:
        print(f"  Found {len(critical_points)} critical chokepoints")
        selected_point, score = critical_points[0]
        
        # Verify that blocking is safe for Sokoban puzzles
        if check_block_safety(tag_grid, selected_point):
            print(f"Placing critical blocker at {selected_point} (score: {score})")
            r, c = selected_point
            
            # Update tag grid
            tag_grid[r, c] = 1  # Mark as wall
            
            # Update world
            BLOCKER_TILE_ID = getattr(Config, 'BUSH_TILE_ID', 5)
            if 0 <= c < world.tile_map.shape[1] and 0 <= r < world.tile_map.shape[0]:
                world.tile_map[r, c] = BLOCKER_TILE_ID
                cell = world.get_tile(c, r)
                if cell:
                    cell.possibilities = [BLOCKER_TILE_ID]
                    cell.entropy = 0
            
            # Verify all paths are blocked
            end_reachable, _, _ = find_bypass_areas(tag_grid, solution_path, start_pos, end_pos)
            if not end_reachable:
                print("  Success! All paths blocked with a single critical blocker")
                return tag_grid, world
    
    # If no critical points or they weren't sufficient, use flood fill approach
    print("Using flood fill to detect bypass areas...")
    end_reachable, blocking_points, reachable = find_bypass_areas(tag_grid, solution_path, start_pos, end_pos)
    
    if not end_reachable:
        print("  End is not reachable without solving puzzles - no blockers needed")
        return tag_grid, world
        
    print(f"  Found {len(blocking_points)} potential blocking points")
    
    # Place blockers with a more thorough approach - no maximum limit
    blockers_placed = 0
    BLOCKER_TILE_ID = getattr(Config, 'BUSH_TILE_ID', 5)
    
    # Try more points with a blocking simulation first
    print("  Simulating block effects to find optimal points...")
    simulation_results = []
    
    for i, ((r, c), score) in enumerate(blocking_points[:200]):  # Test up to 200 points
        if not check_block_safety(tag_grid, (r, c)):
            continue
            
        # Create a temporary grid with this point blocked
        temp_grid = tag_grid.copy()
        temp_grid[r, c] = 1
        
        # Check if this blocks all paths
        still_reachable, _, new_reachable = find_bypass_areas(temp_grid, solution_path, start_pos, end_pos)
        
        # Calculate effectiveness
        if not still_reachable:
            # This point blocks all paths!
            effectiveness = 1.0
        else:
            # Calculate percentage of reachable area reduced
            original_cells = np.sum(reachable)
            remaining_cells = np.sum(new_reachable)
            effectiveness = 1.0 - (remaining_cells / original_cells)
        
        # Create enhanced score based on effectiveness
        enhanced_score = score * (1.0 + effectiveness * 10)
        simulation_results.append(((r, c), enhanced_score, effectiveness))
    
    # Sort by enhanced score
    simulation_results.sort(key=lambda x: x[1], reverse=True)
    
    # Actual blocking phase
    blocking_attempts = 0
    max_attempts = 500  # Very high to ensure we try enough combinations
    
    while end_reachable and blocking_attempts < max_attempts:
        blocking_attempts += 1
        
        if not simulation_results:
            print("  No more viable blocking points available")
            break
        
        (r, c), enhanced_score, effectiveness = simulation_results.pop(0)
        
        # Skip if already blocked
        if tag_grid[r, c] == 1:
            continue
        
        # Place the blocker
        print(f"Placing blocker at {(r, c)} (score: {enhanced_score:.2f}, effectiveness: {effectiveness:.2f})")
        tag_grid[r, c] = 1  # Mark as wall
        
        # Update world tile
        if 0 <= c < world.tile_map.shape[1] and 0 <= r < world.tile_map.shape[0]:
            world.tile_map[r, c] = BLOCKER_TILE_ID
            cell = world.get_tile(c, r)
            if cell:
                cell.possibilities = [BLOCKER_TILE_ID]
                cell.entropy = 0
        
        blockers_placed += 1
        
        # Check if we've successfully blocked all paths
        end_reachable, new_points, new_reachable = find_bypass_areas(tag_grid, solution_path, start_pos, end_pos)
        
        if not end_reachable:
            print(f"  Successfully blocked all bypass paths with {blockers_placed} blockers")
            break
        
        # If still reachable, update our simulation with fresh data
        if blockers_placed % 3 == 0:  # Re-analyze every 3 blockers
            print("  Re-analyzing remaining points...")
            simulation_results = []
            
            for i, ((r, c), _) in enumerate(new_points[:100]):  # Test top 100 points
                if tag_grid[r, c] == 1 or not check_block_safety(tag_grid, (r, c)):
                    continue
                
                # Create a temporary grid with this point blocked
                temp_grid = tag_grid.copy()
                temp_grid[r, c] = 1
                
                # Check if this blocks all paths
                still_reachable, _, temp_reachable = find_bypass_areas(temp_grid, solution_path, start_pos, end_pos)
                
                # Calculate effectiveness
                if not still_reachable:
                    effectiveness = 1.0
                else:
                    # Calculate percentage of reachable area reduced
                    original_cells = np.sum(new_reachable)
                    remaining_cells = np.sum(temp_reachable)
                    effectiveness = 1.0 - (remaining_cells / original_cells)
                
                # Base score from original points list
                base_score = i  # Lower index = higher score
                
                # Enhanced score includes effectiveness and proximity to end
                end_proximity = 1.0 / (1.0 + min(abs(r - end_pos[0]) + abs(c - end_pos[1]), 10))
                enhanced_score = base_score + (effectiveness * 1000) + (end_proximity * 100)
                simulation_results.append(((r, c), enhanced_score, effectiveness))
            
            # Sort by enhanced score
            simulation_results.sort(key=lambda x: x[1], reverse=True)
    
    print(f"Total blockers placed: {blockers_placed}")
    
    # Final verification
    end_reachable, _, _ = find_bypass_areas(tag_grid, solution_path, start_pos, end_pos)
    if end_reachable:
        print(f"  Warning: End is still reachable without solving puzzles")
        print("  Consider manually adding more Sokoban puzzles to block critical paths")
    else:
        print("  Verification complete: All bypass paths successfully blocked")
    
    return tag_grid, world

# ------------------------------------------------------------------------
# Inject Sokoban puzzle with quality checks
# ------------------------------------------------------------------------
def inject_sokoban_poly(world, tag_grid: np.ndarray, cells, seed, num_boxes):
    """Enhanced Sokoban puzzle injection with solvability verification"""
    # filter out-of-bounds
    rows, cols = tag_grid.shape
    cells = [(r, c) for r, c in cells if 0 <= r < rows and 0 <= c < cols]
    if not cells:
        return False

    # bounding box
    rs, cs = zip(*cells)
    r0, r1 = min(rs), max(rs)
    c0, c1 = min(cs), max(cs)
    h, w = (r1-r0+1), (c1-c0+1)
    
    # Ensure minimum dimensions for viable puzzles
    if h < 3 or w < 3:
        print(f"  Skipping region with dimensions {w}x{h} (needs at least 3x3)")
        return False
        
    # FEATURE 2: Adjust number of boxes based on region size
    original_boxes = num_boxes
    if len(cells) < 8:  # Very small region
        num_boxes = 1
    elif len(cells) < 12:  # Small region
        num_boxes = min(num_boxes, 1)
    elif len(cells) < 18:  # Medium region
        num_boxes = min(num_boxes, 2)
        
    if num_boxes != original_boxes:
        print(f"  Reduced boxes from {original_boxes} to {num_boxes} based on region size")

    lvl = SokobanLevel(w, h, num_boxes)
    mapping = Config.SOKOBAN_GRID_TO_TILE_MAP

    # seed walls/floors
    for dy in range(h):
        for dx in range(w):
            rr, cc = r0+dy, c0+dx
            if (0 <= rr < rows and 0 <= cc < cols and 
                (rr, cc) in cells and 
                tag_grid[rr, cc] != 1 and  # Skip wall tiles
                cc < world.tile_map.shape[1] and rr < world.tile_map.shape[0]):
                lvl.nodes[dy][dx].wall = False
            else:
                lvl.nodes[dy][dx].wall = True

    # Place player at the seed point
    pr, pc = seed
    lvl.setPlayerPos(pr - r0, pc - c0)
    
    # Print the level for debugging
    print(f"  Level dimensions: {w}x{h}")
    print(f"  Attempting to place {num_boxes} boxes")

    # Generate puzzle
    try:
        result = generator.generatePaths(lvl)
        if not result or getattr(lvl, "trash", False):
            print(f"  Failed to generate puzzle")
            if num_boxes > 1:
                print(f"  Retrying with 1 box")
                lvl = SokobanLevel(w, h, 1)
                # Re-seed walls
                for dy in range(h):
                    for dx in range(w):
                        rr, cc = r0+dy, c0+dx
                        if (0 <= rr < rows and 0 <= cc < cols and 
                            (rr, cc) in cells and 
                            tag_grid[rr, cc] != 1):
                            lvl.nodes[dy][dx].wall = False
                        else:
                            lvl.nodes[dy][dx].wall = True
                lvl.setPlayerPos(pr - r0, pc - c0)
                result = generator.generatePaths(lvl)
                if not result or getattr(lvl, "trash", False):
                    return False
            else:
                return False
    except Exception as e:
        print(f"  Exception in generatePaths: {e}")
        return False

    # Get the tile grid
    grid = lvl.get_tile_grid()
    
    # Count boulders and holes to ensure balance
    boulders = sum(1 for row in grid for cell in row if cell == 3)
    holes = sum(1 for row in grid for cell in row if cell == 2)
    
    if boulders != holes:
        print(f"  Error: Unbalanced puzzle with {boulders} boulders and {holes} holes")
        return False

    # FEATURE 1: Post-generation verification using Sokoban solver
    if not verify_sokoban_solvable(grid):
        print(f"  Error: Puzzle verification failed - likely unsolvable")
        return False

    # Write back boulders and holes to tag_grid
    for dy in range(h):
        for dx in range(w):
            val = grid[dy][dx]
            if val in (2, 3):  # hole=2, boulder=3 in SokobanLevel
                rr, cc = r0+dy, c0+dx
                if 0 <= rr < rows and 0 <= cc < cols and tag_grid[rr, cc] != 1:
                    tag_grid[rr, cc] = 4 if val == 2 else 3
                    if cc < world.tile_map.shape[1] and rr < world.tile_map.shape[0]:
                        cell = world.get_tile(cc, rr)
                        cell.possibilities = [mapping[val]]
                        cell.entropy = 0
                        world.tile_map[rr,cc] =mapping[val]

    return True

# ------------------------------------------------------------------------
# Orchestrator: Place puzzles around the map
# ------------------------------------------------------------------------
def prepare_puzzle_world(world, tag_grid: np.ndarray, solution_path, num_boxes_per_puzzle=None):
    # Convert solution_path to set for faster lookups
    solution_set = set(tuple(pos) for pos in solution_path)
    
    # Find all chokepoints
    cps = detect_chokepoints(tag_grid, solution_path)
    
    # Find strategic blocking points
    blockers = find_strategic_blockers(tag_grid, solution_path)
    print(f"  Found {len(blockers)} strategic blocking points")
    path_blockers = find_path_blockers(tag_grid, solution_path)
    print(f"  Found {len(path_blockers)} path blocking points")
    
    # Combine all potential seeds
    seed_candidates = []
    
    # Add solution path points first (highest priority)
    for i, pos in enumerate(solution_path):
        # Skip start and end, and only use every 2nd point to avoid overcrowding
        if i > 0 and i < len(solution_path)-1 and i % 2 == 0:
            seed_candidates.append((pos, 80))
    
    # Add yellow path blockers next (high priority)
    for blocker, score in path_blockers:
        if blocker not in [s[0] for s in seed_candidates]:
            seed_candidates.append((blocker, score))
    
    # Add strategic blockers next (medium priority)
    for blocker, score in blockers:
        if blocker not in [s[0] for s in seed_candidates]:
            seed_candidates.append((blocker, score + 15))
    
    # Add chokepoints last (lowest priority)
    for cp in cps:
        if cp not in [s[0] for s in seed_candidates]:
            seed_candidates.append((cp, 10))
    
    # Sort by priority score
    seed_candidates.sort(key=lambda x: x[1], reverse=True)
    print(f"  Total of {len(seed_candidates)} potential puzzle locations identified")
    
    visited_cells = set()
    puzzle_count = 0
    target_puzzles = min(20, len(seed_candidates))  # Target up to 20 puzzles
    
    # Process seed candidates
    for seed, priority in seed_candidates:
        if puzzle_count >= target_puzzles:
            break
            
        # Skip if seed already used
        if seed in visited_cells:
            continue
            
        # Find region for this seed
        region, quality = find_open_region(tag_grid, seed)
        
        # Skip if too small
        if len(region) < MIN_REGION_CELLS:
            continue
            
        # Special quality threshold for path and solution points
        is_path = tag_grid[seed[0], seed[1]] == 2
        is_solution = seed in solution_set
        min_quality = -1 if (is_path or is_solution) else 1
        
        if quality < min_quality:
            continue
            
        # Check overlap with existing puzzles
        overlap = sum(1 for cell in region if cell in visited_cells)
        overlap_percentage = overlap / len(region) if region else 1.0
        
        # Special case for path and solution tiles - allow more overlap
        if is_path or is_solution:
            allowed_overlap = 0.8  # Allow more overlap
        else:
            allowed_overlap = 0.8
            
        if overlap_percentage > allowed_overlap:
            print(f"  Skipping region at {seed} - {overlap_percentage:.1%} overlap with existing puzzles")
            continue
            
        print(f"Processing region at {seed} (size: {len(region)}, quality: {quality}, priority: {priority})")
        
        # For path-based puzzles, use fewer boxes to improve success rate
        if is_path or is_solution:
            num_boxes = 1  # Simple puzzles have higher success rate
        else:
            num_boxes = min(MAX_BOXES, max(MIN_BOXES, len(region) // 6))
        
        # Try to inject
        if inject_sokoban_poly(world, tag_grid, region, seed, num_boxes):
            puzzle_count += 1
            print(f"Sokoban #{puzzle_count} injected at {seed} (region size {len(region)})")
            
            # Mark only important cells as visited to allow more puzzles
            for r, c in region:
                if tag_grid[r, c] in (3, 4):  # Boulder or hole
                    # Mark just a small area around each object
                    for dr in range(-1, 2):
                        for dc in range(-1, 2):
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < tag_grid.shape[0] and 0 <= nc < tag_grid.shape[1]:
                                visited_cells.add((nr, nc))
                
            # micro-WFC: initialize possibilities and collapse until no contradictions
            for (rr, cc) in region:
                if not (0 <= cc < world.tile_map.shape[1] and 0 <= rr < world.tile_map.shape[0]):
                    continue
                    
                cell = world.get_tile(cc, rr)
                tag = tag_grid[rr, cc]
                if tag in (3, 4):
                    cell.possibilities = [Config.SOKOBAN_GRID_TO_TILE_MAP[tag]]
                else:
                    base = list(Config.FOREST_DOMAIN)
                    if getattr(cell, "is_left_boundary", False):
                        base = [p for p in base if p not in Config.INNER_BOUNDARIES_LEFT_RESTRICT]
                    if getattr(cell, "is_right_boundary", False):
                        base = [p for p in base if p not in Config.INNER_BOUNDARIES_RIGHT_RESTRICT]
                    cell.possibilities = base
                cell.entropy = len(cell.possibilities)

            while True:
                world.runWFC(
                    adjacency_rules=Config.adjacency_rules_forest,
                    weights=Config.tile_weights_forest,
                    region=region
                )
                bad = [
                    (rr, cc) for (rr, cc) in region
                    if 0 <= cc < world.tile_map.shape[1] and 0 <= rr < world.tile_map.shape[0]
                    and world.get_tile(cc, rr).entropy == 0
                    and not world.get_tile(cc, rr).possibilities
                ]
                if not bad:
                    break
                for (rr, cc) in bad:
                    c = world.get_tile(cc, rr)
                    c.possibilities = [Config.TILE_GRASS]
                    c.entropy = 1

    print(f"Total Sokobans injected: {puzzle_count}")
    
    # After placing all Sokoban puzzles, add strategic blockers
    start_pos = None
    end_pos = None
    
    # Find start and end positions
    for r in range(tag_grid.shape[0]):
        for c in range(tag_grid.shape[1]):
            if tag_grid[r, c] == 5:  # Start
                start_pos = (r, c)
            elif tag_grid[r, c] == 6:  # End
                end_pos = (r, c)
    
    if start_pos and end_pos:
        print("\nAdding strategic blockers to prevent direct path to end...")
        # Use the enhanced blocker function with flood fill
        tag_grid, world = place_path_blockers(world, tag_grid, solution_path)
        
    return world
