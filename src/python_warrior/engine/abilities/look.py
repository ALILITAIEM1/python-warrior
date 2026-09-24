from .base import Base


class Look(Base):
    description = 'Returns a list of up to three Spaces in the given direction ("forward" by default).'

    def perform(self, direction="forward"):
        self.verify_direction(direction)
        return [self.space(direction, amount) for amount in (1, 2, 3)]
