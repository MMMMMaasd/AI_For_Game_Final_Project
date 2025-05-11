import pygame
import sys
from SokobanLevel import *
from ClassWorld import World
from ClassDrawWorld import DrawWorld
from Config import *
from enum import Enum, auto
import random

class GameState(Enum):
    EXPLORATION = auto()
    PUZZLE = auto()
    VICTORY = auto()
    
# === Pygame Constants ===
TILE_SIZE = 32
FPS = 60
LABEL_HEIGHT = 120


# === Colors ===
COLOR_FLOOR = (230, 230, 230)
COLOR_PATH = (255, 255, 150)
COLOR_BOX = (160, 82, 45)
COLOR_HOLE = (138, 43, 226)
COLOR_SOKOBAN_PATH = (255, 200, 200)
COLOR_PLAYER = (50, 200, 50)
COLOR_GRID_LINE = (200, 200, 200)
COLOR_BUTTON = (70, 130, 180)
COLOR_BUTTON_TEXT = (255, 255, 255)
COLOR_VICTORY_BG = (50, 50, 50, 200)  # Semi-transparent dark background
COLOR_VICTORY_TEXT = (255, 255, 255)
COLOR_WARNING = (255, 0, 0)

# === Settings ===
INTERACTIVE = True  # ✅ Set False for instant collapse

# === Initialize Pygame ===
pygame.init()
pygame.font.init()
font = pygame.font.SysFont('Arial', 18)
game_state = GameState.EXPLORATION
player = None
current_puzzle_index = None

# === Maze Setup ===
maze = MazeGenerator(25, 25, num_boxes=5)
maze.generate()
maze.tile_grid = decorate_maze(maze.tile_grid)
tile_grid = maze.tile_grid

grid_width = maze.width
grid_height = maze.height

# === Set up screen ===
width_px = grid_width * TILE_SIZE
height_px = grid_height * TILE_SIZE + LABEL_HEIGHT
screen = pygame.display.set_mode((width_px, height_px))
pygame.display.set_caption("Maze + WFC Visualizer")
PLAYER_SPRITE_IMG = pygame.image.load("./player_sprite.png").convert_alpha()
HOLE_SPRITE_IMG = pygame.image.load("./hole_grass.png").convert_alpha()
STONE_SPRITE_IMG = pygame.image.load("./boulder_grass.png").convert_alpha()
CANDY_SPRITE_IMG = pygame.image.load("./rare-candy.png").convert_alpha()

clock = pygame.time.Clock()

# === Buttons ===
button_maze = pygame.Rect(width_px // 4 - 80, grid_height * TILE_SIZE + 10, 160, 40)
button_wfc = pygame.Rect(3 * width_px // 4 - 80, grid_height * TILE_SIZE + 10, 160, 40)

# === Player setup ===
class Player:
    def __init__(self, maze, world):
        self.maze = maze
        self.world = world
        self.position = maze.start
        self.solved_puzzles = set()
        self.collected_candies = set()
        self.candy_positions = {}
        
        self.region_walkable_tiles = {}
        for i, (sx, sy, ex, ey, _) in enumerate(maze.puzzle_regions):
            walkable = []
            for y in range(sy, ey + 1):
                for x in range(sx, ex + 1):
                    if tile_grid[y, x] == 12:  # Walkable grass tile
                        walkable.append((x, y))
            self.region_walkable_tiles[i] = walkable
    
    def get_random_candy_position(self, region_index):
        """Get a random walkable position within the region"""
        walkable = self.region_walkable_tiles.get(region_index, [])
        return random.choice(walkable) if walkable else None
    
    def _is_path(self, x, y):
        """Check if a tile is walkable path"""
        return self.world.getType(x, y) in {TILE_GRASS, TILE_GRASS_HOLE}
    
    def solve_puzzle(self, region_index):
        self.solved_puzzles.add(region_index)
        candy_pos = self.get_random_candy_position(region_index)
        print(f"Solving puzzle {region_index}, candy pos: {candy_pos}")  # Debug
        if candy_pos:
            self.candy_positions[region_index] = candy_pos
            print(f"Candy placed at {candy_pos} for region {region_index}")  # Debug
    
    def check_candy_collection(self):
        x, y = self.position
        for puzzle_index, (cx, cy) in self.candy_positions.items():
            if (puzzle_index in self.solved_puzzles and
                puzzle_index not in self.collected_candies and
                x == cx and y == cy):
                self.collected_candies.add(puzzle_index)
                return True
        return False
            
    def move(self, dx, dy):
        new_x, new_y = self.position[0] + dx, self.position[1] + dy
        
        # Check boundaries
        if not (0 <= new_x < self.maze.width and 0 <= new_y < self.maze.height):
            return False
            
        tile_type = self.world.getType(new_x, new_y)
        
        # Handle box pushing
        if tile_type in {TILE_GRASS_STONE, TILE_BOX_ON_HOLE}:
            return self._push_box(new_x, new_y, dx, dy)
            
        # Normal movement
        if self._can_move_to(new_x, new_y):
            self.position = (new_x, new_y)
            self._check_puzzle_region()
            return True
        return False
        
    def _can_move_to(self, x, y):
        tile_type = self.world.getType(x, y)
        return ((tile_type not in UNWALKABLE_TILES) and (tile_type is not TILE_SOKO_BLOCKER))
    
    def _push_box(self, box_x, box_y, dx, dy):
        target_x, target_y = box_x + dx, box_y + dy
    
        # Check boundaries
        if not (0 <= target_x < self.maze.width and 0 <= target_y < self.maze.height):
            return False
        
        target_type = self.world.getType(target_x, target_y)
        target_maze_value = self.maze.tile_grid[target_y][target_x]
    
        # Can't push into blockers, walls, or other boxes
        if (target_type in UNWALKABLE_TILES or
            target_maze_value == 11 or  # Wall tile
            target_type in {TILE_GRASS_STONE, TILE_BOX_ON_HOLE}):
            return False
        
        # Perform the push
        self._move_box(box_x, box_y, target_x, target_y)
        self.position = (box_x, box_y)  # Move player to box's previous position
        return True
    
    
    def _move_box(self, from_x, from_y, to_x, to_y):
        """Handle the actual box movement and tile updates"""
        # Determine what to leave behind
        original_tile = self.world.getType(from_x, from_y)
        if original_tile == TILE_BOX_ON_HOLE:
            # Box was on a hole - restore the hole
            self.world.setTile(from_x, from_y, TILE_GRASS_HOLE)
        else:
            # Box was on grass - restore grass
            self.world.setTile(from_x, from_y, TILE_GRASS)
    
        # Determine what to create at new position
        target_tile = self.world.getType(to_x, to_y)
        if target_tile == TILE_GRASS_HOLE:
            # Box is moving onto a hole
            self.world.setTile(to_x, to_y, TILE_BOX_ON_HOLE)
        else:
            # Box is moving onto grass
            self.world.setTile(to_x, to_y, TILE_GRASS_STONE)
    
        # Update box position tracking
        if (from_x, from_y) in self.maze.box_positions:
            self.maze.box_positions.remove((from_x, from_y))
        self.maze.box_positions.append((to_x, to_y))
        
    def _check_puzzle_region(self):
        x, y = self.position
        print("Regions: =================")
        print(self.maze.puzzle_regions)
        for i, (sx, sy, ex, ey, _) in enumerate(self.maze.puzzle_regions):
            if sx <= x <= ex and sy <= y <= ey and i not in self.solved_puzzles:
                print(f"Entered puzzle region {i}")
                # Here you'd activate puzzle mode
        
    def candies_remaining(self):
        return len(self.maze.puzzle_regions) - len(self.collected_candies)
        
    def has_won(self):
    # Must be at exit AND collected all candies
        at_exit = self.position == self.maze.end
        all_candies = len(self.collected_candies) == len(self.maze.puzzle_regions)
        return at_exit and all_candies
        
# === WFC Setup ===
wfc_world = None
wfc_drawer = None
current_mode = "Maze"
wfc_done = False

def draw_candies():
    if not player or not wfc_done:
        return
        
    for puzzle_index, (cx, cy) in player.candy_positions.items():
        if (puzzle_index in player.solved_puzzles and
            puzzle_index not in player.collected_candies):
            # Draw candy at its position
            print("Draw Candy !!!!!!!")
            print()
            scaled_candy = pygame.transform.scale(CANDY_SPRITE_IMG,
                                             (TILE_SIZE, TILE_SIZE))
            screen.blit(scaled_candy,
                       (cx * TILE_SIZE + TILE_SIZE//4,
                        cy * TILE_SIZE + TILE_SIZE//4))
                        
def draw_candy_counter():
    if not player or not wfc_done:
        return
        
    candy_font = pygame.font.SysFont('Arial', 24, bold=True)
    counter_text = f"Candies: {len(player.collected_candies)}/{len(player.maze.puzzle_regions)}"
    text_surface = candy_font.render(counter_text, True, (255, 255, 255))
    
    # Draw a semi-transparent background
    bg_rect = pygame.Rect(10, 10, text_surface.get_width() + 20, text_surface.get_height() + 10)
    bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
    bg_surface.fill((0, 0, 0, 128))  # Semi-transparent black
    screen.blit(bg_surface, bg_rect)
    
    # Draw the text
    screen.blit(text_surface, (20, 15))
    
def draw_victory_panel():
    # Create a semi-transparent overlay
    overlay = pygame.Surface((width_px, height_px), pygame.SRCALPHA)
    overlay.fill(COLOR_VICTORY_BG)
    screen.blit(overlay, (0, 0))
    
    # Draw victory text
    victory_font = pygame.font.SysFont('Arial', 48)
    victory_text = victory_font.render("Congratulations!", True, COLOR_VICTORY_TEXT)
    text_rect = victory_text.get_rect(center=(width_px//2, height_px//2 - 50))
    screen.blit(victory_text, text_rect)
    
    # Draw instruction text
    instr_font = pygame.font.SysFont('Arial', 24)
    instr_text = instr_font.render("Press any key to continue", True, COLOR_VICTORY_TEXT)
    instr_rect = instr_text.get_rect(center=(width_px//2, height_px//2 + 50))
    screen.blit(instr_text, instr_rect)
    
    pygame.display.flip()
    
    # Wait for key press
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False

def draw_end_marker():
    if maze.end:
        end_x, end_y = maze.end
        rect = pygame.Rect(
            end_x * TILE_SIZE,
            end_y * TILE_SIZE,
            TILE_SIZE,
            TILE_SIZE
        )
        pygame.draw.rect(screen, (255, 0, 0), rect, 3)  # Red border
        
# === Draw functions ===
def draw_grid():
    for x in range(grid_height):
        for y in range(grid_width):
            rect = pygame.Rect(y * TILE_SIZE, x * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            value = tile_grid[x, y]

            if value == 0:
                pygame.draw.rect(screen, COLOR_FLOOR, rect)
            elif value == 1:
                pygame.draw.rect(screen, COLOR_PATH, rect)
            elif value == 2:
                pygame.draw.rect(screen, COLOR_BOX, rect)
            elif value == 3:
                pygame.draw.rect(screen, COLOR_HOLE, rect)
            elif value == 4:
                pygame.draw.rect(screen, COLOR_SOKOBAN_PATH, rect)
            elif value == 5:
                pygame.draw.rect(screen, COLOR_PLAYER, rect)
            elif value == 6:
                # pygame.draw.rect(screen, (100, 149, 237), rect)  # 🎯 Blue (Cornflower Blue)
                pygame.draw.rect(screen, COLOR_FLOOR, rect)
            elif value == 7:
                # pygame.draw.rect(screen, (220, 20, 60), rect)    # 🎯 Red (Crimson)
                pygame.draw.rect(screen, COLOR_FLOOR, rect)
            elif value == 8:  # Region floor
                pygame.draw.rect(screen, (200, 230, 255), rect)  # Light blue
            elif value == 9:  # Region wall
                pygame.draw.rect(screen, (100, 100, 150), rect)  # Dark blue
            elif value == 10: # Region player start
                pygame.draw.rect(screen, (50, 200, 50), rect)  # Bright green
            elif value == 11:
                pygame.draw.rect(screen, (200, 200, 200), rect)
            elif value == 12:
                pygame.draw.rect(screen, (50, 50, 1), rect)

            pygame.draw.rect(screen, COLOR_GRID_LINE, rect, 1)

def draw_buttons():
    pygame.draw.rect(screen, COLOR_BUTTON, button_maze)
    pygame.draw.rect(screen, COLOR_BUTTON, button_wfc)

    text_surface1 = font.render("Maze View", True, COLOR_BUTTON_TEXT)
    text_surface2 = font.render("Run WFC", True, COLOR_BUTTON_TEXT)

    text_rect1 = text_surface1.get_rect(center=button_maze.center)
    text_rect2 = text_surface2.get_rect(center=button_wfc.center)

    screen.blit(text_surface1, text_rect1)
    screen.blit(text_surface2, text_rect2)


def is_puzzle_solved(puzzle_index):
    sx, sy, ex, ey, box_count = maze.puzzle_regions[puzzle_index]
    solved_boxes = 0
    
    # Get all holes in this puzzle region
    holes_in_region = []
    tile_grid = maze.tile_grid
    for y in range(sy, ey + 1):
        for x in range(sx, ex + 1):
            if tile_grid[x, y] == 3:
                holes_in_region.append((x, y))
    print(f"holes region: {holes_in_region}, number of holes in total: {len(holes_in_region)}")
    # Check all boxes in the region
    for box_x, box_y in maze.box_positions:
            # Check if box is on any hole (either regular hole or box_on_hole)
            if (box_y, box_x) in holes_in_region:
                solved_boxes += 1
    
    print(f"Puzzle {puzzle_index}: {solved_boxes}/{box_count} boxes solved")
    return solved_boxes >= box_count

    
KEY_PRESS_DELAY = 200  # milliseconds between moves
last_move_time = 0
# === Main loop ===
running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if button_maze.collidepoint(event.pos):
                # Regenerate Maze
                maze.generate()
                maze.tile_grid = decorate_maze(maze.tile_grid)
                tile_grid = maze.tile_grid

                wfc_world = None
                wfc_drawer = None
                player = None
                current_mode = "Maze"
                wfc_done = False
                game_state = GameState.EXPLORATION

            if button_wfc.collidepoint(event.pos):
                # Switch to WFC mode
                wfc_world = World(grid_width, grid_height, maze_tile_grid=tile_grid)
                wfc_drawer = DrawWorld(wfc_world, PLAYER_SPRITE_IMG, HOLE_SPRITE_IMG, STONE_SPRITE_IMG)

                current_mode = "WFC"
                wfc_done = False

                if not INTERACTIVE:
                    while not wfc_done:
                        result = wfc_world.waveFunctionCollapse()
                        if result == 0:
                            wfc_done = True
                    wfc_drawer.update()
    keys = pygame.key.get_pressed()
     # Initialize player after WFC is done
    if wfc_done and not player and current_mode == "WFC":
        player = Player(maze, wfc_world)
    if player and wfc_done:
        current_time = pygame.time.get_ticks()
        if current_time - last_move_time > KEY_PRESS_DELAY:
            if game_state == GameState.EXPLORATION:
                moved = False
                if keys[pygame.K_LEFT]:
                    moved = player.move(-1, 0)
                elif keys[pygame.K_RIGHT]:
                    moved = player.move(1, 0)
                elif keys[pygame.K_UP]:
                    moved = player.move(0, -1)
                elif keys[pygame.K_DOWN]:
                    moved = player.move(0, 1)
                if moved:
                    last_move_time = current_time
                    player.check_candy_collection()
                    wfc_drawer.update()
                
                # Check if entered a puzzle region
                for i, region in enumerate(maze.puzzle_regions):
                    sx, sy, ex, ey, _ = region
                    if (sx <= player.position[0] <= ex and
                        sy <= player.position[1] <= ey and
                        i not in player.solved_puzzles):
                        game_state = GameState.PUZZLE
                        current_puzzle_index = i
                        break
                    
            elif game_state == GameState.PUZZLE:
                # Handle puzzle-specific controls
                if keys[pygame.K_ESCAPE]:
                    game_state = GameState.EXPLORATION
                else:
                    # Handle puzzle movement (Sokoban mechanics)
                    moved = False
                    if keys[pygame.K_LEFT]:
                        moved = player.move(-1, 0)  # Replace with puzzle-specific movement
                    elif keys[pygame.K_RIGHT]:
                        moved = player.move(1, 0)
                    elif keys[pygame.K_UP]:
                        moved = player.move(0, -1)
                    elif keys[pygame.K_DOWN]:
                        moved = player.move(0, 1)
                    if moved:
                        last_move_time = current_time
                        wfc_drawer.update()
                
                    # Check if puzzle solved
                    if is_puzzle_solved(current_puzzle_index):
                        player.solve_puzzle(current_puzzle_index)
                        game_state = GameState.EXPLORATION
        
        # Check win condition
        if player.has_won():
            game_state = GameState.VICTORY
            print("Congratulations! You won!")
    # === Update screen ===
    screen.fill(COLOR_FLOOR)

    if current_mode == "Maze":
        draw_grid()
        draw_end_marker()
        draw_buttons()

    else:
        draw_buttons()
        for x in range(grid_height):
            for y in range(grid_width):
                if tile_grid[y, x] == 2:  # 2 = box in maze
                    wfc_world.addStoneTile(x, y, TILE_GRASS_STONE)
                if tile_grid[y,x] == 5: # 5 = player
                    wfc_world.addStoneTile(x, y, TILE_PLAYER)
                if tile_grid[y,x] == 3: # 3 = holes
                    wfc_world.addStoneTile(x, y, TILE_GRASS_HOLE)
                if tile_grid[y,x] == 11:
                    wfc_world.addStoneTile(x, y, TILE_SOKO_BLOCKER)
                if tile_grid[y, x] == 12:
                    wfc_world.addStoneTile(x, y, TILE_GRASS)
                if tile_grid[y, x] == 10:
                    wfc_world.addStoneTile(x, y, TILE_GRASS)
                    
        if wfc_world and wfc_drawer:
            if INTERACTIVE and not wfc_done:
                result = wfc_world.waveFunctionCollapse()
                if result == 0: wfc_done = True
            
            wfc_drawer.update()
            if wfc_done and player:
                wfc_drawer.draw(screen, player.position)
                draw_candies()
                draw_candy_counter()
                draw_end_marker()
                # Show end position warnings if needed
                if player.position == maze.end and not player.has_won():
                    warning_bg = pygame.Surface((width_px, 60), pygame.SRCALPHA)
                    warning_bg.fill((0, 0, 0, 180))
                    screen.blit(warning_bg, (0, 40))
    
                    warning_font = pygame.font.SysFont('Arial', 24, bold=True)
                    if player.candies_remaining() > 0:
                        warning_text = warning_font.render(
                            f"Collect {player.candies_remaining()} more candy(s) to win!",
                            True,
                            (255, 255, 255)
                        )
                    else:
                        warning_text = warning_font.render(
                            "You have all candies! Return to the exit!",
                            True,
                            (255, 255, 255)
                        )
                    screen.blit(warning_text, (width_px//2 - warning_text.get_width()//2, 50))
            else:
                wfc_drawer.draw(screen)
    
    if game_state == GameState.VICTORY:
        draw_victory_panel()
        # Reset game after victory
        maze.generate()
        maze.tile_grid = decorate_maze(maze.tile_grid)
        tile_grid = maze.tile_grid
        wfc_world = None
        wfc_drawer = None
        player = None
        current_mode = "Maze"
        wfc_done = False
        game_state = GameState.EXPLORATION

    pygame.display.flip()

pygame.quit()
sys.exit()
