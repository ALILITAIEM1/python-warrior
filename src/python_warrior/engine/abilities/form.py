import math

from ...events import emit
from .base import Base


class Form(Base):
    description = "Forms a golem in given direction taking half of invoker's health. The passed function is called for each golem turn."

    def perform(self, direction="forward", turn=None):
        self.verify_direction(direction)
        if self.space(direction).is_empty():
            x, y = self._unit.position.translate_offset(*self.offset(direction))
            health = math.floor(self._unit.health / 2.0)
            golem = self._unit.base_golem()
            golem.max_health = health
            golem.turn = turn
            self._unit.health -= health
            self._unit.position.floor.add(golem, x, y, self._unit.position.direction)
            self._unit.say(f"forms a golem {direction} and gives half of his health ({health})")
            emit("formed", golem, by=self._unit, location=(x, y))
        else:
            self._unit.say("fails to form golem because something is blocking the way.")
