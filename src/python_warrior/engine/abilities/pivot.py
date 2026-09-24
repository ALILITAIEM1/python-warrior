from ...events import emit
from .base import Base

ROTATION_DIRECTIONS = ["forward", "right", "backward", "left"]


class Pivot(Base):
    description = 'Rotate "left", "right" or "backward" (default).'

    def perform(self, direction="backward"):
        self.verify_direction(direction)
        self._unit.position.rotate(ROTATION_DIRECTIONS.index(direction))
        self._unit.say(f"pivots {direction}")
        emit("pivoted", self._unit, direction=self._unit.position.direction)
