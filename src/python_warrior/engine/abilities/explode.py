from ...events import emit
from .base import Base


class Explode(Base):
    description = "Kills you and all surrounding units. You probably don't want to do this intentionally."

    def __init__(self, unit):
        super().__init__(unit)
        self.time = None

    def perform(self):
        if self._unit.position:
            self._unit.say("explodes, collapsing the ceiling and damanging every unit.")
            emit("exploded", self._unit, location=self._unit.location)
            for unit in self._unit.position.floor.units:
                unit.take_damage(100)

    def pass_turn(self):
        if self.time and self._unit.position:
            self._unit.say("is ticking")
            self.time -= 1
            emit("ticking", self._unit, time=self.time)
            if self.time == 0:
                self.perform()
