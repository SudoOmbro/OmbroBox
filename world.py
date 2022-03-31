import random
from typing import Tuple, List


class Tile:

    NAME: str
    MAX_SKIP: int = 60

    def __init__(self, color: Tuple[int, int, int], density: int, world: "World", x: int, y: int):
        self.color = color
        self.density = density
        self.x = x
        self.y = y
        self.world = world
        self.max_skip_update: int = 0
        self.skip_update: int = 0

    def get_tile(self, x: int, y: int) -> "Tile" or None:
        return self.world.matrix[y][x]

    def move(self, new_x: int, new_y: int, replacement_tile: "Tile" or None = None):
        self.world.matrix[self.y][self.x] = replacement_tile
        self.x = new_x
        self.y = new_y
        self.world.matrix[self.y][self.x] = self

    def try_move(self, x_delta: int, y_delta: int) -> bool:
        next_x: int = self.x + x_delta
        if (next_x < 0) or (next_x >= self.world.width):
            return False
        next_y: int = self.y + y_delta
        if (next_y < 0) or (next_y >= self.world.height):
            return False
        checked_tile = self.get_tile(next_x, next_y)
        if not checked_tile:
            self.move(next_x, next_y)
            return True
        elif checked_tile.density < self.density:
            checked_tile.x = self.x
            checked_tile.y = self.y
            self.move(next_x, next_y, replacement_tile=checked_tile)
            return True
        return False

    def do_update(self):
        if self.skip_update != 0:
            self.skip_update -= 1
            return False
        if self.update():
            self.max_skip_update = 0
            self.skip_update = 0
        else:
            self.max_skip_update += 1 if self.max_skip_update != self.MAX_SKIP else 0
            self.skip_update = self.max_skip_update
        return True

    def update(self) -> bool:
        raise NotImplemented


class World:

    def __init__(self, width: int, height: int):
        self.updates: int = 0
        self.width = width
        self.height = height
        self.tiles: List[Tile] = []
        # init world matrix
        self.matrix: List[List[Tile or None]] = []
        for _ in range(height):
            self.matrix.append([None for _ in range(width)])
        print(f"world size: x {len(self.matrix[0])}, y {len(self.matrix)}")

    def add_tile(self, tile_type: type, x: int, y: int):
        new_tile: Tile = tile_type(self, x, y)
        if not self.matrix[y][x]:
            self.tiles.append(new_tile)
            self.matrix[y][x] = new_tile

    def delete_tile(self, x: int, y: int):
        tile = self.matrix[y][x]
        if tile:
            self.tiles.remove(tile)
            self.matrix[y][x] = None

    def update(self):
        self.updates = 0
        for tile in self.tiles:
            if tile.do_update():
                self.updates += 1


# Tile types --------------------------------------


class SolidTile(Tile):

    MAX_SKIP = 100000

    def update(self) -> bool:
        return False


class SemiSolidTile(Tile):

    def update(self):
        if self.try_move(0, 1):
            return True
        if self.try_move(-1, 1):
            return True
        if self.try_move(1, 1):
            return True
        return False


class LiquidTile(Tile):

    MAX_SKIP = 20

    def update(self):
        if self.try_move(0, 1):
            return True
        if self.try_move(-1, 0):
            return True
        if self.try_move(-1, 1):
            return True
        if self.try_move(1, 1):
            return True
        if self.try_move(1, 0):
            return True
        return False


# Tiles ---------------------------------


class ConcreteTile(SolidTile):

    NAME = "Concrete"

    def __init__(self, world: "World", x: int, y: int):
        super().__init__(
            (160 + random.randint(-20, 20), 160 + random.randint(-20, 20), 160 + random.randint(-20, 20)),
            100,
            world,
            x,
            y
        )


class SandTile(SemiSolidTile):

    NAME = "Sand"

    def __init__(self, world: "World", x: int, y: int):
        super().__init__((255-random.randint(0, 50), 255-random.randint(0, 50), 0), 10, world, x, y)


class WaterTile(LiquidTile):

    NAME = "Water"

    def __init__(self, world: "World", x: int, y: int):
        super().__init__((0, 0, 255-random.randint(0, 100)), 2, world, x, y)


class OilTile(LiquidTile):

    NAME = "Oil"

    def __init__(self, world: "World", x: int, y: int):
        super().__init__((193-random.randint(0, 20), 193-random.randint(0, 20), 69-random.randint(0, 10)), 1, world, x, y)


TILES: List[type] = [
    ConcreteTile,
    SandTile,
    WaterTile,
    OilTile
]
