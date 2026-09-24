from .base import Base


class Archer(Base):
    shoot_power = 3
    max_health = 7
    character = "a"

    def __init__(self):
        super().__init__()
        self.add_abilities("shoot!", "look")

    def play_turn(self, turn):
        for direction in ("forward", "left", "right"):
            for space in turn.look(direction):
                if space.is_player():
                    turn.shoot(direction)
                    return
                elif not space.is_empty():
                    break
