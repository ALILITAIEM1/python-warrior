from .base import Base


class DirectionOfStairs(Base):
    description = 'Returns the direction ("left", "right", "forward", "backward") the stairs are from your location.'

    def perform(self):
        return self._unit.position.relative_direction_of_stairs()
