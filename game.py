import sys
from typing import List, Tuple

import pygame
from pygame.locals import *

from world.world import World, Dir, HeatTile
from world.tiles import TILES

"""
All PyGame stuff is here (rendering & inputs)
"""

pygame.init()

FONT = pygame.font.Font('font.otf', 18)
SMALL_FONT = pygame.font.Font('font.otf', 14)

# Game Setup
FPS = 60
fpsClock = pygame.time.Clock()
WINDOW = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
pygame.display.set_caption('OmbroBox')
pygame.display.set_icon(pygame.image.load("icon.png"))

paused_text = FONT.render("Simulation paused", False, (255, 255, 255))


def render(world: World, selected_tile: int, mouse_position: Tuple[int, int], paused: bool, tiles_info: bool):
    # set window caption (show FPS)
    pygame.display.set_caption(f'OmbroBox | FPS: {int(fpsClock.get_fps())}')
    # render world
    surface = pygame.Surface((world.width, world.height))
    for tile in world.tiles:
        surface.set_at((tile.x, tile.y), tile.color)
    surface.set_at(mouse_position, (255, 255, 255))
    scaled_surface = pygame.transform.scale(surface, WINDOW.get_size())
    # render selected tile
    tile_text = FONT.render(
        f"selected ({selected_tile + 1}/{len(TILES)}): {TILES[selected_tile].NAME}",
        False,
        (255, 255, 255)
    )
    scaled_surface.blit(tile_text, (10, 10))
    # render additional information if tiles info is on
    if tiles_info:
        total_particles_text = FONT.render(f"Total tiles: {len(world.tiles)}", False, (255, 255, 255))
        scaled_surface.blit(total_particles_text, (10, 50))
        tile = world.space_matrix[mouse_position[1]][mouse_position[0]]
        if tile:
            mouse_pos = pygame.mouse.get_pos()
            tile_type_text = SMALL_FONT.render(
                f"Type: {tile.NAME}",
                False,
                (255, 255, 255)
            )
            tile_type_text_shadow = SMALL_FONT.render(
                f"Type: {tile.NAME}",
                False,
                (0, 0, 0)
            )
            scaled_surface.blit(tile_type_text_shadow, (mouse_pos[0] + 12, mouse_pos[1] + 2))
            scaled_surface.blit(tile_type_text, (mouse_pos[0] + 10, mouse_pos[1]))
            if "heat" in tile.__dict__:
                tile_heat_text = SMALL_FONT.render(
                    f"Heat: {tile.heat}",
                    False,
                    (255, 255, 255)
                )
                tile_heat_text_shadow = SMALL_FONT.render(
                    f"Heat: {tile.heat}",
                    False,
                    (0, 0, 0)
                )
                scaled_surface.blit(tile_heat_text_shadow, (mouse_pos[0] + 12, mouse_pos[1] + 22))
                scaled_surface.blit(tile_heat_text, (mouse_pos[0] + 10, mouse_pos[1] + 20))
    # render pause text if the simulation is paused
    if paused:
        scaled_surface.blit(paused_text, (WINDOW.get_width() - paused_text.get_width() - 10, 10))
    # render surface to window
    WINDOW.blit(scaled_surface, (0, 0))
    pygame.display.flip()


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
    pause: bool = False
    tiles_info: bool = False

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
            if event.type == KEYDOWN:
                if event.unicode == " ":
                    pause = not pause
                elif event.scancode == 58:
                    # Press F1
                    tiles_info = not tiles_info
                elif event.scancode == 41:
                    # Press ESC
                    world = World(160, 90)
        if pygame.mouse.get_pressed()[0]:
            world.add_tile(TILES[selected_tile], mouse_position[0], mouse_position[1])
            if pygame.key.get_pressed()[K_LCTRL]:
                for direction in Dir.ALL:
                    world.add_tile(
                        TILES[selected_tile],
                        mouse_position[0] + direction[0],
                        mouse_position[1] + direction[1]
                    )
        elif pygame.mouse.get_pressed()[2]:
            world.delete_tile(mouse_position[0], mouse_position[1])
            if pygame.key.get_pressed()[K_LCTRL]:
                for direction in Dir.ALL:
                    world.delete_tile(
                        mouse_position[0] + direction[0],
                        mouse_position[1] + direction[1]
                    )
        # update physics
        if not pause:
            world.update()
        # render
        render(world, selected_tile, mouse_position, pause, tiles_info)
        fpsClock.tick(FPS)


if __name__ == '__main__':
    main()
