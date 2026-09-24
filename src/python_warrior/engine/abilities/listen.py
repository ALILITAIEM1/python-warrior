from .base import Base


class Listen(Base):
    description = "Returns a list of all spaces which have units in them."

    def perform(self):
        return [u.position.space for u in self._unit.position.floor.units if u is not self._unit]
