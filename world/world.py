from functools import cache
from typing import Tuple, List, Type, Iterable, Callable

from world.semirandom import randint


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


class TileFlags:
    CAN_MOVE = 0
    TRANSMITS_HEAT = 1


class NextPosition:

    def __init__(self, x: int, y: int, valid: bool):
        self.x = x
        self.y = y
        self.valid = valid


class Tile:

    NAME: str

    def __init__(
            self,
            color: Tuple[int, int, int],
            density: int,
            world: "World",
            x: int,
            y: int
    ):
        # render stuff
        self.color = color
        # Physics stuff
        self.density = density
        # position
        self.x = x
        self.y = y
        self.world = world
        # control flags
        self.active: bool = True

    def remove(self):
        if self.active:
            self.world.tiles_to_delete.append(self)
            self.active = False
            return True
        return False

    def add(self):
        self.world.tiles.append(self)
        self.world.spatial_matrix[self.y][self.x] = self

    def delete(self):
        self.world.tiles.remove(self)
        self.world.spatial_matrix[self.y][self.x] = None

    def get_next_pos(self, relative_vector: Tuple[int, int]) -> NextPosition:
        # returns the world position given a vector relative to the tile
        next_x: int = self.x + relative_vector[0]
        if not 0 <= next_x < self.world.width:
            return NextPosition(0, 0, False)
        next_y: int = self.y + relative_vector[1]
        if not 0 <= next_y < self.world.height:
            return NextPosition(0, 0, False)
        return NextPosition(next_x, next_y, True)

    def get_neighbour_tile(self, direction: Tuple[int, int]) -> "Tile" or None:
        next_pos = self.get_next_pos(direction)
        if not next_pos.valid:
            return None
        checked_tile = self.world.spatial_matrix[next_pos.y][next_pos.x]
        if not checked_tile:
            return None
        return checked_tile

    def transform(self, new_type: type) -> "Tile" or None:
        if self.remove():
            new_tile = new_type(self.world, self.x, self.y)
            self.world.tiles_to_add.append(new_tile)
            return new_tile
        return None


class MovingTile(Tile):

    _MAX_UPDATE_SKIP = 3

    def __init__(self, color: Tuple[int, int, int], density: int, world: "World", x: int, y: int):
        super().__init__(color, density, world, x, y)
        self._skip_update: int = 0
        self._cooldown: int = 0

    def add(self):
        super().add()
        self.world.moving_tiles.append(self)

    def delete(self):
        super().delete()
        self.world.moving_tiles.remove(self)

    def move(self, new_x: int, new_y: int, replacement_tile: "Tile" or None):
        self.world.spatial_matrix[self.y][self.x] = replacement_tile
        self.x = new_x
        self.y = new_y
        self.world.spatial_matrix[self.y][self.x] = self

    def try_move(self, direction: Tuple[int, int]) -> bool:
        next_pos = self.get_next_pos(direction)
        if not next_pos.valid:
            return False
        checked_tile = self.world.spatial_matrix[next_pos.y][next_pos.x]
        if not checked_tile:
            self.move(next_pos.x, next_pos.y, None)
            return True
        elif checked_tile.density < self.density:
            checked_tile.x = self.x
            checked_tile.y = self.y
            self.move(next_pos.x, next_pos.y, replacement_tile=checked_tile)
            return True
        return False

    def check_directions(self, directions: Iterable[Tuple[int, int]]):
        if self._cooldown == 0:
            for direction in directions:
                if self.try_move(direction):
                    self._skip_update = 0
                    return
        else:
            self._cooldown -= 1
            return
        if self._skip_update != self._MAX_UPDATE_SKIP:
            self._skip_update += 1
        self._cooldown = self._skip_update

    def update_position(self):
        raise NotImplemented


class HeatTile(Tile):

    UPPER_HEATH_THRESHOLD: Tuple[int, Type[Tile]] or None = None
    LOWER_HEATH_THRESHOLD: Tuple[int, Type[Tile]] or None = None

    check_thresholds: Callable

    def __init__(
            self,
            color: Tuple[int, int, int],
            density: int,
            world: "World",
            x: int,
            y: int,
            base_heat: int = 25,
            heat_transfer_coefficient: float = 1,
            passive_heat_loss: int = 0
    ):
        super().__init__(color, density, world, x, y)
        self.heat = base_heat
        self.heat_transfer_coefficient = heat_transfer_coefficient
        self.passive_heath_loss = passive_heat_loss
        # optimize threshold check
        if self.UPPER_HEATH_THRESHOLD and (not self.LOWER_HEATH_THRESHOLD):
            self.check_thresholds = self.check_upper_threshold
        elif (not self.UPPER_HEATH_THRESHOLD) and self.LOWER_HEATH_THRESHOLD:
            self.check_thresholds = self.check_lower_threshold
        elif self.UPPER_HEATH_THRESHOLD and self.LOWER_HEATH_THRESHOLD:
            self.check_thresholds = self.check_both_thresholds
        else:
            self.check_thresholds = self.check_no_threshold

    def add(self):
        super().add()
        self.world.heat_tiles.append(self)

    def delete(self):
        super().delete()
        self.world.heat_tiles.remove(self)

    def check_no_threshold(self) -> bool:
        return False

    def check_upper_threshold(self) -> bool:
        if self.heat >= self.UPPER_HEATH_THRESHOLD[0]:
            if self.UPPER_HEATH_THRESHOLD[1]:
                new_tile = self.transform(self.UPPER_HEATH_THRESHOLD[1])
                if new_tile:
                    new_tile.heat = self.heat
                return True
            self.remove()
            return True
        return False

    def check_lower_threshold(self) -> bool:
        if self.heat <= self.LOWER_HEATH_THRESHOLD[0]:
            if self.LOWER_HEATH_THRESHOLD[1]:
                new_tile = self.transform(self.LOWER_HEATH_THRESHOLD[1])
                if new_tile:
                    new_tile.heat = self.heat
                return True
            self.remove()
            return True
        return False

    def check_both_thresholds(self) -> bool:
        return self.check_upper_threshold() or self.check_lower_threshold()

    def exchange_heat(self, target_tile: "HeatTile"):
        htc: float = self.heat_transfer_coefficient + target_tile.heat_transfer_coefficient
        exchanged_heat = int((target_tile.heat - self.heat) * htc) >> 2
        self.heat += exchanged_heat
        target_tile.heat -= exchanged_heat

    @cache
    def can_tile_exchange_heat(self, tile):
        return (tile is not None) and (tile in self.world.heat_tiles)

    def do_exchange_heat(self):
        self.heat -= self.passive_heath_loss
        for direction in Dir.ALL:
            tile: Tile = self.get_neighbour_tile(direction)
            if self.can_tile_exchange_heat(tile):
                self.exchange_heat(tile)
        self.check_thresholds()

    def update_temperature(self):
        raise NotImplemented


class CustomTile(Tile):

    def add(self):
        super().add()
        self.world.custom_tiles.append(self)

    def delete(self):
        super().delete()
        self.world.custom_tiles.remove(self)

    def custom_update(self):
        raise NotImplemented


class GenericSystem:

    NAME: str

    def __init__(self, world: "World"):
        self.world = world

    def update(self):
        raise NotImplemented


class MovementSystem(GenericSystem):

    NAME = "Movement System"

    def update(self):
        for tile in self.world.moving_tiles:
            tile.update_position()


class HeathSystem(GenericSystem):

    NAME = "Heath System"

    def update(self):
        for tile in self.world.heat_tiles:
            tile.update_temperature()


class CustomTileSystem(GenericSystem):

    NAME = "Custom Tile System"

    def update(self):
        for tile in self.world.custom_tiles:
            tile.custom_update()


class World:

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        # init tile lists
        self.tiles: List[Tile] = []
        self.moving_tiles: List[MovingTile] = []
        self.heat_tiles: List[HeatTile] = []
        self.custom_tiles: List[CustomTile] = []
        self.tiles_to_delete: List[Tile] = []
        self.tiles_to_add: List[Tile] = []
        # init world matrices
        init_matrix: List[List[Tile or None]] = []
        for _ in range(height):
            init_matrix.append([None for _ in range(width)])
        self.spatial_matrix: Tuple[List[Tile], ...] = tuple(init_matrix)
        print(f"world size: x {len(self.spatial_matrix[0])}, y {len(self.spatial_matrix)}")
        # init systems
        self.systems: Iterable[GenericSystem] = (
            MovementSystem(self),
            HeathSystem(self),
            CustomTileSystem(self)
        )

    def add_tile(self, tile_type: type, x: int, y: int) -> Tile:
        """ adds a tile at the given position and returns it """
        new_tile: Tile = tile_type(self, x, y)
        if not self.spatial_matrix[y][x]:
            new_tile.add()
        return new_tile

    def delete_tile(self, x: int, y: int) -> Tile:
        """ Removes a tile at the given position and returns it """
        tile = self.spatial_matrix[y][x]
        if tile:
            tile.remove()
        return tile

    def update(self):
        # update systems
        for system in self.systems:
            system.update()
        # delete tiles that need to be deleted
        if self.tiles_to_delete:
            for tile in self.tiles_to_delete:
                tile.delete()
                del tile
            self.tiles_to_delete.clear()
        # add tiles that need to be added
        if self.tiles_to_add:
            for tile in self.tiles_to_add:
                tile.add()
                del tile
            self.tiles_to_add.clear()


# Tile types --------------------------------------

class SolidTile(HeatTile):

    def update_temperature(self):
        self.do_exchange_heat()


class SemiSolidTile(HeatTile, MovingTile):

    DIRECTIONS = (Dir.DOWN, Dir.DOWN_LEFT, Dir.DOWN_RIGHT)

    def update_position(self):
        self.check_directions(self.DIRECTIONS)

    def update_temperature(self):
        self.do_exchange_heat()


class LiquidTile(HeatTile, MovingTile):

    DIRECTIONS = (
        (Dir.DOWN, Dir.DOWN_LEFT, Dir.LEFT, Dir.DOWN_RIGHT, Dir.RIGHT),
        (Dir.DOWN, Dir.DOWN_RIGHT, Dir.RIGHT, Dir.DOWN_LEFT, Dir.LEFT)
    )

    def update_position(self):
        self.check_directions(self.DIRECTIONS[randint(2)])

    def update_temperature(self):
        self.do_exchange_heat()


class GasTile(HeatTile, MovingTile):

    DIRECTIONS = (
        (Dir.UP, Dir.UP_LEFT, Dir.LEFT, Dir.UP_RIGHT, Dir.RIGHT),
        (Dir.UP, Dir.UP_RIGHT, Dir.RIGHT, Dir.UP_LEFT, Dir.LEFT)
    )

    def update_position(self):
        self.check_directions(self.DIRECTIONS[randint(2)])

    def update_temperature(self):
        self.do_exchange_heat()
