# test.py

import numpy as np
from collections import deque
import pygame
import os
import sys

import Config
from agent_before_phase_2 import prepare_puzzle_world

# -----------------------------------------------------------------------------
# 1) Paste your 30×30 TILE-ID map here (exactly as you listed it)
# -----------------------------------------------------------------------------
tile_ids_str = """
 217  217  217  218    1   13   17   13  641  641  641  642    1    1    1    1    9   17    8  216  217  217  218    1    1  648  649  650  664  649
 225  225  646  226   16  641    8    1    1    1    1    8    1  217  217  218    9   16    1  224  225  646  226    9   13   17   17   17  656  657
   9  648  649  666  648  649  650    1   13    8    1    1    1  225  646  226    8    9   13   13  664  649  650   13    3    1    1    8  664  649
 641   17   17  658  656  657  658    1    8  642  664  649  666  664  649  666   13   13    8    8  672  673  655   13    1    1   17    8  672  673
 649  650    1    1    1    1    1    1   16    8  672  657  658  656  673  658    9   17    9   16  675  676  677    8   16    8    8    9  675  676
 673  655    1  648  649  666  242    8   13   13  664  649  666  675  676  677    1   17   17    8    9  642    9   16   13   13    8    9   16    9
 676  677    1  656  657  658   13    8   17    9  656  673  658    8   13    9   13   13    1    1    8    9   13    8   17   16  641    8  208  209
   1    1    1  664  649  666   13    1    9    9  675  676  677   13    8   17   17    9    8    1    8    1    8   17   13  648  649  650  216  217
   1    9    8  672  657  658   13    1   17   17   13    9    8    9   13    8   16  208  209  209  210    8    9    9   13   17   17   17  224  646
   1   13    9  664  649  666   17    8   17   16    1   16    9    8    8  208  209  254  217  217  255  209  209  210    8    8   16    8  664  649
   1   16    8  672  657  658   13  641  641  641   17  208  209  210    9  216  217  217  263  225  225  225  225  226    9   13    8    8  672  657
   1   13    9  664  649  666    8  224  217  226   16  216  217  218   17  216  217  217  218    8    8    9  641    9   16    8   13    8  664  649
   1   16   13  656  673  658    9   16  225    9    8  224  646  226   16  216  217  217  226    9    1  648  649  650   17    1   13   17  656  657
   1    1   16  675  676  677   13    8    9    8  642  664  649  666   17  224  646  225    9   17   17  656  657  658   17  641    9    8  664  649
   1    1    8   13    8    1   17   17   17   17    9  656  673  658   13  648  649  650    8   13    8  664  649  666  648  649  650   17  656  657
 221    1    1   17    9    9    2  253  253  253   16  675  676  677    1   17   17   17   17  641    8  656  657  658  656  657  658   17  664  649
  17  666    1    9   16    9   13  641  641  246    9   13    1    8   16   13    1    9  648  649  650  664  649  666  664  649  666    8  672  657
  13    1    1    1    1    1   17  224  217  218    9  641  641  641  642    1    1    9  656  673  658  656  657  658  672  657  658    8  664  649
  16    1    9  680  212  213    1   16  225  226    9  224  217  226    8    8   13    9  675  676  677  664  649  666  664  649  666    8  656  673
   1    1   17  219  261  221   16    8    9    1    9   16  225    9    9   13    3   16    8    9    8  656  673  658  672  657  658   16  675  676
   1   17   13   17   17   17    9    9   16    9   13   17  641  642    9    9    8    3    8    9   16  675  676  677  664  649  666  641  642    1
   1    1    1   16    9  641  641  641  641   16   13  648  649  650    8    8    9    1    9   17    1   16    1    8  672  673  662  649  650  648
  13    1    1    3    9  224    1    1    1    1   13  654  673  655   13   17   16   17   17   17   17   17   17   13  675  676  670  657  658  656
   1   13    1  209  210    1    1   16    1    1    9  675  676  677    8    1    9    2  253  253  253  253  253   16    8   13  664  649  666  664
 209  209    1    1  226    1  247  641  246    1    1  642    9    8   17    1    8   13  641  641  641  641  246    9   16    8  672  657  658  672
 217  217  218    1    2    1  216  217  218   17    1    1    1    1  641  641    8   16  224  217  217  217  218   17    1   13  664  649  666  664
 225  646  226    1    1    1  224  646  226    9  224  225    1    1    1    1   13  641   16  225  225  646  226   16  641   17  656  657  658  656
 664  649  666  664  649  666  664  649  666  641  641  641  641    1    8    1    1  226    9    9  664  649  666  648  649  650  664  649  666  664
 656  657  658  672  657  658  672  657  658  224  217  217  226    8  642   17    1    1   13   16  656  673  658   17   17   17  656  673  658  656
 664  649  666  664  649  666  664  649  666   16  225  225    9  641    1    1    1    1  644   13  675  676  677   13  641   16  675  676  677  675
"""

tile_id_map = np.array(
    [ list(map(int, row.split())) for row in tile_ids_str.strip().splitlines() ],
    dtype=int
)

# -----------------------------------------------------------------------------
# 2) Paste your 30×30 TAG-GRID here
# -----------------------------------------------------------------------------
tag_grid_str = """
0 0 0 0 0 0 0 0 1 1 1 0 2 2 2 6 0 0 0 0 0 0 0 0 0 1 1 1 1 1
0 0 1 1 1 1 1 2 2 2 2 0 2 0 0 0 0 0 0 0 1 1 1 0 0 0 0 0 1 1
0 1 1 1 1 1 1 2 0 0 2 2 2 0 1 0 0 0 0 0 1 1 1 0 1 0 0 0 1 1
1 0 0 1 1 1 1 2 0 0 1 1 1 1 1 1 0 0 0 0 1 1 1 0 0 0 0 0 1 1
1 1 2 2 2 2 2 2 0 0 1 1 1 1 1 1 0 0 0 0 1 1 1 0 0 0 0 0 1 1
1 1 2 1 1 1 1 0 0 0 1 1 1 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0
1 1 2 1 1 1 0 0 0 0 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
2 2 2 1 1 1 0 0 0 0 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 0 0
2 0 0 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 0 0
2 0 0 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1
2 0 0 1 1 1 0 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1
2 0 0 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 0 0 0 0 1 1
2 0 0 1 1 1 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 1 1 1 0 0 0 0 1 1
2 0 0 1 1 1 0 0 0 0 0 1 1 1 0 1 1 0 0 0 0 1 1 1 1 1 1 0 1 1
2 2 0 0 0 0 0 0 0 0 0 1 1 1 0 1 1 1 0 0 0 1 1 1 1 1 1 0 1 1
0 2 2 0 0 0 1 1 1 1 0 1 1 1 0 0 0 0 1 1 1 1 1 1 1 1 1 0 1 1
0 1 2 0 0 0 0 1 1 1 0 0 0 0 0 0 0 0 1 1 1 1 1 1 1 1 1 0 1 1
0 2 2 0 0 0 0 0 0 0 0 1 1 1 0 0 0 0 1 1 1 1 1 1 1 1 1 0 1 1
0 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 1 1 1 1 0 1 1
2 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 1 1 1 1 1 1 0 1 1
2 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 1 0 0 0 1 1 1 1 1 1 0 0 0
2 2 0 0 0 1 1 1 1 0 0 1 1 1 0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 1
0 2 2 1 0 0 2 2 2 0 0 1 1 1 0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 1
0 0 2 0 0 2 2 0 2 2 0 1 1 1 0 0 0 1 1 1 1 1 1 0 0 0 1 1 1 1
0 0 2 2 0 2 1 1 1 2 2 0 0 0 0 0 0 0 1 1 1 1 1 0 0 0 1 1 1 1
0 0 0 2 1 2 0 0 0 0 2 2 2 0 1 1 0 0 0 0 0 0 0 0 0 0 1 1 1 1
0 1 0 2 2 2 0 1 0 0 0 0 2 2 2 2 0 1 0 0 0 1 0 0 1 0 1 1 1 1
1 1 1 1 1 1 1 1 1 1 1 1 1 0 0 2 2 0 0 0 1 1 1 1 1 1 1 1 1 1
1 1 1 1 1 1 1 1 1 0 0 0 0 0 0 0 2 0 0 0 1 1 1 0 0 0 1 1 1 1
1 1 1 1 1 1 1 1 1 0 0 0 0 1 0 5 2 0 1 0 1 1 1 0 1 0 1 1 1 1
"""

# You can optionally print it to verify
# print(tag_grid_str)

tag_grid = np.array(
    [ list(map(int, row.split())) for row in tag_grid_str.strip().splitlines() ],
    dtype=int
)

rows, cols = tag_grid.shape

# -----------------------------------------------------------------------------
# 3) Reconstruct solution_path from start(5) → end(6)
# -----------------------------------------------------------------------------
def find_solution_path(grid):
    start = tuple(np.argwhere(grid==5)[0])
    end   = tuple(np.argwhere(grid==6)[0])
    q, prev = deque([start]), {start: None}
    dirs = [(-1,0),(1,0),(0,-1),(0,1)]
    while q:
        r,c = q.popleft()
        if (r,c)==end: break
        for dr,dc in dirs:
            nr,nc = r+dr, c+dc
            if 0<=nr<rows and 0<=nc<cols and grid[nr,nc]!=1 and (nr,nc) not in prev:
                prev[(nr,nc)] = (r,c)
                q.append((nr,nc))
    # backtrack
    path, cur = [], end
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    return path[::-1]

solution_path = find_solution_path(tag_grid)
print(f"Found solution path with {len(solution_path)} steps")

# -----------------------------------------------------------------------------
# 4) StubWorld: minimal getType, get_tile, runWFC
# -----------------------------------------------------------------------------
class StubCell:
    def __init__(self):
        self.possibilities = []
        self.entropy = 0

class StubWorld:
    def __init__(self, tile_map, tag_map):
        self.tile_map = tile_map
        self.tag_map = tag_map
        self.rows, self.cols = tag_map.shape
        self._cells = [
            [StubCell() for _ in range(tag_map.shape[1])]
            for __ in range(tag_map.shape[0])
        ]
    def getType(self, x, y):
        if 0 <= y < self.rows and 0 <= x < self.cols:
            return int(self.tile_map[y, x])
        return None
    def get_tile(self, x, y):
        if 0 <= y < self.rows and 0 <= x < self.cols:
            return self._cells[y][x]
        return None
    def runWFC(self, adjacency_rules, weights, region):
        # no-op for testing
        pass

# -----------------------------------------------------------------------------
# 5) Run your polygon-based Sokoban pass
# -----------------------------------------------------------------------------
world = StubWorld(tile_id_map, tag_grid)
prepare_puzzle_world(world, tag_grid, solution_path)

# -----------------------------------------------------------------------------
# 6) Bake the new boulder/hole IDs back into the tile map
# -----------------------------------------------------------------------------
mapping = Config.SOKOBAN_GRID_TO_TILE_MAP
for r in range(rows):
    for c in range(cols):
        if 0 <= r < tile_id_map.shape[0] and 0 <= c < tile_id_map.shape[1]:
            if tag_grid[r,c] == 3:      # boulder
                tile_id_map[r,c] = mapping[3]
            elif tag_grid[r,c] == 4:    # hole
                # Force holes to use tile ID 727 from Tanibo tileset
                tile_id_map[r,c] = 727
        else:
            print(f"Warning: Skipping out-of-bounds coordinate ({r},{c})")

# -----------------------------------------------------------------------------
# 7) Dump the results
# -----------------------------------------------------------------------------
print("\n=== TAG GRID AFTER INJECTION (3=boulder,4=hole) ===")
for row in tag_grid:
    print(" ".join(str(v) for v in row))

print("\n=== TILE ID MAP AFTER INJECTION ===")
for row in tile_id_map:
    print(" ".join(f"{v:4d}" for v in row))

# -----------------------------------------------------------------------------
# 8) Visualize with Pygame - Full Tileset Renderer
# -----------------------------------------------------------------------------
class TilesetRenderer:
    def __init__(self, tile_id_map, tag_grid, solution_path):
        self.tile_id_map = tile_id_map
        self.tag_grid = tag_grid
        self.solution_path = solution_path
        self.rows, self.cols = tile_id_map.shape
        self.tilesize = Config.TILESIZE * Config.SCALETILE
        self.width = int(self.cols * self.tilesize)
        self.height = int(self.rows * self.tilesize + 40)  # Extra space for status
        
        # Toggle for view mode
        self.show_tile_ids = True  # Start with tile IDs view
        
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Forest + Sokoban Visualization")
        self.font = pygame.font.Font(pygame.font.get_default_font(), 18)
        self.clock = pygame.time.Clock()
        
        # Load spritesheets
        self.sprite_cache = {}
        self.forest_sheet = pygame.image.load(Config.SPRITESHEET_PATH)
        
        # Try to load special sprites
        self.stone_sprite = None
        self.tanibo_sheet = None
        
        if os.path.exists(Config.STONE_SPRITE_PATH):
            self.stone_sprite = pygame.image.load(Config.STONE_SPRITE_PATH)
        
        if os.path.exists(Config.TANIBO_SPRITESHEET_PATH):
            self.tanibo_sheet = pygame.image.load(Config.TANIBO_SPRITESHEET_PATH)
    
    def get_sprite(self, tile_id):
        # Check cache first
        if tile_id in self.sprite_cache:
            return self.sprite_cache[tile_id]
        
        # Handle special case for holes using Tanibo tileset ID 727
        if self.tag_grid[r, c] == 4 and tile_id == 0:
            tile_id = 727  # Use Tanibo hole tile ID
        
        if tile_id in Config.tile_sprites:
            sheet_name, x, y = Config.tile_sprites[tile_id]
            
            sheet = None
            if sheet_name == "forest":
                sheet = self.forest_sheet
            elif sheet_name == "stone" and self.stone_sprite:
                sheet = self.stone_sprite
            elif sheet_name == "tanibo" and self.tanibo_sheet:
                sheet = self.tanibo_sheet
                
            if sheet:
                tile = pygame.Surface((Config.TILESIZE, Config.TILESIZE), pygame.SRCALPHA)
                tile.blit(sheet, (0, 0), (x, y, Config.TILESIZE, Config.TILESIZE))
                scaled = pygame.transform.scale(tile, (int(self.tilesize), int(self.tilesize)))
                self.sprite_cache[tile_id] = scaled
                return scaled
        
        # Fallback for unknown tiles - create a color based on type
        color = (0, 128, 0)  # Default green
        if tile_id == Config.SOKOBAN_BOX_ID:
            color = (139, 69, 19)  # Brown for boulder
        elif tile_id not in Config.WALKABLE_TILES:
            color = (100, 70, 30)  # Dark brown for walls
            
        surf = pygame.Surface((int(self.tilesize), int(self.tilesize)))
        surf.fill(color)
        self.sprite_cache[tile_id] = surf
        return surf
    
    def draw_tag_grid(self):
        # Draw colored rectangles based on tag values
        for r in range(self.rows):
            for c in range(self.cols):
                tag = self.tag_grid[r, c]
                if tag == 0:  # Walkable
                    color = (128, 128, 128)  # Gray
                elif tag == 1:  # Wall
                    color = (0, 128, 0)      # Green
                elif tag == 2:  # Path
                    color = (255, 255, 0)    # Yellow
                elif tag == 3:  # Boulder
                    color = (139, 69, 19)    # Brown
                elif tag == 4:  # Hole
                    color = (0, 0, 255)      # Blue
                elif tag == 5:  # Start
                    color = (255, 0, 0)      # Red
                elif tag == 6:  # End
                    color = (128, 0, 128)    # Purple
                else:
                    color = (255, 255, 255)  # White (unknown)
                
                rect = pygame.Rect(c * self.tilesize, r * self.tilesize, 
                                  self.tilesize, self.tilesize)
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (50, 50, 50), rect, 1)  # Grid lines
        
        # Highlight solution path
        if self.solution_path:
            for r, c in self.solution_path:
                rect = pygame.Rect(c * self.tilesize, r * self.tilesize, 
                                  self.tilesize, self.tilesize)
                pygame.draw.rect(self.screen, (255, 255, 0), rect, 2)
    
    def draw_tile_map(self):
        # Draw actual tiles based on tile IDs
        for r in range(self.rows):
            for c in range(self.cols):
                tile_id = self.tile_id_map[r, c]
                
                # Special handling for holes - ensure they use the right tile ID
                if self.tag_grid[r, c] == 4 and tile_id == 0:
                    tile_id = 727  # Force hole tile ID
                
                sprite = self.get_sprite(tile_id)
                self.screen.blit(sprite, (c * self.tilesize, r * self.tilesize))
        
        # Highlight special elements with outlines
        for r in range(self.rows):
            for c in range(self.cols):
                tag = self.tag_grid[r, c]
                rect = pygame.Rect(c * self.tilesize, r * self.tilesize, 
                                  self.tilesize, self.tilesize)
                
                if tag == 3:  # Boulder
                    pygame.draw.rect(self.screen, (200, 100, 50), rect, 3)
                elif tag == 4:  # Hole
                    pygame.draw.rect(self.screen, (50, 150, 200), rect, 3)
                elif tag == 5:  # Start
                    pygame.draw.rect(self.screen, (0, 255, 0), rect, 3)
                elif tag == 6:  # End
                    pygame.draw.rect(self.screen, (255, 0, 0), rect, 3)
    
    def run(self):
        running = True
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_m:
                        self.show_tile_ids = not self.show_tile_ids
                        mode = "Tile ID Map" if self.show_tile_ids else "Tag Grid"
                        print(f"Switched to {mode} View")
            
            # Clear screen
            self.screen.fill((30, 30, 30))
            
            # Draw current view
            if self.show_tile_ids:
                self.draw_tile_map()
            else:
                self.draw_tag_grid()
            
            # Status info
            mode = "Tile ID Map" if self.show_tile_ids else "Tag Grid"
            status = f"Forest + Sokoban - {mode} View (M to toggle, ESC to exit)"
            text = self.font.render(status, True, (200, 200, 200))
            self.screen.blit(text, (10, self.height - 30))
            
            # Update display
            pygame.display.flip()
            self.clock.tick(30)
        
        pygame.quit()
        sys.exit()

# Run visualization
if __name__ == "__main__":
    renderer = TilesetRenderer(tile_id_map, tag_grid, solution_path)
    renderer.run()