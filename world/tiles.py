from typing import List, Type

from world.world import Tile, GasTile, World, LiquidTile, SemiSolidTile, SolidTile, ChaosTile, CustomTile, Dir
from world.semirandom import randint

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
            (140 + randint(40), 140 + randint(40), 140 + randint(40)),
            100000,
            world,
            x,
            y
        )


@add_to_tile_list
class WoodTile(SolidTile):

    NAME = "Wood"
    UPPER_HEATH_THRESHOLD = 500, "BurningWood"

    def __init__(self, world: World, x: int, y: int):
        super().__init__(
            (117 + randint(40), 63 + randint(40), 4 + randint(40)),
            100000,
            world,
            x,
            y,
            heat_transfer_coefficient=0.01
        )


@add_to_tile_list
class BurningWood(SolidTile):

    NAME = "Burning Wood"
    UPPER_HEATH_THRESHOLD = 2000, "AshTile"
    LOWER_HEATH_THRESHOLD = 90, WoodTile

    def __init__(self, world: World, x: int, y: int):
        super().__init__(
            (209 + randint(40), 118 + randint(40), 4),
            100000,
            world,
            x,
            y,
            base_heat=500,
            heat_transfer_coefficient=1,
            passive_heat_loss=-5
        )


@add_to_tile_list
class GlassTile(SolidTile):

    NAME = "Glass"

    def __init__(self, world: World, x: int, y: int):
        super().__init__(
            (152 + randint(40), 203 + randint(40), 206 + randint(40)),
            100000,
            world,
            x,
            y,
            heat_transfer_coefficient=0.5
        )


# Semi solid tiles --------------------


@add_to_tile_list
class SandTile(SemiSolidTile):

    NAME = "Sand"
    UPPER_HEATH_THRESHOLD = 800, GlassTile

    def __init__(self, world: World, x: int, y: int):
        super().__init__(
            (205-randint(50), 205-randint(50), 0),
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
            (40-randint(10), 40-randint(10), 50-randint(10)),
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
            (200-randint(20), 200-randint(20), 255-randint(20)),
            1,
            world,
            x,
            y,
            base_heat=-40,
        )


@add_to_tile_list
class AshTile(SemiSolidTile):

    NAME = "Ash"

    def __init__(self, world: World, x: int, y: int):
        super().__init__(
            (140-randint(20), 140-randint(20), 140-randint(20)),
            1,
            world,
            x,
            y,
            base_heat=100,
        )


# Liquid tiles -------------------

@add_to_tile_list
class WaterTile(LiquidTile):

    NAME = "Water"
    UPPER_HEATH_THRESHOLD = 100, "VaporTile"
    LOWER_HEATH_THRESHOLD = 0, IceTile

    def __init__(self, world: World, x: int, y: int):
        super().__init__(
            (0, 0, 155+randint(100)),
            2,
            world,
            x,
            y,
        )


@add_to_tile_list
class OilTile(LiquidTile):

    NAME = "Oil"
    UPPER_HEATH_THRESHOLD = 300, "FireTile"

    def __init__(self, world: World, x: int, y: int):
        super().__init__(
            (193-randint(20), 193-randint(20), 69-randint(10)),
            1,
            world,
            x,
            y,
            base_heat=25,
        )


@add_to_tile_list
class LavaTile(LiquidTile):

    NAME = "Lava"
    LOWER_HEATH_THRESHOLD = 500, RockTile

    def __init__(self, world: World, x: int, y: int):
        super().__init__(
            (255 - randint(20), 0, 0),
            1000,
            world,
            x,
            y,
            base_heat=10000,
            heat_transfer_coefficient=0.1
        )


@add_to_tile_list
class LiquidNitrogen(LiquidTile):

    NAME = "Liquid Nitrogen"
    UPPER_HEATH_THRESHOLD = 0, None

    def __init__(self, world: World, x: int, y: int):
        super().__init__(
            (255, 255, 255),
            0,
            world,
            x,
            y,
            base_heat=-10000,
        )


# Gas tiles -----------------

@add_to_tile_list
class VaporTile(GasTile):

    NAME = "Vapor"
    LOWER_HEATH_THRESHOLD = 60, WaterTile

    def __init__(self, world: World, x: int, y: int):
        super().__init__(
            (255-randint(20), 255-randint(20), 255-randint(20)),
            0,
            world,
            x,
            y,
            base_heat=220 + randint(120),
            passive_heat_loss=1
        )


@add_to_tile_list
class SmokeTile(GasTile):

    NAME = "Smoke"
    LOWER_HEATH_THRESHOLD = 100, None

    def __init__(self, world: World, x: int, y: int):
        super().__init__(
            (50-randint(20), 50-randint(20), 50-randint(20)),
            0,
            world,
            x,
            y,
            base_heat=220 + randint(120),
        )


# Chaos tiles -------------------

@add_to_tile_list
class FireTile(ChaosTile):

    NAME = "Fire"
    LOWER_HEATH_THRESHOLD = 100, SmokeTile

    def __init__(self, world: World, x: int, y: int):
        super().__init__(
            (242-randint(20), 141-randint(20), 0),
            0,
            world,
            x,
            y,
            base_heat=1000,
            passive_heat_loss=1,
            heat_transfer_coefficient=1
        )


@add_to_tile_list
class GreyGooTile(CustomTile):

    NAME = "Grey Goo"

    def __init__(self, world: World, x: int, y: int):
        super().__init__(
            (180, 180, 180),
            0,
            world,
            x,
            y
        )

    def custom_update(self):
        for direction in Dir.ALL:
            tile: Tile = self.get_neighbour_tile(direction)
            if tile and (type(tile) != GreyGooTile):
                tile.transform(GreyGooTile)


# This is needed as a workaround of Python's lack of forward declaration
for tile_to_fix in TILES:
    if "UPPER_HEATH_THRESHOLD" in tile_to_fix.__dict__:
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
