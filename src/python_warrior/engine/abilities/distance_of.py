from .base import Base


class DistanceOf(Base):
    description = "Pass a Space as an argument, and it will return an integer representing the distance to that space."

    def perform(self, space):
        return self._unit.position.distance_of(space)
