from .base import Base
from .golem import Golem


class Warrior(Base):
    attack_power = 5
    shoot_power = 3
    max_health = 20
    character = "@"
    player_class = None  # set by Level.load_player

    def __init__(self):
        super().__init__()
        self.score = 0
        self._name = None
        self._golem_abilities = []
        self._player = None

    def play_turn(self, turn):
        self.player.play_turn(turn)

    @property
    def player(self):
        if self._player is None:
            self._player = type(self).player_class()
        return self._player

    def earn_points(self, points):
        self.score += points
        self.say(f"earns {points} points")

    @property
    def name(self):
        return self._name if self._name else "Warrior"

    @name.setter
    def name(self, value):
        self._name = value

    def perform_turn(self):
        if self._current_turn.action is None:
            self.say("does nothing")
        super().perform_turn()

    def add_golem_abilities(self, *abilities):
        self._golem_abilities += abilities

    def has_golem(self):
        return bool(self._golem_abilities)

    def base_golem(self):
        golem = Golem()
        golem.add_abilities(*self._golem_abilities)
        return golem
