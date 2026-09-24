"""DSL used by tower level files (port of RubyWarrior::LevelLoader).

A level file is plain Python executed with these functions as globals::

    size(8, 1)
    stairs(7, 0)
    warrior(0, 0, "east", abilities=["walk!"])
    unit("sludge", 4, 0, "west")
"""

from . import engine
from .engine import units as units_module
from .utils import camelize


class LevelLoader:
    def __init__(self, level):
        self.floor = engine.Floor()
        self.level = level
        self.level.floor = self.floor

    def description(self, desc):
        self.level.description = desc

    def tip(self, tip):
        self.level.tip = tip

    def clue(self, clue):
        self.level.clue = clue

    def time_bonus(self, bonus):
        self.level.time_bonus = bonus

    def ace_score(self, score):
        self.level.ace_score = score

    def size(self, width, height):
        self.floor.width = width
        self.floor.height = height

    def stairs(self, x, y):
        self.floor.place_stairs(x, y)

    def unit(self, unit, x, y, facing="north", abilities=()):
        if not isinstance(unit, units_module.Base):
            unit = getattr(units_module, camelize(str(unit)))()
        self.floor.add(unit, x, y, facing)
        if abilities:
            unit.add_abilities(*abilities)
        return unit

    def warrior(self, *args, **kwargs):
        warrior = self.unit(units_module.Warrior(), *args, **kwargs)
        self.level.setup_warrior(warrior)
        return warrior

    def namespace(self):
        names = ["description", "tip", "clue", "time_bonus", "ace_score", "size", "stairs", "unit", "warrior"]
        return {name: getattr(self, name) for name in names}

    def load(self, source, filename="<level>"):
        exec(compile(source, filename, "exec"), self.namespace())
