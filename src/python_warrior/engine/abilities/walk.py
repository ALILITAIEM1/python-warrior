from ...events import emit
from .base import Base


class Walk(Base):
    description = 'Move in the given direction ("forward" by default).'

    def perform(self, direction="forward"):
        self.verify_direction(direction)
        if self._unit.position:
            self._unit.say(f"walks {direction}")
            target = self.space(direction)
            if target.is_empty():
                start = self._unit.location
                self._unit.position.move(*self.offset(direction))
                emit("moved", self._unit, start=start, end=self._unit.location)
            else:
                self._unit.say(f"bumps into {target}")
                emit("bumped", self._unit, target=target.location)
