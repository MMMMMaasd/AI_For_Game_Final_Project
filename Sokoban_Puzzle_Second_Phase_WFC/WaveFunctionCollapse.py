import pygame
from ClassWorld import World
from ClassDrawWorld import DrawWorld
from Config import *

# INTERACTIVE = True
INTERACTIVE = True
INTERACTIVE_KEYPRESS = False

pygame.init()
clock = pygame.time.Clock()

displaySurface = pygame.display.set_mode((WORLD_X * TILESIZE * SCALETILE, WORLD_Y * TILESIZE * SCALETILE))
pygame.display.set_caption("Wave Function Collapse")

world = World(WORLD_X, WORLD_Y)
drawWorld = DrawWorld(world)

done = False

if not INTERACTIVE:
    while not done:
        result = world.waveFunctionCollapse()
        if result == 0:
            done = True

    print("\nGenerated tile type map:")
    for y in range(WORLD_Y):
        row = []
        for x in range(WORLD_X):
            row.append(str(world.getType(x, y)))
        print(" ".join(row))

drawWorld.update()
isRunning = True

while isRunning:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                isRunning = False
            if event.key == pygame.K_SPACE:
                if INTERACTIVE and INTERACTIVE_KEYPRESS:
                    world.waveFunctionCollapse()
                    drawWorld.update()

    if INTERACTIVE and not INTERACTIVE_KEYPRESS:
        if not done:
            result = world.waveFunctionCollapse()
            if result == 0:
                done = True
        drawWorld.update()

    drawWorld.draw(displaySurface)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
