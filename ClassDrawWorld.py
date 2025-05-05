import pygame
import Config

class DrawWorld:
    def __init__(self, world):
        self.world = world
        self.font_entropy = pygame.font.Font(None, 11)
        self.font_debug   = pygame.font.Font(None, 9)

        self.spritesheets = {}
        self.sprites      = {}

        try:
            self.spritesheets['forest'] = pygame.image.load(Config.SPRITESHEET_PATH).convert_alpha()
        except:
            self.spritesheets['forest'] = None

        try:
            self.spritesheets['tanibo'] = pygame.image.load(Config.TANIBO_SPRITESHEET_PATH).convert_alpha()
        except:
            self.spritesheets['tanibo'] = None

        try:
            self.sprites['stone']  = pygame.image.load(Config.STONE_SPRITE_PATH).convert_alpha()
        except:
            self.sprites['stone']  = None

        self.worldSurface = pygame.Surface(
            (Config.WORLD_X * Config.TILESIZE * Config.SCALETILE,
             Config.WORLD_Y * Config.TILESIZE * Config.SCALETILE)
        )

        self.COLOR_ENTROPY_LOW  = (0,255,0)
        self.COLOR_ENTROPY_HIGH = (200,200,200)
        self.COLOR_CONTRADICTION= (255,0,0)
        self.COLOR_PATH        = (255,255,0,100)
        self.COLOR_SOKO        = (0,0,255,60)
        self.COLOR_REGION = (255, 0, 0, 128)
        self.COLOR_BOUNDARY = (0, 0, 255, 160)

    def update(self, show_entropy=False, highlight_path=None, highlight_sokoban=None, highlight_regions=None):
        self.worldSurface.fill((0,0,0,0))
        lowest = float('inf')
        if show_entropy:
            for r in range(self.world.rows):
                for c in range(self.world.cols):
                    t = self.world.get_tile(c,r)
                    if t and t.entropy>0:
                        lowest = min(lowest, t.entropy)

        path_surf = pygame.Surface(self.worldSurface.get_size(), pygame.SRCALPHA)
        soko_surf = pygame.Surface(self.worldSurface.get_size(), pygame.SRCALPHA)
        region_surf = pygame.Surface(self.worldSurface.get_size(), pygame.SRCALPHA)
        boundary_surf = pygame.Surface(self.worldSurface.get_size(), pygame.SRCALPHA)
        if highlight_regions:
            for region in highlight_regions:
                for r, c in region['open_tiles']:
                    rect = pygame.Rect(
                        c*Config.TILESIZE*Config.SCALETILE,
                        r*Config.TILESIZE*Config.SCALETILE,
                        Config.TILESIZE*Config.SCALETILE,
                        Config.TILESIZE*Config.SCALETILE
                    )
                    pygame.draw.rect(region_surf, self.COLOR_REGION, rect)
                
                # Draw boundaries (blue)
                for r, c in region['boundaries']:
                    rect = pygame.Rect(
                        c*Config.TILESIZE*Config.SCALETILE,
                        r*Config.TILESIZE*Config.SCALETILE,
                        Config.TILESIZE*Config.SCALETILE,
                        Config.TILESIZE*Config.SCALETILE
                    )
                    pygame.draw.rect(boundary_surf, self.COLOR_BOUNDARY, rect)
                        
        if highlight_path:
            for r,c in highlight_path:
                rect = pygame.Rect(c*Config.TILESIZE*Config.SCALETILE,
                                   r*Config.TILESIZE*Config.SCALETILE,
                                   Config.TILESIZE*Config.SCALETILE,
                                   Config.TILESIZE*Config.SCALETILE)
                pygame.draw.rect(path_surf, self.COLOR_PATH, rect)

        if highlight_sokoban:
            for c,r in highlight_sokoban:
                rect = pygame.Rect(c*Config.TILESIZE*Config.SCALETILE,
                                   r*Config.TILESIZE*Config.SCALETILE,
                                   Config.TILESIZE*Config.SCALETILE,
                                   Config.TILESIZE*Config.SCALETILE)
                pygame.draw.rect(soko_surf, self.COLOR_SOKO, rect)

        for r in range(self.world.rows):
            for c in range(self.world.cols):
                t = self.world.get_tile(c,r)
                if not t: continue

                dest = pygame.Rect(c*Config.TILESIZE*Config.SCALETILE,
                                   r*Config.TILESIZE*Config.SCALETILE,
                                   Config.TILESIZE*Config.SCALETILE,
                                   Config.TILESIZE*Config.SCALETILE)

                tile_img = pygame.Surface((Config.TILESIZE, Config.TILESIZE), pygame.SRCALPHA)
                tile_img.fill((0,0,0,0))

                if t.entropy>0:
                    if show_entropy:
                        col = self.COLOR_ENTROPY_LOW if t.entropy==lowest else self.COLOR_ENTROPY_HIGH
                        txt = self.font_entropy.render(str(t.entropy), True, col)
                        tile_img.blit(txt, txt.get_rect(center=(Config.TILESIZE//2,Config.TILESIZE//2)))
                elif not t.possibilities:
                    tile_img.fill(self.COLOR_CONTRADICTION)
                else:
                    tid = t.possibilities[0]
                    if tid in Config.tile_sprites:
                        sheet, sx, sy = Config.tile_sprites[tid]
                        if sheet in self.spritesheets and self.spritesheets[sheet]:
                            src = pygame.Rect(sx, sy, Config.TILESIZE, Config.TILESIZE)
                            tile_img.blit(self.spritesheets[sheet], (0,0), src)
                        elif sheet in self.sprites and self.sprites[sheet]:
                            tile_img.blit(self.sprites[sheet], (0,0))
                        else:
                            tile_img.fill((255,0,255))
                            d = self.font_debug.render("?",True,(0,0,0))
                            tile_img.blit(d,(1,1))
                    else:
                        tile_img.fill((255,165,0))
                        d = self.font_debug.render(str(tid%100),True,(0,0,0))
                        tile_img.blit(d,(1,1))

                scaled = pygame.transform.scale(tile_img, (dest.width,dest.height))
                self.worldSurface.blit(scaled, dest)

        self.worldSurface.blit(region_surf, (0, 0))
        self.worldSurface.blit(boundary_surf, (0,0))
        self.worldSurface.blit(path_surf, (0,0))
        self.worldSurface.blit(soko_surf, (0,0))

    def draw(self, displaySurface):
        displaySurface.blit(self.worldSurface, (0,0))
