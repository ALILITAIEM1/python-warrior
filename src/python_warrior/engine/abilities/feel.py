from .base import Base


class Feel(Base):
    description = 'Returns a Space for the given direction ("forward" by default).'

    def perform(self, direction="forward"):
        self.verify_direction(direction)
        return self.space(direction)
