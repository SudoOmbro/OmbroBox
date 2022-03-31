import sys
from typing import List

import pygame
from pygame.locals import *

from world import World, TILES

pygame.init()

FONT = pygame.font.Font('font.otf', 18)

# Game Setup
FPS = 60
fpsClock = pygame.time.Clock()

WINDOW = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
pygame.display.set_caption('OmbroBox')
pygame.display.set_icon(pygame.image.load("icon.png"))


def render(world: World, selected_tile: int):
    pygame.display.set_caption(f'OmbroBox | FPS: {int(fpsClock.get_fps())}')
    surface = pygame.Surface((world.width, world.height))
    for tile in world.tiles:
        surface.set_at((tile.x, tile.y), tile.color)
    scaled_surface = pygame.transform.scale(surface, WINDOW.get_size())
    updates_text = FONT.render(f"world updates: {world.updates}", False, (255, 255, 255))
    tile_text = FONT.render(f"selected tile: {TILES[selected_tile].NAME}", False, (255, 255, 255))
    scaled_surface.blit(tile_text, (10, 10))
    scaled_surface.blit(updates_text, (10, 50))
    WINDOW.blit(scaled_surface, (0, 0))
    pygame.display.flip()
    fpsClock.tick(FPS)


def clamp(n, smallest, largest) -> int:
    ll: List[int] = [smallest, n, largest]
    ll.sort()
    return ll[1]


def add_tile_at_mouse_pos(tile_type: type, world: World):
    window_size = WINDOW.get_size()
    mouse_pos = pygame.mouse.get_pos()
    world.add_tile(
        tile_type,
        clamp(int((mouse_pos[0] / window_size[0]) * world.width), 0, world.width - 1),
        clamp(int((mouse_pos[1] / window_size[1]) * world.height), 0, world.height - 1)
    )


def delete_tile_at_mouse_pos(world: World):
    window_size = WINDOW.get_size()
    mouse_pos = pygame.mouse.get_pos()
    world.delete_tile(
        clamp(int((mouse_pos[0] / window_size[0]) * world.width), 0, world.width - 1),
        clamp(int((mouse_pos[1] / window_size[1]) * world.height), 0, world.height - 1)
    )


def main():
    world = World(160, 90)
    selected_tile: int = 0

    while True:
        # Get inputs
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEWHEEL:
                if event.y == -1:
                    if selected_tile == 0:
                        selected_tile = len(TILES) - 1
                    else:
                        selected_tile -= 1
                else:
                    if selected_tile == len(TILES) - 1:
                        selected_tile = 0
                    else:
                        selected_tile += 1
            if pygame.mouse.get_pressed()[0]:
                add_tile_at_mouse_pos(TILES[selected_tile], world)
            elif pygame.mouse.get_pressed()[2]:
                delete_tile_at_mouse_pos(world)
        # update physics
        world.update()
        # render
        render(world, selected_tile)


if __name__ == '__main__':
    main()
