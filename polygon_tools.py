# polygon_tools.py
# Utility functions for polygon-based region detection in Sokoban injection

import numpy as np
from collections import deque


def region_flood(mask: np.ndarray, seed: tuple[int, int]) -> set[tuple[int, int]]:
    """
    Flood-fill to get all connected True cells from seed in mask.
    mask: 2D boolean array
    seed: (r, c) starting cell, must satisfy mask[r,c] == True
    Returns a set of (r,c) cells.
    """
    rows, cols = mask.shape
    visited = {seed}
    q = deque([seed])
    while q:
        r, c = q.popleft()
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r + dr, c + dc
            if (0 <= nr < rows and 0 <= nc < cols and
                mask[nr, nc] and (nr, nc) not in visited):
                visited.add((nr, nc))
                q.append((nr, nc))
    return visited


def marching_squares(mask: np.ndarray, seed: tuple[int,int]) -> list[tuple[float,float]]:
    """
    Given a boolean mask and a seed inside a region, extract the approximate contour
    as an ordered list of (x,y) vertex coordinates outlining the region boundary.
    """
    # 1) Flood-fill the region
    region = region_flood(mask, seed)
    if not region:
        return []

    # 2) Collect boundary segments (grid-edge segments where region meets background)
    segments = set()
    for (r, c) in region:
        for dr, dc, edge in ((-1,0,'top'), (1,0,'bottom'), (0,-1,'left'), (0,1,'right')):
            nr, nc = r+dr, c+dc
            if not (0 <= nr < mask.shape[0] and 0 <= nc < mask.shape[1] and mask[nr,nc]):
                # exterior edge
                if edge == 'top':
                    segments.add(((c, r), (c+1, r)))
                elif edge == 'bottom':
                    segments.add(((c, r+1), (c+1, r+1)))
                elif edge == 'left':
                    segments.add(((c, r), (c, r+1)))
                elif edge == 'right':
                    segments.add(((c+1, r), (c+1, r+1)))

    # 3) Chain segments into a polygon path
    if not segments:
        return []
    start_seg = segments.pop()
    poly = [start_seg[0], start_seg[1]]
    curr = start_seg[1]
    while segments:
        for seg in list(segments):
            a, b = seg
            if a == curr:
                poly.append(b)
                curr = b
                segments.remove(seg)
                break
            elif b == curr:
                poly.append(a)
                curr = a
                segments.remove(seg)
                break
        else:
            # no connected segment found, break to avoid infinite loop
            break

    return poly


def point_in_polygon(point: tuple[float,float], poly: list[tuple[float,float]]) -> bool:
    """
    Ray-casting algorithm to test if `point` is inside `poly`.
    poly is a list of (x,y) vertices.
    """
    x, y = point
    inside = False
    n = len(poly)
    for i in range(n):
        x0, y0 = poly[i]
        x1, y1 = poly[(i+1) % n]
        if ((y0 > y) != (y1 > y)):
            x_int = (x1 - x0) * (y - y0) / (y1 - y0) + x0
            if x < x_int:
                inside = not inside
    return inside


def flood_fill_polygon(tag_grid: np.ndarray, poly: list[tuple[float,float]], seed=None) -> list[tuple[int,int]]:
    """
    Given a tag_grid and a polygon boundary (in grid coords), return a list of all
    cells (r,c) whose centers lie inside the polygon and whose tag is 0 or 2.
    Uses flood fill algorithm starting from the seed point for better connectivity.
    """
    rows, cols = tag_grid.shape
    visited = set()
    result = []
    
    # If no seed provided, find the first valid point inside the polygon
    if seed is None:
        for r in range(rows):
            for c in range(cols):
                if tag_grid[r, c] in (0, 2):
                    cx, cy = c + 0.5, r + 0.5
                    if point_in_polygon((cx, cy), poly):
                        seed = (r, c)
                        break
            if seed is not None:
                break
    
    # If we couldn't find a seed point, return empty list
    if seed is None:
        return []
    
    # Initialize queue with seed
    queue = deque([seed])
    
    # Directions for flood fill
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    while queue:
        r, c = queue.popleft()
        
        # Skip if already visited
        if (r, c) in visited:
            continue
        
        # Mark as visited
        visited.add((r, c))
        # Skip wall tiles and tiles adjacent to walls
        adjacent_to_wall = False
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and tag_grid[nr, nc] == 1:
                adjacent_to_wall = True
                break
        
        # Only include walkable cells (open or path)
        if tag_grid[r, c] in (0, 2) and not adjacent_to_wall:
            # Test cell center
            cx, cy = c + 0.5, r + 0.5
            if point_in_polygon((cx, cy), poly):
                result.append((r, c))
                
                # Add neighbors to queue
                for dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    if (0 <= nr < rows and 0 <= nc < cols and 
                        (nr, nc) not in visited and 
                        tag_grid[nr, nc] in (0, 2)):
                        queue.append((nr, nc))
    
    return result

