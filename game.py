import sys
from typing import List, Tuple

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


def render(world: World, selected_tile: int, mouse_position: Tuple[int, int]):
    pygame.display.set_caption(f'OmbroBox | FPS: {int(fpsClock.get_fps())}')
    surface = pygame.Surface((world.width, world.height))
    for tile in world.tiles:
        surface.set_at((tile.x, tile.y), tile.color)
    surface.set_at(mouse_position, (255, 255, 255))
    scaled_surface = pygame.transform.scale(surface, WINDOW.get_size())
    updates_text = FONT.render(f"world updates: {world.updates}", False, (255, 255, 255))
    tile_text = FONT.render(f"selected tile: {TILES[selected_tile].NAME}", False, (255, 255, 255))
    total_particles_text = FONT.render(f"Total tiles: {len(world.tiles)}", False, (255, 255, 255))
    scaled_surface.blit(tile_text, (10, 10))
    scaled_surface.blit(updates_text, (10, 50))
    scaled_surface.blit(total_particles_text, (10, 90))
    WINDOW.blit(scaled_surface, (0, 0))
    pygame.display.flip()
    fpsClock.tick(FPS)


def clamp(n, smallest, largest) -> int:
    ll: List[int] = [smallest, n, largest]
    ll.sort()
    return ll[1]


def get_mouse_world_position(world: World) -> Tuple[int, int]:
    window_size = WINDOW.get_size()
    mouse_pos = pygame.mouse.get_pos()
    mouse_x = clamp(int((mouse_pos[0] / window_size[0]) * world.width), 0, world.width - 1)
    mouse_y = clamp(int((mouse_pos[1] / window_size[1]) * world.height), 0, world.height - 1)
    return mouse_x, mouse_y


def main():
    world = World(160, 90)
    selected_tile: int = 0

    while True:
        # Get mouse position
        mouse_position = get_mouse_world_position(world)
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
            world.add_tile(TILES[selected_tile], mouse_position[0], mouse_position[1])
        elif pygame.mouse.get_pressed()[2]:
            world.delete_tile(mouse_position[0], mouse_position[1])
        # update physics
        world.update()
        # render
        render(world, selected_tile, mouse_position)


if __name__ == '__main__':
    main()
