from ...events import emit
from .base import Base


class Bind(Base):
    description = 'Binds a unit in given direction to keep him from moving ("forward" by default).'

    def perform(self, direction="forward"):
        self.verify_direction(direction)
        receiver = self.unit(direction)
        if receiver:
            self._unit.say(f"binds {direction} and restricts {receiver}")
            receiver.bind()
            emit("bound", receiver, by=self._unit, location=receiver.location)
        else:
            self._unit.say(f"binds {direction} and restricts nothing")
