from .base import Base


class Health(Base):
    description = "Returns an integer representing your health."

    def perform(self):
        return self._unit.health
