from ...events import emit
from .base import Base


class Rescue(Base):
    description = 'Rescue a captive from his chains (earning 20 points) in given direction ("forward" by default).'

    def perform(self, direction="forward"):
        from ..units.captive import Captive

        self.verify_direction(direction)
        if self.space(direction).is_captive():
            recipient = self.unit(direction)
            self._unit.say(f"unbinds {direction} and rescues {recipient}")
            recipient.unbind()
            if isinstance(recipient, Captive):
                location = recipient.location
                recipient.position = None
                emit("rescued", recipient, location=location, by=self._unit)
                self._unit.earn_points(20)
        else:
            self._unit.say(f"unbinds {direction} and rescues nothing")
