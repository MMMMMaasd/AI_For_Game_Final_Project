import pygame
from Config import *


class DrawWorld:

    def __init__(self, world):
        self.font0 = pygame.font.Font(pygame.font.get_default_font(), 14)
        self.font1 = pygame.font.Font(pygame.font.get_default_font(), 11)
        self.font2 = pygame.font.Font(pygame.font.get_default_font(), 8)
        self.spritesheet = pygame.image.load(SPRITESHEET_PATH).convert_alpha()
        self.world = world
        self.worldSurface = pygame.Surface(
            (WORLD_X * TILESIZE * SCALETILE, WORLD_Y * TILESIZE * SCALETILE)
        )

    def update(self):
        lowest_entropy = self.world.getLowestEntropy()

        for y in range(WORLD_Y):
            for x in range(WORLD_X):
                tile_entropy = self.world.getEntropy(x, y)
                tile_type = self.world.getType(x, y)

                print(tile_type, tile_entropy)
                # Tile not collapsed — show entropy
                if tile_entropy > 0:
                    tile_image = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)
                    if tile_entropy == 27:
                        textSurface = self.font2.render(str(tile_entropy), True, "darkgrey")
                        tile_image.blit(textSurface, (3, 3))
                    elif tile_entropy >= 10:
                        textSurface = self.font1.render(str(tile_entropy), True, "grey")
                        tile_image.blit(textSurface, (2, 3))
                    else:
                        color = "green" if tile_entropy == lowest_entropy else "white"
                        textSurface = self.font0.render(str(tile_entropy), True, color)
                        tile_image.blit(textSurface, (4, 1))

                # Tile collapsed — draw final tile
                elif tile_type in tileSprites:
                    # For forest tiles, draw a grass base layer first
                    tile_image = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)
                    
                   # if tile_type >= TILE_FORESTN:
                   #     grass_pos = tileSprites[TILE_GRASS]
                   #     grass_img = self.spritesheet.subsurface(
                   #         pygame.Rect(grass_pos[0], grass_pos[1], TILESIZE, TILESIZE)
                   #     )
                   #     tile_image.blit(grass_img, (0, 0))
                        
                    pos = tileSprites[tile_type]
                    sprite = self.spritesheet.subsurface(pygame.Rect(pos[0], pos[1], TILESIZE, TILESIZE))
                    tile_image.blit(sprite, (0, 0))

                else:
                    # Unknown tile or not in tileSprites — fallback
                    tile_image = pygame.Surface((TILESIZE, TILESIZE))
                    tile_image.fill((255, 0, 255))  # magenta as error color

                # Scale and blit to worldSurface
                tile_image = pygame.transform.scale_by(tile_image, (SCALETILE, SCALETILE))
                self.worldSurface.blit(
                    tile_image,
                    (x * TILESIZE * SCALETILE, y * TILESIZE * SCALETILE)
                )

    def draw(self, displaySurface):
        displaySurface.blit(self.worldSurface, (0, 0))
