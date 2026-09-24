import math

from ...events import emit
from .base import Base


class Attack(Base):
    description = 'Attacks a unit in given direction ("forward" by default).'

    def perform(self, direction="forward"):
        self.verify_direction(direction)
        receiver = self.unit(direction)
        target = self.space(direction).location
        if receiver:
            self._unit.say(f"attacks {direction} and hits {receiver}")
            emit("attacked", self._unit, target=target, hit=True)
            if direction == "backward":
                power = math.ceil(self._unit.attack_power / 2.0)
            else:
                power = self._unit.attack_power
            self.damage(receiver, power)
        else:
            self._unit.say(f"attacks {direction} and hits nothing")
            emit("attacked", self._unit, target=target, hit=False)
