from ...events import emit
from ...utils import ruby_round
from .base import Base


class Rest(Base):
    description = "Gain 10% of max health back, but do nothing more."

    def perform(self):
        unit = self._unit
        if unit.health < unit.max_health:
            amount = ruby_round(unit.max_health * 0.1)
            if unit.health + amount > unit.max_health:
                amount = unit.max_health - unit.health
            unit.health += amount
            unit.say(f"receives {amount} health from resting, up to {unit.health} health")
            emit("healed", unit, amount=amount, health=unit.health)
        else:
            unit.say("is already fit as a fiddle")
