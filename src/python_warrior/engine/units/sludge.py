from .base import Base


class Sludge(Base):
    attack_power = 3
    max_health = 12
    character = "s"

    def __init__(self):
        super().__init__()
        self.add_abilities("attack!", "feel")

    def play_turn(self, turn):
        for direction in ("forward", "left", "right", "backward"):
            if turn.feel(direction).is_player():
                turn.attack(direction)
                return
