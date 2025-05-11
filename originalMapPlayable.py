import pygame
import numpy as np
from collections import defaultdict
from Config import *

# Initialize Pygame
pygame.init()

# Map configuration
MAP_WIDTH = len(wfc_input_array[0])  # Number of columns
MAP_HEIGHT = len(wfc_input_array)    # Number of rows
BASE_TILE_SIZE = 8  # Base tile size (will be scaled with zoom)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Zoom configuration
ZOOM_LEVELS = [0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0]  # Available zoom levels
current_zoom = 2  # Start with 2x zoom (index in ZOOM_LEVELS)
TILE_SIZE = int(BASE_TILE_SIZE * ZOOM_LEVELS[current_zoom])

# Calculate viewport size in tiles
VIEWPORT_TILES_W = SCREEN_WIDTH // TILE_SIZE
VIEWPORT_TILES_H = SCREEN_HEIGHT // TILE_SIZE


# Colors
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pokemon Forest Maze")

# Load spritesheet
try:
    spritesheet = pygame.image.load(SPRITESHEET_PATH).convert_alpha()
except:
    print(f"Error loading spritesheet at {SPRITESHEET_PATH}")
    spritesheet = pygame.Surface((16*8, 16*8))  # Fallback empty spritesheet
    spritesheet.fill((255, 0, 255))  # Magenta for missing texture

# Load player sprite
try:
    player_sprite = pygame.image.load("player_sprite.png").convert_alpha()  # Replace with your player sprite path
    # Scale player sprite to match tile size (or slightly smaller)
    player_sprite = pygame.transform.scale(player_sprite, (TILE_SIZE, TILE_SIZE))
except:
    print("Error loading player sprite, using red rectangle instead")
    player_sprite = None

# Player setup
player_pos = [5, 11]  # Starting position (x, y)
win_pos = [29, 62]    # Winning position (x, y)

# Create a dictionary to map tile IDs to their spritesheet coordinates
def create_tile_mapping():
    tile_map = {}
    for tile_id in unique_ids_set:
        x = (tile_id % 8) * 16  # Assuming 8 tiles per row in spritesheet
        y = (tile_id // 8) * 16
        tile_map[tile_id] = (x, y)
    return tile_map

tile_mapping = create_tile_mapping()

# Game state
camera_x = max(0, player_pos[0] - VIEWPORT_TILES_W // 2)
camera_y = max(0, player_pos[1] - VIEWPORT_TILES_H // 2)
game_won = False

def update_zoom(new_zoom_index):
    """Update zoom level and recalculate tile size"""
    global current_zoom, TILE_SIZE, VIEWPORT_TILES_W, VIEWPORT_TILES_H
    current_zoom = new_zoom_index % len(ZOOM_LEVELS)
    TILE_SIZE = int(BASE_TILE_SIZE * ZOOM_LEVELS[current_zoom])
    VIEWPORT_TILES_W = SCREEN_WIDTH // TILE_SIZE
    VIEWPORT_TILES_H = SCREEN_HEIGHT // TILE_SIZE
    
    # Rescale player sprite if it exists
    if player_sprite:
        global player_sprite_scaled
        original_sprite = pygame.image.load("player_sprite.png").convert_alpha()
        player_sprite_scaled = pygame.transform.scale(original_sprite, (TILE_SIZE, TILE_SIZE))
    
    # Update camera to keep player centered
    update_camera()

def render_map():
    """Render the visible portion of the map based on camera position"""
    start_x = max(0, camera_x)
    start_y = max(0, camera_y)
    end_x = min(MAP_WIDTH, start_x + VIEWPORT_TILES_W + 1)  # +1 to prevent gaps at edges
    end_y = min(MAP_HEIGHT, start_y + VIEWPORT_TILES_H + 1)
    
    for y in range(start_y, end_y):
        for x in range(start_x, end_x):
            tile_id = wfc_input_array[y][x]
            if tile_id in tile_mapping:
                src_x, src_y = tile_mapping[tile_id]
                dest_x = (x - camera_x) * TILE_SIZE
                dest_y = (y - camera_y) * TILE_SIZE
                
                # Scale down the tile from original 16px to our display size
                tile_surface = pygame.Surface((16, 16), pygame.SRCALPHA)
                tile_surface.blit(spritesheet, (0, 0), (src_x, src_y, 16, 16))
                scaled_tile = pygame.transform.scale(tile_surface, (TILE_SIZE, TILE_SIZE))
                screen.blit(scaled_tile, (dest_x, dest_y))
            else:
                # Unknown tile - draw magenta placeholder
                pygame.draw.rect(screen, (255, 0, 255),
                                ((x - camera_x) * TILE_SIZE,
                                 (y - camera_y) * TILE_SIZE,
                                 TILE_SIZE, TILE_SIZE))

def render_player():
    """Render the player at their current position"""
    player_screen_x = (player_pos[0] - camera_x) * TILE_SIZE
    player_screen_y = (player_pos[1] - camera_y) * TILE_SIZE
    
    if -TILE_SIZE <= player_screen_x < SCREEN_WIDTH and -TILE_SIZE <= player_screen_y < SCREEN_HEIGHT:
        if player_sprite:
            # Draw player sprite centered on tile
            screen.blit(player_sprite_scaled, (player_screen_x, player_screen_y))
        else:
            # Fallback: draw red rectangle
            pygame.draw.rect(screen, COLOR_RED,
                           (player_screen_x, player_screen_y, TILE_SIZE, TILE_SIZE))

def render_win_message():
    """Render win message when player reaches the goal"""
    font = pygame.font.SysFont(None, 36)
    text = font.render("You Win! Press R to restart", True, COLOR_WHITE)
    text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
    screen.blit(text, text_rect)

def move_player(dx, dy):
    """Attempt to move the player, checking for collisions"""
    new_x = player_pos[0] + dx
    new_y = player_pos[1] + dy
    
    # Check boundaries
    if 0 <= new_x < MAP_WIDTH and 0 <= new_y < MAP_HEIGHT:
        # Check if tile is walkable (in movable_ids)
        if wfc_input_array[new_y][new_x] in movable_ids:
            player_pos[0] = new_x
            player_pos[1] = new_y
            update_camera()
            return True
    return False

def update_camera():
    """Center camera on player while keeping within map bounds"""
    global camera_x, camera_y
    camera_x = max(0, min(player_pos[0] - VIEWPORT_TILES_W // 2, MAP_WIDTH - VIEWPORT_TILES_W))
    camera_y = max(0, min(player_pos[1] - VIEWPORT_TILES_H // 2, MAP_HEIGHT - VIEWPORT_TILES_H))

def check_win_condition():
    """Check if player has reached the win position"""
    return player_pos[0] == win_pos[0] and player_pos[1] == win_pos[1]

# Initialize zoom and player sprite
update_zoom(current_zoom)

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if game_won and event.key == pygame.K_r:
                # Reset game
                player_pos = [5, 11]
                update_camera()
                game_won = False
            elif not game_won:
                if event.key == pygame.K_LEFT:
                    move_player(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    move_player(1, 0)
                elif event.key == pygame.K_UP:
                    move_player(0, -1)
                elif event.key == pygame.K_DOWN:
                    move_player(0, 1)
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    update_zoom(current_zoom + 1)
                elif event.key == pygame.K_MINUS:
                    update_zoom(current_zoom - 1)
    
    # Check win condition
    if not game_won and check_win_condition():
        game_won = True
    
    # Render
    screen.fill(COLOR_BLACK)
    render_map()
    render_player()
    
    if game_won:
        render_win_message()
    
    # Display zoom level in corner
    font = pygame.font.SysFont(None, 24)
    zoom_text = font.render(f"Zoom: {ZOOM_LEVELS[current_zoom]}x (Press +/- to adjust)", True, COLOR_WHITE)
    screen.blit(zoom_text, (10, 10))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
