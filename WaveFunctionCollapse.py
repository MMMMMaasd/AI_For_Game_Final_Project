import pygame
import sys
from SokobanLevel import *
from ClassWorld import World
from ClassDrawWorld import DrawWorld
from Config import *
from enum import Enum, auto
import math

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
COLOR_VICTORY_BG = (50, 50, 50, 200)
COLOR_VICTORY_TEXT = (255, 255, 255)

# === Settings ===
INTERACTIVE = True

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

# Precompute puzzle holes
maze.puzzle_holes = []
for region in maze.puzzle_regions:
    sx, sy, ex, ey, _ = region
    holes = []
    for y in range(sy, ey + 1):
        for x in range(sx, ex + 1):
            if maze.tile_grid[y][x] == 3:
                holes.append((x, y))
    maze.puzzle_holes.append(holes)

grid_width = maze.width
grid_height = maze.height

# === Set up screen ===
width_px = grid_width * TILE_SIZE
height_px = grid_height * TILE_SIZE + LABEL_HEIGHT
screen = pygame.display.set_mode((width_px, height_px))
pygame.display.set_caption("Sokoban Challenge")
PLAYER_SPRITE_IMG = pygame.image.load("./player_sprite.png").convert_alpha()
HOLE_SPRITE_IMG = pygame.image.load("./hole_grass.png").convert_alpha()
STONE_SPRITE_IMG = pygame.image.load("./boulder_grass.png").convert_alpha()

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
        self.steps = 0
        self.score = 0
        self.visited_puzzles = set()
        self.initial_boxes = set(maze.box_positions.copy())
        self.final_boxes = set()

    def _is_in_region(self, pos, region):
        sx, sy, ex, ey, _ = region
        return sx <= pos[0] <= ex and sy <= pos[1] <= ey

    def calculate_puzzle_score(self, puzzle_index):
        boxes = [b for b in self.initial_boxes if self._is_in_region(b, maze.puzzle_regions[puzzle_index])]
        holes = maze.puzzle_holes[puzzle_index]
        min_distance = 0
        for box in boxes:
            distances = [math.hypot(box[0]-h[0], box[1]-h[1]) for h in holes]
            min_distance += min(distances) if distances else 0
        return min_distance

    def move(self, dx, dy):
        new_x, new_y = self.position[0] + dx, self.position[1] + dy
        
        if not (0 <= new_x < self.maze.width and 0 <= new_y < self.maze.height):
            return False
            
        tile_type = self.world.getType(new_x, new_y)
        
        if tile_type in {TILE_GRASS_STONE, TILE_BOX_ON_HOLE}:
            return self._push_box(new_x, new_y, dx, dy)
            
        if self._can_move_to(new_x, new_y):
            self.position = (new_x, new_y)
            self.steps += 1
            self.score += 1
            return True
        return False

    def _can_move_to(self, x, y):
        tile_type = self.world.getType(x, y)
        return ((tile_type not in UNWALKABLE_TILES) and (tile_type is not TILE_SOKO_BLOCKER))
    
    def _push_box(self, box_x, box_y, dx, dy):
        target_x, target_y = box_x + dx, box_y + dy
    
        if not (0 <= target_x < self.maze.width and 0 <= target_y < self.maze.height):
            return False
        
        target_type = self.world.getType(target_x, target_y)
        target_maze_value = self.maze.tile_grid[target_y][target_x]
    
        if (target_type in UNWALKABLE_TILES or
            target_maze_value == 11 or
            target_type in {TILE_GRASS_STONE, TILE_BOX_ON_HOLE}):
            return False
        
        self._move_box(box_x, box_y, target_x, target_y)
        self.position = (box_x, box_y)
        return True
    
    def _move_box(self, from_x, from_y, to_x, to_y):
        original_tile = self.world.getType(from_x, from_y)
        if original_tile == TILE_BOX_ON_HOLE:
            self.world.setTile(from_x, from_y, TILE_GRASS_HOLE)
        else:
            self.world.setTile(from_x, from_y, TILE_GRASS)

        target_tile = self.world.getType(to_x, to_y)
        if target_tile == TILE_GRASS_HOLE:
            self.world.setTile(to_x, to_y, TILE_BOX_ON_HOLE)
        else:
            self.world.setTile(to_x, to_y, TILE_GRASS_STONE)

        if (from_x, from_y) in self.maze.box_positions:
            self.maze.box_positions.remove((from_x, from_y))
        self.maze.box_positions.append((to_x, to_y))
        
    def has_won(self):
        return self.position == self.maze.end
    
    def calculate_final_score(self):
        self.final_boxes = set(self.maze.box_positions)
        efficiency_bonus = 0
        
        for i, region in enumerate(self.maze.puzzle_regions):
            initial_boxes = [b for b in self.initial_boxes if self._is_in_region(b, region)]
            final_boxes = [b for b in self.final_boxes if self._is_in_region(b, region)]
            holes = self.maze.puzzle_holes[i]
            
            if len(final_boxes) >= len(holes):
                min_moves = self.calculate_puzzle_score(i)
                actual_moves = len(initial_boxes) - len(final_boxes)
                efficiency_bonus += max(min_moves - actual_moves, 0) * 0.5
                
        start_dist = math.hypot(maze.start[0]-maze.end[0], maze.start[1]-maze.end[1])
        path_efficiency = start_dist / self.steps if self.steps > 0 else 1
        return int((self.score * path_efficiency) + efficiency_bonus)

# === WFC Setup ===
wfc_world = None
wfc_drawer = None
current_mode = "Maze"
wfc_done = False

def draw_score_panel():
    if not player or not wfc_done:
        return
        
    score_font = pygame.font.SysFont('Arial', 24, bold=True)
    steps_text = f"Steps: {player.steps}"
    score_text = f"Score: {player.calculate_final_score()}"
    
    steps_surface = score_font.render(steps_text, True, (255, 255, 255))
    score_surface = score_font.render(score_text, True, (255, 255, 255))
    
    bg_width = max(steps_surface.get_width(), score_surface.get_width()) + 20
    bg_rect = pygame.Rect(10, 10, bg_width, 65)
    bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
    bg_surface.fill((0, 0, 0, 128))
    screen.blit(bg_surface, bg_rect)
    
    screen.blit(steps_surface, (20, 15))
    screen.blit(score_surface, (20, 40))

def draw_victory_panel():
    overlay = pygame.Surface((width_px, height_px), pygame.SRCALPHA)
    overlay.fill(COLOR_VICTORY_BG)
    screen.blit(overlay, (0, 0))
    
    victory_font = pygame.font.SysFont('Arial', 48)
    score_font = pygame.font.SysFont('Arial', 36)
    
    victory_text = victory_font.render("Victory!", True, COLOR_VICTORY_TEXT)
    final_score = player.calculate_final_score()
    score_text = score_font.render(f"Final Score: {final_score}", True, COLOR_VICTORY_TEXT)
    steps_text = score_font.render(f"Total Steps: {player.steps}", True, COLOR_VICTORY_TEXT)
    
    victory_rect = victory_text.get_rect(center=(width_px//2, height_px//2 - 60))
    score_rect = score_text.get_rect(center=(width_px//2, height_px//2))
    steps_rect = steps_text.get_rect(center=(width_px//2, height_px//2 + 60))
    
    screen.blit(victory_text, victory_rect)
    screen.blit(score_text, score_rect)
    screen.blit(steps_text, steps_rect)
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
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
        pygame.draw.rect(screen, (255, 0, 0), rect, 3)

def draw_grid():
    for x in range(grid_height):
        for y in range(grid_width):
            rect = pygame.Rect(y * TILE_SIZE, x * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            value = tile_grid[x, y]
            colors = {
                0: COLOR_FLOOR,
                1: COLOR_PATH,
                2: COLOR_BOX,
                3: COLOR_HOLE,
                4: COLOR_SOKOBAN_PATH,
                5: COLOR_PLAYER,
                8: (200, 230, 255),
                9: (100, 100, 150),
                10: (50, 200, 50),
                11: (200, 200, 200),
                12: (50, 50, 1)
            }
            pygame.draw.rect(screen, colors.get(value, COLOR_FLOOR), rect)
            pygame.draw.rect(screen, COLOR_GRID_LINE, rect, 1)

def draw_buttons():
    pygame.draw.rect(screen, COLOR_BUTTON, button_maze)
    pygame.draw.rect(screen, COLOR_BUTTON, button_wfc)
    text1 = font.render("Maze View", True, COLOR_BUTTON_TEXT)
    text2 = font.render("Run WFC", True, COLOR_BUTTON_TEXT)
    screen.blit(text1, text1.get_rect(center=button_maze.center))
    screen.blit(text2, text2.get_rect(center=button_wfc.center))

KEY_PRESS_DELAY = 200
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
                wfc_world = World(grid_width, grid_height, maze_tile_grid=tile_grid)
                wfc_drawer = DrawWorld(wfc_world, PLAYER_SPRITE_IMG, HOLE_SPRITE_IMG, STONE_SPRITE_IMG)
                current_mode = "WFC"
                wfc_done = False
                if not INTERACTIVE:
                    while not wfc_done:
                        result = wfc_world.waveFunctionCollapse()
                        if result == 0: wfc_done = True
                    wfc_drawer.update()

    keys = pygame.key.get_pressed()
    if wfc_done and not player and current_mode == "WFC":
        player = Player(maze, wfc_world)

    if player and wfc_done:
        current_time = pygame.time.get_ticks()
        
        # Continuous region check
        if game_state == GameState.EXPLORATION:
            for i, (sx, sy, ex, ey, _) in enumerate(maze.puzzle_regions):
                if (sx <= player.position[0] <= ex and
                    sy <= player.position[1] <= ey):
                    if i not in player.visited_puzzles:
                        player.visited_puzzles.add(i)
                        player.score += 0.5
                    game_state = GameState.PUZZLE
                    current_puzzle_index = i
                    break

        if current_time - last_move_time > KEY_PRESS_DELAY:
            moved = False
            if game_state == GameState.EXPLORATION:
                if keys[pygame.K_LEFT]: moved = player.move(-1, 0)
                elif keys[pygame.K_RIGHT]: moved = player.move(1, 0)
                elif keys[pygame.K_UP]: moved = player.move(0, -1)
                elif keys[pygame.K_DOWN]: moved = player.move(0, 1)
                
            elif game_state == GameState.PUZZLE:
                if keys[pygame.K_ESCAPE]:
                    game_state = GameState.EXPLORATION
                else:
                    if keys[pygame.K_LEFT]: moved = player.move(-1, 0)
                    elif keys[pygame.K_RIGHT]: moved = player.move(1, 0)
                    elif keys[pygame.K_UP]: moved = player.move(0, -1)
                    elif keys[pygame.K_DOWN]: moved = player.move(0, 1)

            if moved:
                last_move_time = current_time
                wfc_drawer.update()

        if player.has_won():
            player.final_boxes = set(maze.box_positions)
            game_state = GameState.VICTORY

    # Drawing
    screen.fill(COLOR_FLOOR)
    if current_mode == "Maze":
        draw_grid()
        draw_end_marker()
        draw_buttons()
    else:
        draw_buttons()
        if wfc_world and wfc_drawer:
            if INTERACTIVE and not wfc_done:
                result = wfc_world.waveFunctionCollapse()
                if result == 0: wfc_done = True
            wfc_drawer.update()
            if wfc_done:
                wfc_drawer.draw(screen, player.position if player else None)
                draw_end_marker()
                if player:
                    draw_score_panel()
                    if player.position == maze.end and not player.has_won():
                        warning_text = font.render("Reach the exit to complete!", True, (255, 255, 255))
                        screen.blit(warning_text, (width_px//2 - 100, 50))

    if game_state == GameState.VICTORY:
        draw_victory_panel()
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
