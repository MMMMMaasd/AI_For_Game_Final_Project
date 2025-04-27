from collections import deque
import random
import Config
from SokobanInjector import inject_sokoban_puzzle

def agent_runner(world, solution_path, size=7, max_iterations=10):
    """
    Repeatedly inject Sokoban puzzles at chokepoints of any alternate routes
    from start to end, until no bypass paths remain.
    """
    if not solution_path:
        print("Agent: no solution path provided.")
        return

    start = solution_path[0]
    end   = solution_path[-1]

    # start with no blocked tiles; we'll block only injected regions
    avoid_set = set()
    blocked_chokepoints = set()

    def bfs_find_alternates():
        """Return a path from start to end avoiding avoid_set."""
        visited = {start}
        queue = deque([(start, [start])])
        while queue:
            (r, c), path = queue.popleft()
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = r + dr, c + dc
                coord = (nr, nc)
                # bounds
                if not (0 <= nr < world.rows and 0 <= nc < world.cols):
                    continue
                # avoid blocked regions
                if coord in avoid_set:
                    continue
                # already visited
                if coord in visited:
                    continue
                # must be passable
                tid = world.getType(nc, nr)
                if coord != end and tid not in (
                    *Config.FOREST_FLOOR_TILES,
                    Config.SOKOBAN_FLOOR_ID,
                    *Config.TILE_BOULDER_SPOTS,
                    Config.SOKOBAN_BOX_ID
                ):
                    continue
                visited.add(coord)
                new_path = path + [coord]
                if coord == end:
                    return new_path
                queue.append((coord, new_path))
        return None

    for iteration in range(1, max_iterations+1):
        # for first iteration, use the original solution_path
        if not avoid_set:
            alt_path = solution_path
        else:
            alt_path = bfs_find_alternates()
            if not alt_path:
                print(f"Agent: no alternate path after {iteration-1} injections → DONE.")
                return

        # find divergence points (where alt_path leaves solution_path)
        divergences = [p for p in alt_path if p not in solution_path]
        # on first iteration divergences = all points except start/end
        if not divergences:
            # fallback to any point along the path (excluding start/end)
            divergences = solution_path[1:-1]

        # pick an unblocked chokepoint or random divergence
        unblocked = [p for p in divergences if p not in blocked_chokepoints]
        chokepoint = random.choice(unblocked if unblocked else divergences)
        blocked_chokepoints.add(chokepoint)

        # build region around chokepoint
        half = size // 2
        r0, c0 = chokepoint
        region = [
            (r, c)
            for r in range(r0-half, r0+half+1)
            for c in range(c0-half, c0+half+1)
            if 0 <= r < world.rows and 0 <= c < world.cols
        ]
        # pick two seeds inside region
        seeds = random.sample(region, 2) if len(region) >= 2 else [chokepoint]
        if len(seeds) < 2:
            print(f"Agent: could not pick 2 seeds in region {region}; aborting.")
            return

        print(f"Agent: iteration {iteration}, chokepoint {chokepoint}, seeds {seeds}")
        new_tiles = inject_sokoban_puzzle(world, solution_path, size=size, seeds=seeds)
        if not new_tiles:
            print("Agent: injection failed; aborting.")
            return

        # block injected tiles only
        avoid_set.update(new_tiles)

    print("Agent: reached max iterations without fully blocking paths.")
