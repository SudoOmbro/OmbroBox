from random import randint
from typing import List, Type

from world.world import Tile, GasTile, World, LiquidTile, SemiSolidTile, SolidTile

TILES: List[Type[Tile]] = []
_TILES_TO_FIX: List[Type[Tile]] = []


def add_to_tile_list(tile: Type[Tile]) -> Type[Tile]:
    TILES.append(tile)
    print(f"Added tile {tile.NAME}")
    return tile


# Solid tiles ----------------------

@add_to_tile_list
class ConcreteTile(SolidTile):

    NAME = "Concrete"

    def __init__(self, world: World, x: int, y: int):
        super().__init__(
            (160 + randint(-20, 20), 160 + randint(-20, 20), 160 + randint(-20, 20)),
            100000,
            world,
            x,
            y,
            base_heat=25,
            heat_transfer_coefficient=1
        )


# Semi solid tiles --------------------


@add_to_tile_list
class SandTile(SemiSolidTile):

    NAME = "Sand"

    def __init__(self, world: World, x: int, y: int):
        super().__init__(
            (255-randint(0, 50), 255-randint(0, 50), 0),
            10,
            world,
            x,
            y,
            heat_transfer_coefficient=0.05
        )


@add_to_tile_list
class RockTile(SemiSolidTile):

    NAME = "Rock"
    UPPER_HEATH_THRESHOLD = 1000, "LavaTile"

    def __init__(self, world: World, x: int, y: int):
        super().__init__(
            (50-randint(0, 10), 50-randint(0, 10), 50-randint(0, 10)),
            800,
            world,
            x,
            y
        )


@add_to_tile_list
class IceTile(SemiSolidTile):

    NAME = "Ice"
    UPPER_HEATH_THRESHOLD = 0, "WaterTile"

    def __init__(self, world: World, x: int, y: int):
        super().__init__(
            (200-randint(0, 20), 200-randint(0, 20), 255-randint(0, 20)),
            1,
            world,
            x,
            y,
            base_heat=-40,
            heat_transfer_coefficient=1
        )


@add_to_tile_list
class AshTile(SemiSolidTile):

    NAME = "Ash"
    UPPER_HEATH_THRESHOLD = 500, "FireTile"

    def __init__(self, world: World, x: int, y: int):
        super().__init__(
            (140-randint(0, 20), 140-randint(0, 20), 140-randint(0, 20)),
            1,
            world,
            x,
            y,
            base_heat=100,
            heat_transfer_coefficient=1
        )


# Liquid tiles -------------------

@add_to_tile_list
class WaterTile(LiquidTile):

    NAME = "Water"
    UPPER_HEATH_THRESHOLD = 100, "VaporTile"
    LOWER_HEATH_THRESHOLD = 0, IceTile

    def __init__(self, world: World, x: int, y: int):
        super().__init__(
            (0, 0, 255-randint(0, 100)),
            2,
            world,
            x,
            y,
            base_heat=25,
            heat_transfer_coefficient=1
        )


@add_to_tile_list
class OilTile(LiquidTile):

    NAME = "Oil"
    UPPER_HEATH_THRESHOLD = 300, "FireTile"

    def __init__(self, world: World, x: int, y: int):
        super().__init__(
            (193-randint(0, 20), 193-randint(0, 20), 69-randint(0, 10)),
            1,
            world,
            x,
            y,
            base_heat=25,
            heat_transfer_coefficient=2
        )


@add_to_tile_list
class LavaTile(LiquidTile):

    NAME = "Lava"
    LOWER_HEATH_THRESHOLD = 100, RockTile

    def __init__(self, world: World, x: int, y: int):
        super().__init__(
            (255 - randint(0, 20), 0, 0),
            1000,
            world,
            x,
            y,
            base_heat=2000,
            heat_transfer_coefficient=0.1
        )


@add_to_tile_list
class LiquidNitrogen(LiquidTile):

    NAME = "Liquid Nitrogen"

    def __init__(self, world: World, x: int, y: int):
        super().__init__(
            (255, 255, 255),
            1000,
            world,
            x,
            y,
            base_heat=-2000,
            heat_transfer_coefficient=0
        )


# Gas tiles -----------------

@add_to_tile_list
class VaporTile(GasTile):

    NAME = "Vapor"
    LOWER_HEATH_THRESHOLD = 60, WaterTile

    def __init__(self, world: World, x: int, y: int):
        super().__init__(
            (255-randint(0, 20), 255-randint(0, 20), 255-randint(0, 20)),
            0,
            world,
            x,
            y,
            base_heat=randint(220, 340),
            heat_transfer_coefficient=1,
            passive_heat_loss=1
        )


@add_to_tile_list
class SmokeTile(GasTile):

    NAME = "Smoke"
    LOWER_HEATH_THRESHOLD = 100, AshTile

    def __init__(self, world: World, x: int, y: int):
        super().__init__(
            (50-randint(0, 20), 50-randint(0, 20), 50-randint(0, 20)),
            0,
            world,
            x,
            y,
            base_heat=randint(220, 340),
            heat_transfer_coefficient=1,
        )


@add_to_tile_list
class FireTile(GasTile):

    NAME = "Fire"
    LOWER_HEATH_THRESHOLD = 100, SmokeTile

    def __init__(self, world: World, x: int, y: int):
        super().__init__(
            (242-randint(0, 20), 141-randint(0, 20), 0),
            0,
            world,
            x,
            y,
            base_heat=600,
            heat_transfer_coefficient=1,
            passive_heat_loss=1
        )


# THE HACK OF THE CENTURY, FUCK YOU AND YOUR LACK OF FORWARD DECLARATIONS
for tile_to_fix in TILES:
    if tile_to_fix.UPPER_HEATH_THRESHOLD:
        if type(tile_to_fix.UPPER_HEATH_THRESHOLD[1]) == str:
            print(f"fixing {tile_to_fix.UPPER_HEATH_THRESHOLD[1]}")
            tile_to_fix.UPPER_HEATH_THRESHOLD = \
                tile_to_fix.UPPER_HEATH_THRESHOLD[0], \
                globals()[tile_to_fix.UPPER_HEATH_THRESHOLD[1]]
    if tile_to_fix.LOWER_HEATH_THRESHOLD:
        if type(tile_to_fix.LOWER_HEATH_THRESHOLD[1]) == str:
            print(f"fixing {tile_to_fix.LOWER_HEATH_THRESHOLD[1]}")
            tile_to_fix.LOWER_HEATH_THRESHOLD = \
                tile_to_fix.LOWER_HEATH_THRESHOLD[0], \
                globals()[tile_to_fix.LOWER_HEATH_THRESHOLD[1]]
