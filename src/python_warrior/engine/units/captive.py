from .base import Base


class Captive(Base):
    max_health = 1
    character = "C"

    def __init__(self):
        super().__init__()
        self.bind()
