import pygame
from Config import *


class DrawWorld:

    def __init__(self, world):
        self.font0 = pygame.font.Font(pygame.font.get_default_font(), 14)
        self.font1 = pygame.font.Font(pygame.font.get_default_font(), 11)
        self.font2 = pygame.font.Font(pygame.font.get_default_font(), 8)
        self.spritesheet = pygame.image.load(SPRITESHEET_PATH).convert_alpha()
        self.player_sprite = pygame.image.load(PLAYER_SPRITE_PATH).convert_alpha()
        self.stone_sprite = pygame.image.load(STONE_SPRITE_PATH).convert_alpha()
        self.world = world
        self.worldSurface = pygame.Surface(
            (WORLD_X * TILESIZE * SCALETILE, WORLD_Y * TILESIZE * SCALETILE)
        )
        
        self.COLOR_WALL = (100, 100, 100)    # Dark gray
        self.COLOR_FLOOR = (200, 200, 180)   # Light beige
        self.COLOR_BOX = (200, 120, 50)      # Orange/brown
        self.COLOR_TARGET = (50, 200, 50)    # Green
        self.COLOR_PLAYER = (50, 50, 200)    # Blue
        self.COLOR_ENTROPY = (200, 200, 200) # Light gray

    
    def update(self, show_entropy=False):
        lowest_entropy = self.world.getLowestEntropy()
        for y in range(WORLD_Y):
            for x in range(WORLD_X):
                tile_entropy = self.world.getEntropy(x, y)
                tile_type = self.world.getType(x, y)

                tile_image = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)

                if tile_entropy > 0:
                    # Case: Wall tile during WFC
                    if self.world.wall_mask[y][x]:
                        tile_image.fill(self.COLOR_WALL)
                        if show_entropy:
                            color = "green" if tile_entropy == lowest_entropy else "gray"
                            text = str(tile_entropy)
                            text_surface = self.font0.render(text, True, color)  # White text
                            tile_image.blit(text_surface, (3, 1))

                    # Case: Floor path tile during WFC
                    elif self.world.floor_mask[y][x]:
                        tile_image.fill(self.COLOR_FLOOR)
                    
                    elif self.world.target_mask[y][x]:
                        tile_image.fill(self.COLOR_TARGET)
                    
                    elif self.world.box_mask[y][x]:
                        tile_image.fill(self.COLOR_BOX)
                    
                    elif self.world.player_mask[y][x]:
                        tile_image.fill(self.COLOR_PLAYER)

                # Case: Collapsed tile — draw sprite
                else:
                    if tile_type in tileSprites:
                        pos = tileSprites[tile_type]
                        sprite = self.spritesheet.subsurface(pygame.Rect(pos[0], pos[1], TILESIZE, TILESIZE))
                        tile_image.blit(sprite, (0, 0))
                    elif tile_type == STONE_TILE:
                        # Stone Tile and Player tile are 16 x 16 pixels in default
                        stone_scaled = pygame.transform.scale_by(self.stone_sprite, (1, 1))
                        tile_image.blit(stone_scaled, (0, 0))
                    elif tile_type == PLAYER_TILE:
                        player_scaled = pygame.transform.scale_by(self.player_sprite, (1, 1))
                        tile_image.blit(player_scaled, (0, 0))

                    # Case: Error fallback
                    else:
                        tile_image.fill((255, 0, 255))  # Magenta

                tile_image = pygame.transform.scale_by(tile_image, (SCALETILE, SCALETILE))
                self.worldSurface.blit(tile_image, (x * TILESIZE * SCALETILE, y * TILESIZE * SCALETILE))

        
    def draw(self, displaySurface):
        displaySurface.blit(self.worldSurface, (0, 0))
