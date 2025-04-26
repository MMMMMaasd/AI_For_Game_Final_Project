import pygame
import sys
import os

# === CONFIG ===
# SPRITESHEET = "Tanibo_tileset.png"
SPRITESHEET = "tileset_forest.png"
TILESIZE    = 16

# --- Init Pygame & compute scaling ---
pygame.init()
info   = pygame.display.Info()
# load sheet (no convert yet)
raw_sheet = pygame.image.load(os.path.join(os.path.dirname(__file__), SPRITESHEET))
w_full, h_full = raw_sheet.get_size()

# figure out scale so it never exceeds 80% of your screen
max_w  = int(info.current_w * 0.8)
max_h  = int(info.current_h * 0.8)
scale  = min(max_w / w_full, max_h / h_full, 1.0)
w_disp = int(w_full * scale)
h_disp = int(h_full * scale)

# now set the video mode
screen = pygame.display.set_mode((w_disp, h_disp))
pygame.display.set_caption("Click a tile → prints ID (ESC to quit)")

# only *after* display is set can we convert surfaces
sheet      = raw_sheet.convert_alpha()
sheet_disp = pygame.transform.smoothscale(sheet, (w_disp, h_disp))

cols = w_full // TILESIZE
font = pygame.font.SysFont(None, 18)

# draw initial
screen.blit(sheet_disp, (0,0))
pygame.display.flip()

# --- Main loop ---
while True:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()

        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            mx, my = ev.pos
            # map back to original coords
            ox = int(mx/scale)
            oy = int(my/scale)
            tx = ox // TILESIZE
            ty = oy // TILESIZE
            tid = ty*cols + tx

            print(f"Display=({mx},{my}) → Orig=({ox},{oy}) → Tile=({tx},{ty}) → ID={tid}")

            screen.blit(sheet_disp, (0,0))
            hl = pygame.Surface((int(TILESIZE*scale), int(TILESIZE*scale)), pygame.SRCALPHA)
            hl.fill((255,0,0,100))
            screen.blit(hl, (tx*TILESIZE*scale, ty*TILESIZE*scale))
            txt = font.render(f"ID={tid}", True, (255,255,255))
            screen.blit(txt, (5, h_disp - 20))
            pygame.display.flip()
