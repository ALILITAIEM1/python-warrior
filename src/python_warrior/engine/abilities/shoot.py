from ...events import emit
from .base import Base


class Shoot(Base):
    description = 'Shoot your bow & arrow in given direction ("forward" by default).'

    def perform(self, direction="forward"):
        self.verify_direction(direction)
        receivers = [u for u in self.multi_unit(direction, range(1, 4)) if u is not None]
        receiver = receivers[0] if receivers else None
        if receiver:
            self._unit.say(f"shoots {direction} and hits {receiver}")
            emit("shot", self._unit, start=self._unit.location, target=receiver.location, hit=True)
            self.damage(receiver, self._unit.shoot_power)
        else:
            self._unit.say("shoots and hits nothing")
            emit("shot", self._unit, start=self._unit.location,
                 target=self.space(direction, 3).location, hit=False)

    def multi_unit(self, direction, distances):
        return [self.unit(direction, n) for n in distances]
