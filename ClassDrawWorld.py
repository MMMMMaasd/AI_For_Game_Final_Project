import pygame
from Config import *

class DrawWorld:

    def __init__(self, world, player_sprite, hole_sprite, stone_sprite):
        self.TILESIZE = 16
        self.SCALETILE = 2
        self.font0 = pygame.font.Font(pygame.font.get_default_font(), 14)
        self.font1 = pygame.font.Font(pygame.font.get_default_font(), 11)
        self.font2 = pygame.font.Font(pygame.font.get_default_font(), 8)
        self.spritesheet = pygame.image.load(SPRITESHEET_PATH).convert_alpha()

        self.player_sprite = player_sprite
        self.hole_sprite = hole_sprite
        self.stone_sprite = stone_sprite

        self.world = world
        self.worldSurface = pygame.Surface(
            (WORLD_X * self.TILESIZE * self.SCALETILE, WORLD_Y * self.TILESIZE * self.SCALETILE)
        )

    def update(self):
        lowest_entropy = self.world.getLowestEntropy()

        for y in range(WORLD_Y):
            for x in range(WORLD_X):
                tile_entropy = self.world.getEntropy(x, y)
                tile_type = self.world.getType(x, y)

                rect = pygame.Rect(
                    x * self.TILESIZE * self.SCALETILE,
                    y * self.TILESIZE * self.SCALETILE,
                    self.TILESIZE * self.SCALETILE,
                    self.TILESIZE * self.SCALETILE
                )

                if tile_entropy > 0:
                    tile_image = pygame.Surface((self.TILESIZE, self.TILESIZE), pygame.SRCALPHA)

                    # === Background based on maze grid ===
                    if self.world.maze_tile_grid is not None:
                        maze_value = self.world.maze_tile_grid[y][x]

                        if maze_value == 1 or maze_value == 4:
                            tile_image.fill((255, 255, 150))  # yellow for solution path
                        else:
                            tile_image.fill((230, 230, 230))  # light gray for others
                    else:
                        tile_image.fill((230, 230, 230))  # light gray fallback

                    # === Draw entropy number
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


                else:
                    # Collapsed tile — draw final sprite
                    tile_image = pygame.Surface((self.TILESIZE, self.TILESIZE), pygame.SRCALPHA)

                    if tile_type == TILE_PLAYER:
                        tile_image.blit(self.player_sprite, (0, 0))
                    elif tile_type == TILE_GRASS_HOLE:
                        tile_image.blit(self.hole_sprite, (0, 0))
                    elif tile_type == TILE_GRASS_STONE:
                        tile_image.blit(self.stone_sprite, (0, 0))
                    elif tile_type in tileSprites:
                        pos = tileSprites[tile_type]
                        sprite = self.spritesheet.subsurface(
                            pygame.Rect(pos[0], pos[1], self.TILESIZE, self.TILESIZE)
                        )
                        tile_image.blit(sprite, (0, 0))
                    else:
                        # Unknown tile — fallback
                        tile_image.fill((255, 0, 255))  # magenta for error

                # Scale and blit to worldSurface
                tile_image = pygame.transform.scale_by(tile_image, (self.SCALETILE, self.SCALETILE))
                self.worldSurface.blit(tile_image, (x * self.TILESIZE * self.SCALETILE, y * self.TILESIZE * self.SCALETILE))

    def draw(self, displaySurface):
        displaySurface.blit(self.worldSurface, (0, 0))
