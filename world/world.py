import random
from typing import Tuple, List, Dict, Type, Iterable


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
        DOWN,
        DOWN_LEFT,
        DOWN_RIGHT,
        LEFT,
        UP_LEFT,
        UP,
        UP_RIGHT,
        RIGHT,
    )


class NextPosition:

    def __init__(self, x: int, y: int, valid: bool):
        self.x = x
        self.y = y
        self.valid = valid


class Tile:

    NAME: str

    INTERACTIONS: Dict[Type["Tile"], Type["Tile"]] = {}
    """
    This dictionary defines how the tile interacts with other tiles.
    It can be interpreted as key -> value, or in words:
    
        if a tile of type "key" is encountered, then transform into type "value"
    """

    UPPER_HEATH_THRESHOLD: Tuple[int, Type["Tile"]] or None = None
    LOWER_HEATH_THRESHOLD: Tuple[int, Type["Tile"]] or None = None

    def __init__(
            self,
            color: Tuple[int, int, int],
            density: int,
            world: "World",
            x: int,
            y: int,
            base_heat: int = 25,
            heat_transfer_coefficient: float = 0,
            passive_heat_loss: int = 0
    ):
        # render stuff
        self.color = color
        # Physics stuff
        self.density = density
        self.base_heat = base_heat
        self.heat = base_heat
        self.heat_transfer_coefficient = heat_transfer_coefficient
        self.passive_heath_loss = passive_heat_loss
        # position
        self.x = x
        self.y = y
        self.world = world
        # optimization
        self.max_skip_update: int = 0
        self.skip_update: int = 0

    def delete(self):
        self.world.tiles_to_delete.append(self)

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

    def get_neighbour_tile(self, direction: Tuple[int, int]) -> "Tile" or None:
        next_pos = self.get_next_pos(direction)
        if not next_pos.valid:
            return None
        checked_tile = self.get_tile(next_pos.x, next_pos.y)
        if not checked_tile:
            return None
        return checked_tile

    def move(self, new_x: int, new_y: int, replacement_tile: "Tile" or None = None):
        self.world.matrix[self.y][self.x] = replacement_tile
        self.x = new_x
        self.y = new_y
        self.world.matrix[self.y][self.x] = self

    def interact(self, target_tile: "Tile") -> bool:
        interaction = self.INTERACTIONS.get(type(target_tile))
        if interaction:
            self.transform(interaction)
            return True
        return False

    def transform(self, new_type: type) -> "Tile":
        self.delete()
        new_tile = new_type(self.world, self.x, self.y)
        self.world.tiles_to_add.append(new_tile)
        return new_tile

    def check_thresholds(self):
        if self.UPPER_HEATH_THRESHOLD:
            if self.heat >= self.UPPER_HEATH_THRESHOLD[0]:
                new_tile = self.transform(self.UPPER_HEATH_THRESHOLD[1])
                new_tile.heat = self.heat
                return True
        if self.LOWER_HEATH_THRESHOLD:
            if self.heat <= self.LOWER_HEATH_THRESHOLD[0]:
                new_tile = self.transform(self.LOWER_HEATH_THRESHOLD[1])
                new_tile.heat = self.heat
                return True
        return False

    def exchange_heat(self, target_tile: "Tile"):
        htc: float = (self.heat_transfer_coefficient + target_tile.heat_transfer_coefficient) / 2
        exchanged_heat = int(((target_tile.heat - self.heat) * htc) / 2)
        self.heat += exchanged_heat
        target_tile.heat -= exchanged_heat

    def do_interact(self) -> bool:
        # add this to the update function of a tile to have it just interact
        for direction in Dir.ALL:
            tile = self.get_neighbour_tile(direction)
            if not tile:
                continue
            if self.interact(tile):
                return True
        return False

    def do_exchange_heat(self):
        self.heat -= self.passive_heath_loss
        for direction in Dir.ALL:
            tile = self.get_neighbour_tile(direction)
            if not tile:
                continue
            self.exchange_heat(tile)
        self.check_thresholds()

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

    def check_directions(self, directions: Iterable[Tuple[int, int]]):
        # add this to the update function of a tile to make it move
        for direction in directions:
            if self.try_move(direction):
                return

    def update_position(self):
        raise NotImplemented

    def update_temperature(self):
        raise NotImplemented


class World:

    def __init__(self, width: int, height: int):
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
        # update tiles positions
        for tile in self.tiles:
            tile.update_position()
        # update tiles temperatures
        for tile in self.tiles:
            tile.update_temperature()
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

    def update_position(self):
        pass

    def update_temperature(self):
        self.do_exchange_heat()


class SemiSolidTile(Tile):

    DIRECTIONS = (Dir.DOWN, Dir.DOWN_LEFT, Dir.DOWN_RIGHT)

    def update_position(self):
        self.check_directions(self.DIRECTIONS)

    def update_temperature(self):
        self.do_exchange_heat()


class LiquidTile(Tile):

    DIRECTIONS = (
        (Dir.DOWN, Dir.DOWN_LEFT, Dir.LEFT, Dir.DOWN_RIGHT, Dir.RIGHT),
        (Dir.DOWN, Dir.DOWN_RIGHT, Dir.RIGHT, Dir.DOWN_LEFT, Dir.LEFT)
    )

    def update_position(self):
        self.check_directions(random.choice(self.DIRECTIONS))

    def update_temperature(self):
        self.do_exchange_heat()


class GasTile(Tile):

    DIRECTIONS = (
        (Dir.UP, Dir.UP_LEFT, Dir.LEFT, Dir.UP_RIGHT, Dir.RIGHT),
        (Dir.UP, Dir.UP_RIGHT, Dir.RIGHT, Dir.UP_LEFT, Dir.LEFT)
    )

    def update_position(self):
        self.check_directions(random.choice(self.DIRECTIONS))

    def update_temperature(self):
        self.do_exchange_heat()
