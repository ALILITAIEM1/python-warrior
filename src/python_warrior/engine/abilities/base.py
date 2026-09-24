"""Base class of abilities (actions and senses)."""


from ..position import RELATIVE_DIRECTIONS


class Base:
    description = None

    def __init__(self, unit):
        self._unit = unit

    def offset(self, direction, forward=1, right=0):
        if direction == "forward":
            return (forward, -right)
        if direction == "backward":
            return (-forward, right)
        if direction == "right":
            return (right, forward)
        if direction == "left":
            return (-right, -forward)

    def space(self, direction, forward=1, right=0):
        return self._unit.position.relative_space(*self.offset(direction, forward, right))

    def unit(self, direction, forward=1, right=0):
        return self.space(direction, forward, right).unit

    def damage(self, receiver, amount):
        receiver.take_damage(amount)
        if not receiver.is_alive():
            self._unit.earn_points(receiver.max_health)

    def pass_turn(self):
        pass  # callback which is triggered every turn

    def verify_direction(self, direction):
        if direction not in RELATIVE_DIRECTIONS:
            raise ValueError(
                f"Unknown direction {direction!r}. "
                'Should be "forward", "backward", "left" or "right".'
            )
