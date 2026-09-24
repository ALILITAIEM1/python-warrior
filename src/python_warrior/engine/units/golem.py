from .base import Base


class Golem(Base):
    attack_power = 3
    character = "G"

    def __init__(self):
        super().__init__()
        self.turn = None

    def play_turn(self, turn):
        if self.turn:
            self.turn(turn)
