"""The 2D grid holding units and stairs."""

from .position import Position
from .space import Space


class Floor:
    def __init__(self):
        self.width = 0
        self.height = 0
        self._units = []
        self.stairs_location = (-1, -1)

    def add(self, unit, x, y, direction=None):
        self._units.append(unit)
        unit.position = Position(self, x, y, direction)

    def place_stairs(self, x, y):
        self.stairs_location = (x, y)

    @property
    def stairs_space(self):
        return self.space(*self.stairs_location)

    @property
    def units(self):
        return [u for u in self._units if u.position is not None]

    @property
    def other_units(self):
        from .units.warrior import Warrior

        return [u for u in self.units if not isinstance(u, Warrior)]

    def get(self, x, y):
        for unit in self.units:
            if unit.position.is_at(x, y):
                return unit
        return None

    def space(self, x, y):
        return Space(self, x, y)

    def out_of_bounds(self, x, y):
        return x < 0 or y < 0 or x > self.width - 1 or y > self.height - 1

    @property
    def character(self):
        rows = [" " + "-" * self.width]
        for y in range(self.height):
            rows.append("|" + "".join(self.space(x, y).character for x in range(self.width)) + "|")
        rows.append(" " + "-" * self.width)
        return "\n".join(rows) + "\n"

    @property
    def unique_units(self):
        unique = []
        for unit in self.units:
            if type(unit) not in [type(u) for u in unique]:
                unique.append(unit)
        return unique
