import random
from Config import *

class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.world = None
        self.possibilities = list(adjacency_rules.keys())
        self.entropy = len(self.possibilities)
        self.neighbours = dict()
        self.collapsed_neighbors = {}

    def addNeighbour(self, direction, tile):
        self.neighbours[direction] = tile
    
    def getNeighbour(self, direction):
        return self.neighbours.get(direction)
    
    def getDirections(self):
        return list(self.neighbours.keys())

    def getPossibilities(self):
        return self.possibilities
    
    def collapse(self):
        weights = [tileWeights[possibility] for possibility in self.possibilities]
        self.possibilities = random.choices(self.possibilities, weights=weights, k=1)
        self.entropy = 0
        
  
    def _apply_progressive_boundary_rules(self, known_neighbors):
        left = known_neighbors.get(WEST)
        right = known_neighbors.get(EAST)
        top = known_neighbors.get(NORTH)
        bottom = known_neighbors.get(SOUTH)

        required_tile = None
        
        if left in inner_set_tiles:
            required_tile = TILE_ROCK_WALL_LEFT
            
            # Refine if we know top/bottom neighbors
            if top in inner_set_tiles and bottom not in inner_set_tiles:
                required_tile = TILE_ROCK_VERTICAL_DIAGONAL_LEFT
            elif top not in inner_set_tiles and bottom in inner_set_tiles:
                required_tile = TILE_ROCK_WALL_BOTTOM_LEFT

        elif right in inner_set_tiles:
            required_tile = TILE_ROCK_WALL_RIGHT2
            if top in inner_set_tiles and bottom not in inner_set_tiles:
                required_tile = TILE_ROCK_VERTICAL_DIAGONAL_RIGHT
            elif top not in inner_set_tiles and bottom in inner_set_tiles:
                required_tile = TILE_ROCK_WALL_BOTTOM_RIGHT

        elif top in inner_set_tiles:
            required_tile = TILE_ROCK_VERTICAL_MID

        elif bottom in inner_set_tiles:
            required_tile = TILE_ROCK_WALL_BOTTOM_MID

        # Apply if we found a rule
        if required_tile and required_tile in self.possibilities:
            self.possibilities = [required_tile]
            self.entropy = 1
            return True
            
        return False
    
    def _is_inner_boundary(self):
        if not hasattr(self, 'world') or not self.world.wall_mask[self.y][self.x]:
            return False
            
        # Get neighbor mask states
        left = self.getNeighbour(WEST)
        right = self.getNeighbour(EAST)
        top = self.getNeighbour(NORTH)
        bottom = self.getNeighbour(SOUTH)
        
        left_floor = left and self.world.floor_mask[left.y][left.x] if left else False
        right_floor = right and self.world.floor_mask[right.y][right.x] if right else False
        top_floor = top and self.world.floor_mask[top.y][top.x] if top else False
        bottom_floor = bottom and self.world.floor_mask[bottom.y][bottom.x] if bottom else False
        left_player = left and self.world.player_mask[left.y][left.x] if left else False
        right_player = right and self.world.player_mask[right.y][right.x] if right else False
        top_player = top and self.world.player_mask[top.y][top.x] if top else False
        bottom_player = bottom and self.world.player_mask[bottom.y][bottom.x] if bottom else False
        left_box = left and self.world.box_mask[left.y][left.x] if left else False
        right_box = right and self.world.box_mask[right.y][right.x] if right else False
        top_box = top and self.world.box_mask[top.y][top.x] if top else False
        bottom_box = bottom and self.world.box_mask[bottom.y][bottom.x] if bottom else False
        left_target = left and self.world.target_mask[left.y][left.x] if left else False
        right_target = right and self.world.target_mask[right.y][right.x] if right else False
        top_target = top and self.world.target_mask[top.y][top.x] if top else False
        bottom_target = bottom and self.world.target_mask[bottom.y][bottom.x] if bottom else False

        left_is_inner = left_floor or left_player or left_box or left_target
        right_is_inner = right_floor or right_player or right_box or right_target
        top_is_inner = top_floor or top_player or top_box or top_target
        bottom_is_inner = bottom_floor or bottom_player or bottom_box or bottom_target
        # Determine boundary type based on adjacent floor tiles
        if left_is_inner:
            if top_is_inner and not bottom_is_inner and not right_is_inner:
                return TILE_ROCK_VERTICAL_DIAGONAL_LEFT
            elif not top_is_inner and bottom_is_inner and not right_is_inner:
                return TILE_ROCK_WALL_BOTTOM_LEFT
            else:
                return TILE_ROCK_WALL_LEFT
                
        elif right_is_inner:
            if top_is_inner and not bottom_is_inner and not right_is_inner:
                return TILE_ROCK_VERTICAL_DIAGONAL_RIGHT
            elif not top_is_inner and bottom_is_inner and not right_is_inner:
                return TILE_ROCK_WALL_BOTTOM_RIGHT
            else:
                return TILE_ROCK_WALL_RIGHT2
                
        elif top_is_inner:
            return TILE_ROCK_VERTICAL_MID
            
        elif bottom_is_inner:
            return TILE_ROCK_WALL_BOTTOM_MID
            
        return None
    
    def constrain(self, neighbourPossibilities, direction):
        reduced = False


        if self.entropy > 0:
            # ✅ First, determine the opposite direction
            if direction == NORTH:
                opposite = SOUTH
            elif direction == EAST:
                opposite = WEST
            elif direction == SOUTH:
                opposite = NORTH
            elif direction == WEST:
                opposite = EAST
            else:
                raise ValueError(f"Invalid direction: {direction}")

            # ✅ Collect all valid connectors from neighbor possibilities
            connectors = set()
            for neighbourPossibility in neighbourPossibilities:
                connectors |= adjacency_rules[neighbourPossibility][direction]
            
            print(f"[DEBUG] Constraining ({self.x}, {self.y}) from dir {direction}")
            print(f"Neighbor possibilities: {neighbourPossibilities}")
            print(f"Valid connectors: {connectors}")
            print(f"Current possibilities: {self.possibilities}")
    
            # ✅ Remove any invalid possibilities
            for possibility in self.possibilities.copy():
                if possibility not in connectors:
                    self.possibilities.remove(possibility)
                    reduced = True
            print(f"New possibilities: {self.possibilities}")
            self.entropy = len(self.possibilities)
            
        if self.entropy > 1 and self.world.wall_mask[self.y][self.x]:
            boundary_tile = self._is_inner_boundary()
            if boundary_tile and boundary_tile in self.possibilities:
                self.possibilities = [boundary_tile]
                self.entropy = 1
                reduced = True

        return reduced

