"""A single square of the floor, as seen by the player."""


class Space:
    def __init__(self, floor, x, y):
        self._floor = floor
        self._x = x
        self._y = y

    def is_wall(self):
        return self._floor.out_of_bounds(self._x, self._y)

    def is_warrior(self):
        from .units.warrior import Warrior

        return isinstance(self.unit, Warrior)

    def is_golem(self):
        from .units.golem import Golem

        return isinstance(self.unit, Golem)

    def is_player(self):
        return self.is_warrior() or self.is_golem()

    def is_enemy(self):
        return bool(self.unit) and not self.is_player() and not self.is_captive()

    def is_captive(self):
        unit = self.unit
        return bool(unit) and unit.is_bound()

    def is_empty(self):
        return self.unit is None and not self.is_wall()

    def is_stairs(self):
        return self._floor.stairs_location == self.location

    def is_ticking(self):
        unit = self.unit
        return bool(unit) and "explode!" in unit.abilities

    @property
    def unit(self):
        return self._floor.get(self._x, self._y)

    @property
    def location(self):
        return (self._x, self._y)

    @property
    def character(self):
        unit = self.unit
        if unit:
            return unit.character
        if self.is_stairs():
            return ">"
        return " "

    def __str__(self):
        unit = self.unit
        if unit:
            return str(unit)
        if self.is_wall():
            return "wall"
        return "nothing"

    def __repr__(self):
        return f"<Space {self.location} {self}>"
