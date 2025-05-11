import collections
import numpy as np
import time
import Config


def aStarSearchOuter():
    """Outer A* pathfinding through map_values"""
    start_pos = findStart()
    goal_pos = findEnd()
    maze_solved = False

    frontier = PriorityQueue()
    frontier.push([start_pos], heuristic(start_pos, goal_pos))
    exploredSet = set()
    actions = PriorityQueue()
    actions.push([0], heuristic(start_pos, goal_pos))
    count = 0

    while not frontier.isEmpty():
        node = frontier.pop()
        node_action = actions.pop()
        current_pos = node[-1]
        count += 1


        #reached the goal position, return the solution
        if current_pos == goal_pos:
            solution = ','.join(map(str, node_action[1:])).replace(',','') # Clean action output
            print("Solving Steps: ", len(solution))
            print("Solution Moves: ", solution)
            print("Nodes Expanded: ", count)
            maze_solved = True
            return solution, maze_solved


        if current_pos not in exploredSet:
            exploredSet.add(current_pos)
            Cost = cost_func(node)

            #Innner search selected
            if not current_pos == start_pos and map_values[current_pos[0]][current_pos[1]] in SOKOBAN_ENTRANCE:
                print("Searching INNER A*")
                """
                inner_result, success = solve_inner_sokoban(current_pos)
                if success:
                    # Inject inner path into outer path (depends on your structure)
                    node += inner_result.path
                    # Maybe skip to end of Sokoban region?
                    continue
                    """

            for neighbor, move_label in legalActions(current_pos[0], current_pos[1]):
                tile_id = map_values[neighbor[0]][neighbor[1]]

                Heuristic = heuristic(neighbor, goal_pos)
                frontier.push(node + [neighbor], Heuristic + Cost)
                actions.push(node_action + [move_label], Heuristic + Cost)
    solution = "Unsolvable Map, Failed Search - Nodes Exhausted"
    print("Solution Moves: ", solution)
    print("Nodes Expanded: ", count)
    return solution, maze_solved

map_values = []
pre_collapse_values = []

sokoban_areas = []
sokoban_starts = []
sokoban_ends = []
sokoban_players = []

sample_map = [
  [900, 9, 16, 656, 673, 658, 16, 5, 17, 13, 656, 673, 658, 8, 1, 644, 9, 642, 641, 17],
  [3, 9, 17, 675, 676, 677, 13, 5, 5, 13, 675, 676, 677, 13, 648, 665, 650, 648, 649, 650],
  [5, 17, 9, 13, 17, 9, 9, 5, 13, 8, 1, 13, 8, 13, 654, 673, 658, 656, 673, 658],
  [5, 1, 13, 13, 641, 17, 5, 5, 17, 13, 5, 8, 16, 9, 675, 676, 677, 675, 676, 677],
  [5, 8, 13, 648, 649, 650, 13, 17, 5, 5, 5, 5, 9, 1, 642, 1, 9, 13, 13, 16],
  [5, 17, 13, 656, 673, 674, 13, 1, 3, 9, 8, 9, 5, 9, 641, 1, 8, 9, 17, 9],
  [5, 8, 9, 675, 676, 677, 1, 1, 5, 13, 5, 13, 13, 648, 649, 650, 13, 8, 16, 8],
  [5, 13, 16, 13, 8, 16, 1, 5, 1, 13, 5, 5, 13, 654, 673, 658, 16, 13, 5, 9],
  [13, 1, 13, 5, 5, 5, 1, 9, 1, 5, 5, 8, 13, 675, 676, 677, 17, 13, 5, 9],
  [9, 5, 5, 13, 5, 5, 8, 5, 5, 17, 5, 13, 5, 13, 13, 13, 5, 5, 5, 1],
  [9, 5, 17, 5, 5, 5, 9, 9, 5, 5, 16, 9, 5, 5, 13, 5, 1, 17, 13, 5],
  [13, 5, 5, 5, 3, 9, 5, 8, 13, 5, 17, 5, 16, 9, 5, 9, 9, 5, 8, 5],
  [8, 13, 13, 5, 16, 1, 5, 5, 16, 5, 9, 8, 5, 8, 5, 1, 5, 17, 9, 5],
  [5, 5, 17, 5, 5, 5, 5, 8, 13, 5, 5, 13, 8, 5, 13, 13, 5, 16, 5, 5],
  [16, 9, 8, 8, 8, 16, 8, 13, 644, 13, 17, 5, 13, 5, 1, 5, 13, 8, 17, 5],
  [8, 5, 13, 13, 5, 5, 9, 648, 665, 650, 13, 5, 16, 16, 5, 5, 5, 5, 9, 9],
  [8, 13, 644, 9, 9, 13, 13, 656, 657, 674, 8, 9, 3, 5, 16, 16, 13, 8, 13, 648],
  [650, 648, 665, 650, 8, 5, 13, 664, 665, 666, 9, 9, 5, 3, 9, 9, 9, 641, 9, 656],
  [658, 656, 673, 674, 13, 8, 9, 656, 657, 674, 9, 16, 9, 5, 3, 13, 648, 665, 650, 664],
  [677, 675, 676, 677, 17, 641, 642, 664, 665, 666, 641, 8, 3, 5, 8, 13, 656, 657, 674, 672]
]

sample_grid = [
    [5,	7,	7,	7,	7,	7,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0],
    [9,	9,	9,	8,	8,	8,	7,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0],
    [8,	8,	9,	8,	8,	8,	7,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0],
    [8,	8,	9,	8,	8,	8,	7,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0],
    [8,	8,	9,	9,	10,9,	7,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0],
    [8,	8,	8,	8,	8,	9,	1,	7,	7,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0],
    [8,	8,	8,	8,	8,	8,	1,	1,	1,	7,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0],
    [8,	8,	8,	9,	9,	9,	7,	7,	1,	1,	7,	0,	0,	0,	0,	0,	0,	0,	0,	0],
    [8,	8,	8,	9,	8,	9,	1,	7,	7,	1,	7,	0,	0,	0,	7,	7,	7,	7,	7,	7],
    [8,	8,	9,	9,	8,	8,	1,	7,	7,	1,	7,	0,	0,	7,	11,11,11,11,11,11],
    [1,	1,	1,	7,	7,	7,	1,	1,	1,	1,	7,	0,	0,	7,	11,11,11,11,11,11],
    [1,	7,	7,	0,	0,	0,	7,	7,	7,	7,	0,	0,	0,	7,	11,12,3,	3,	11,11],
    [1,	1,	1,	7,	0,	0,	0,	0,	0,	0,	0,	0,	0,	7,	11,12,12,2,	12,11],
    [7,	7,	1,	1,	7,	7,	7,	7,	7,	7,	7,	7,	7,	7,	11,11,2,	12,12,11],
    [8,	8,	8,	9,	9,	8,	8,	8,	8,	8,	8,	1,	1,	1,	11,11,12,11,12,11],
    [8,	8,	8,	8,	10,9,	8,	8,	8,	8,	8,	1,	7,	1,	11,11,3,	2,	12,11],
    [8,	8,	8,	8,	8,	9,	8,	8,	8,	8,	8,	1,	7,	1,	12,5,	12,12,11,11],
    [8,	8,	8,	8,	8,	9,	8,	8,	9,	9,	9,	1,	7,	7,	11,11,12,12,11,11],
    [8,	8,	8,	8,	8,	9,	9,	8,	9,	8,	8,	7,	0,	7,	11,11,11,12,11,11],
    [8,	8,	8,	8,	8,	8,	9,	9,	9,	8,	8,	7,	0,	7,	11,11,11,12,12,12],
]

#------------------------------------------------------------------------------------

class PriorityQueue:
    """Define a PriorityQueue data structure that will be used"""
    def  __init__(self):
        self.Heap = []
        self.Count = 0

    def push(self, item, priority):
        entry = (priority, self.Count, item)
        PriorityQueue.heappush(self.Heap, entry)
        self.Count += 1

    def pop(self):
        (_, _, item) = PriorityQueue.heappop(self.Heap)
        return item

    def isEmpty(self):
        return len(self.Heap) == 0

    # Code taken from heapq
    @staticmethod
    def heappush(heap, item):
        """Push item onto heap, maintaining the heap invariant."""
        heap.append(item)
        PriorityQueue._siftdown(heap, 0, len(heap)-1)

    @staticmethod
    def heappop(heap):
        """Pop the smallest item off the heap, maintaining the heap invariant."""
        lastelt = heap.pop()    # raises appropriate IndexError if heap is empty
        if heap:
            returnitem = heap[0]
            heap[0] = lastelt
            PriorityQueue._siftup(heap, 0)
            return returnitem
        return lastelt

    @staticmethod
    def _siftup(heap, pos):
        endpos = len(heap)
        startpos = pos
        newitem = heap[pos]
        # Bubble up the smaller child until hitting a leaf.
        childpos = 2*pos + 1    # leftmost child position
        while childpos < endpos:
            # Set childpos to index of smaller child.
            rightpos = childpos + 1
            if rightpos < endpos and not heap[childpos] < heap[rightpos]:
                childpos = rightpos
            # Move the smaller child up.
            heap[pos] = heap[childpos]
            pos = childpos
            childpos = 2*pos + 1
        # The leaf at pos is empty now.  Put newitem there, and bubble it up
        # to its final resting place (by sifting its parents down).
        heap[pos] = newitem
        PriorityQueue._siftdown(heap, startpos, pos)

    @staticmethod
    def _siftdown(heap, startpos, pos):
        newitem = heap[pos]
        # Follow the path to the root, moving parents down until finding a place
        # newitem fits.
        while pos > startpos:
            parentpos = (pos - 1) >> 1
            parent = heap[parentpos]
            if newitem < parent:
                heap[pos] = parent
                pos = parentpos
                continue
            break
        heap[pos] = newitem

#------------------------------------------------------------------------------------


#--------------------------------------------------------------------------------------------

UNWALKABLE_TILES = {2, 3, 5, 230, 643, 649, 651, 653, 654, 655, 656, 657, 658, 664, 665, 666, 672, 673, 674, 678, 679, 902}
#648, 650
SOKOBAN_ENTRANCE = {900}
RED_TILE = 73

def findStart():
    for y in range(len(map_values)):
        for x in range(len(map_values[0])):
            if map_values[y][x] == 900:
                return (y, x)

def findEnd():
    for y in reversed(range(len(map_values))):
        for x in reversed(range(len(map_values[0]))):
            if map_values[y][x] not in UNWALKABLE_TILES:
                return (y, x)
    return None

def heuristic(pos, goal):
    #Manhattan distance
    return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])


"""def cost_func(actions):
    return len([x for x in actions if x.islower()])"""


def cost_func(path):
    """
    path: list of positions [(y, x), (y, x), ...]
    Adds +1 for each normal move, +10 for each move into a 900 tile (Sokoban entrance).
    """
    if not path:
        return 0

    total_cost = 0
    for pos in path[1:]:  # Skip the starting position
        tile = map_values[pos[0]][pos[1]]
        if tile in SOKOBAN_ENTRANCE:
            total_cost += 0.5
        else:
            total_cost += 1
    return total_cost


def legalActions(x, y):
    directions = [(-1, 0, 'u'), (1, 0, 'd'), (0, -1, 'l'), (0, 1, 'r')]
    result = []
    for dx, dy, move in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < len(map_values) and 0 <= ny < len(map_values[0]):
            tile_id = map_values[nx][ny]
            if tile_id in SOKOBAN_ENTRANCE:
                result.append(((nx, ny), move.capitalize()))  # Special move into Sokoban zone
            elif tile_id not in UNWALKABLE_TILES:
                result.append(((nx, ny), move))
    return result

"""def prepareSokobanAreas():
    global sokoban_areas
    found_players = 0
    for y in range(len(pre_collapse_values)):
        for x in range(len(pre_collapse_values[0])):
            found_players += 1
            if ((not found_players == 0) and (pre_collapse_values[y][x] == 5)):"""


def updateSolution(solution, solved):
    if solved:
        print("changing")
        i, j = findStart()
        map_values[i][j] = RED_TILE
        for move in solution:
            is_soko_move = move.isupper()
            move = move.lower()
            if move == 'u':
                i-=1
            elif move == 'd':
                i+=1
            elif move == 'l':
                j-=1
            elif move == 'r':
                j+=1
            if not is_soko_move:
                map_values[i][j] = RED_TILE


def solveMap(passed_map, tile_grid, maze):
    #print(sokoban_areas)
    #print(sokoban_starts)
    #print(sokoban_ends)
    #print(sokoban_players)
    print("A* solving generated map ")
    time_start = time.time()

    global map_values
    global pre_collapse_values
    map_values = passed_map
    pre_collapse_values = tile_grid

    print(map_values)

    solution = ''
    solved = False
    solution, solved = aStarSearchOuter()
    updateSolution(solution, solved)

    time_end=time.time()
    time_str = '%.2f seconds.' %(time_end-time_start)
    print("Time of test: ", time_str)

    return map_values

#solveMap(sample_map, sample_grid, maze)