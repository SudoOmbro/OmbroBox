import random
from typing import Tuple, List, Dict


TILES: List[type] = []


def add_to_tile_list(tile: type) -> type:
    TILES.append(tile)
    return tile


class Dir:
    """ Defines all the possible directions """

    UP = 0, -1
    DOWN = 0, 1,
    LEFT = -1, 0,
    RIGHT = 1, 0
    UP_LEFT = -1, -1
    UP_RIGHT = 1, -1
    DOWN_LEFT = -1, 1
    DOWN_RIGHT = 1, 1

    ALL = (
        UP,
        UP_RIGHT,
        RIGHT,
        DOWN_RIGHT,
        DOWN,
        DOWN_LEFT,
        LEFT,
        UP_LEFT
    )


class NextPosition:

    def __init__(self, x: int, y: int, valid: bool):
        self.x = x
        self.y = y
        self.valid = valid


class Tile:

    NAME: str
    MAX_SKIP: int = 60

    DIRECTIONS: Tuple[Tuple[int, int]]
    """ This tuple defines which directions, in order, the tile should check """

    INTERACTIONS: Dict[type, type] = {}
    """
    This dictionary defines how the tile interacts with other tiles.
    It can be interpreted as key -> value, or in words:
    
        if a tile of type "key" is encountered, then transform into type "value"
    """
    # TODO interactions system honestly sucks, it needs to be replaced with a heat transfer based system
    # actually we can keep it, just add the heat system on top.
    # TODO add a heat variable & a heat transfer coefficient variable (htc)

    def __init__(
            self,
            color: Tuple[int, int, int],
            density: int,
            world: "World",
            x: int,
            y: int,
            base_heat: int = 0,
            heat_transfer_coefficient: float = 0
    ):
        # render stuff
        self.color = color
        # Physics stuff
        self.density = density
        self.heat = base_heat
        self.heat_transfer_coefficient = heat_transfer_coefficient
        # position
        self.x = x
        self.y = y
        self.world = world
        # optimization
        self.max_skip_update: int = 0
        self.skip_update: int = 0

    def get_next_pos(self, vector: Tuple[int, int]) -> NextPosition:
        valid: bool = True
        next_x: int = self.x + vector[0]
        if (next_x < 0) or (next_x >= self.world.width):
            valid = False
        next_y: int = self.y + vector[1]
        if (next_y < 0) or (next_y >= self.world.height):
            valid = False
        return NextPosition(next_x, next_y, valid)

    def get_tile(self, x: int, y: int) -> "Tile" or None:
        return self.world.matrix[y][x]

    def move(self, new_x: int, new_y: int, replacement_tile: "Tile" or None = None):
        self.world.matrix[self.y][self.x] = replacement_tile
        self.x = new_x
        self.y = new_y
        self.world.matrix[self.y][self.x] = self

    def check_directions(self):
        for direction in self.DIRECTIONS:
            if self.try_move(direction):
                return True
        return False

    def interact(self):
        # add this to the update function of a tile to have it just interact
        for direction in Dir.ALL:
            # get next position
            next_pos = self.get_next_pos(direction)
            if not next_pos.valid:
                continue
            # get tile to check
            checked_tile = self.get_tile(next_pos.x, next_pos.y)
            if not checked_tile:
                continue
            # check interaction
            interaction = self.INTERACTIONS.get(type(checked_tile))
            if interaction:
                self.transform(interaction)
                return True

    def exchange_heat_and_interact(self):
        # add this to the update function of a tile to have it interact AND exchange heat
        for direction in Dir.ALL:
            # get next position
            next_pos = self.get_next_pos(direction)
            if not next_pos.valid:
                continue
            # get tile to check
            checked_tile = self.get_tile(next_pos.x, next_pos.y)
            if not checked_tile:
                continue
            # check interaction
            interaction = self.INTERACTIONS.get(type(checked_tile))
            if interaction:
                self.transform(interaction)
                return True
            # TODO check heat transfer

    def try_move(self, direction: Tuple[int, int]) -> bool:
        next_pos = self.get_next_pos(direction)
        if not next_pos.valid:
            return False
        checked_tile = self.get_tile(next_pos.x, next_pos.y)
        if not checked_tile:
            self.move(next_pos.x, next_pos.y)
            return True
        elif checked_tile.density < self.density:
            checked_tile.x = self.x
            checked_tile.y = self.y
            self.move(next_pos.x, next_pos.y, replacement_tile=checked_tile)
            return True
        return False

    def delete(self):
        self.world.tiles_to_delete.append(self)

    def transform(self, new_type: type):
        self.delete()
        self.world.tiles_to_add.append(new_type(self.world, self.x, self.y))

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
        self.tiles_to_delete: List[Tile] = []
        self.tiles_to_add: List[Tile] = []
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

    def _add_tile(self, tile: Tile):
        self.tiles.append(tile)
        self.matrix[tile.y][tile.x] = tile

    def delete_tile(self, x: int, y: int):
        tile = self.matrix[y][x]
        if tile:
            self.tiles.remove(tile)
            self.matrix[y][x] = None

    def _delete_tile(self, tile: Tile):
        self.tiles.remove(tile)
        self.matrix[tile.y][tile.x] = None

    def update(self):
        self.updates = 0
        # update tiles
        for tile in self.tiles:
            if tile.do_update():
                self.updates += 1
        # delete tiles that need to be deleted
        if self.tiles_to_delete:
            for tile in self.tiles_to_delete:
                self._delete_tile(tile)
            self.tiles_to_delete.clear()
        # add tiles that need to be added
        if self.tiles_to_add:
            for tile in self.tiles_to_add:
                self._add_tile(tile)
            self.tiles_to_add.clear()


# Tile types --------------------------------------

class SolidTile(Tile):

    MAX_SKIP = 100000

    def update(self) -> bool:
        return False


class SemiSolidTile(Tile):

    DIRECTIONS = (Dir.DOWN, Dir.DOWN_LEFT, Dir.DOWN_RIGHT)

    def update(self):
        return self.check_directions()


class LiquidTile(Tile):

    DIRECTIONS = (Dir.DOWN, Dir.DOWN_LEFT, Dir.LEFT, Dir.DOWN_RIGHT, Dir.RIGHT)
    MAX_SKIP = 20

    def update(self):
        return self.check_directions() or self.interact()


class GasTile(Tile):

    MAX_SKIP = 0
    DIRECTIONS = (Dir.UP, Dir.UP_RIGHT, Dir.RIGHT, Dir.UP_LEFT, Dir.LEFT)

    life: int

    def update(self):
        if self.life == 0:
            self.delete()
            return True
        self.life -= 1
        return self.check_directions()


# Tiles ---------------------------------

@add_to_tile_list
class ConcreteTile(SolidTile):

    NAME = "Concrete"

    def __init__(self, world: "World", x: int, y: int):
        super().__init__(
            (160 + random.randint(-20, 20), 160 + random.randint(-20, 20), 160 + random.randint(-20, 20)),
            100000,
            world,
            x,
            y
        )


@add_to_tile_list
class SandTile(SemiSolidTile):

    NAME = "Sand"

    def __init__(self, world: "World", x: int, y: int):
        super().__init__((255-random.randint(0, 50), 255-random.randint(0, 50), 0), 10, world, x, y)


@add_to_tile_list
class LavaTile(LiquidTile):

    NAME = "Lava"

    def __init__(self, world: "World", x: int, y: int):
        super().__init__((255 - random.randint(0, 20), 0, 0), 1000, world, x, y)


@add_to_tile_list
class VaporTile(GasTile):

    NAME = "Vapor"

    def __init__(self, world: "World", x: int, y: int):
        super().__init__((255-random.randint(0, 20), 255-random.randint(0, 20), 255-random.randint(0, 20)), 0, world, x, y)
        self.life = random.randint(120, 300)

    def update(self):
        if self.life == 0:
            self.transform(WaterTile)
            return True
        self.life -= 1
        return self.check_directions()


@add_to_tile_list
class WaterTile(LiquidTile):

    NAME = "Water"
    INTERACTIONS = {LavaTile: VaporTile}

    def __init__(self, world: "World", x: int, y: int):
        super().__init__((0, 0, 255-random.randint(0, 100)), 2, world, x, y)


@add_to_tile_list
class OilTile(LiquidTile):

    NAME = "Oil"

    def __init__(self, world: "World", x: int, y: int):
        super().__init__((193-random.randint(0, 20), 193-random.randint(0, 20), 69-random.randint(0, 10)), 1, world, x, y)
