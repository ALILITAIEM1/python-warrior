from ...events import emit
from .base import Base


class Detonate(Base):
    description = "Detonate a bomb in a given direction (\"forward\" by default) which damages that space and surrounding 4 spaces (including yourself)."

    def perform(self, direction="forward"):
        self.verify_direction(direction)
        if self._unit.position:
            self._unit.say(f"detonates a bomb {direction} launching a deadly explosion.")
            blast = [(1, 0), (1, 1), (1, -1), (2, 0), (0, 0)]
            emit("detonated", self._unit, center=self.space(direction, 1, 0).location,
                 spaces=[self.space(direction, x, y).location for x, y in blast])
            self.bomb(direction, 1, 0, 8)
            for x, y in blast[1:]:
                self.bomb(direction, x, y, 4)

    def bomb(self, direction, x, y, damage_amount):
        if self._unit.position:
            receiver = self.space(direction, x, y).unit
            if receiver:
                if "explode!" in receiver.abilities:
                    receiver.say("caught in bomb's flames which detonates ticking explosive")
                    receiver.abilities["explode!"].perform()
                else:
                    self.damage(receiver, damage_amount)
