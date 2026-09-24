"""Base class of every unit on the floor."""

from ...events import emit
from ...ui import UI
from ...utils import titleize
from ..turn import Turn


class Base:
    attack_power = 0
    shoot_power = 0
    max_health = 0
    character = "?"

    def __init__(self):
        self.position = None
        self._health = None
        self._bound = False
        self._abilities = {}
        self._current_turn = None

    def earn_points(self, points):
        pass

    @property
    def health(self):
        if self._health is None:
            self._health = self.max_health
        return self._health

    @health.setter
    def health(self, value):
        self._health = value

    def take_damage(self, amount):
        if self.is_bound():
            self.unbind()
        location = self.location
        self.health -= amount
        self.say(f"takes {amount} damage, {self.health} health power left")
        emit("damaged", self, amount=amount, health=self.health, location=location)
        if self.health <= 0:
            self.position = None
            self.say("dies")
            emit("died", self, location=location)

    def is_alive(self):
        return self.position is not None

    def is_bound(self):
        return self._bound

    def unbind(self):
        self.say("released from bonds")
        self._bound = False
        emit("released", self, location=self.location)

    def bind(self):
        self._bound = True

    def say(self, msg):
        UI.puts_with_delay(f"{self.name} {msg}")
        emit("said", self, message=f"{self.name} {msg}")

    @property
    def name(self):
        return titleize(type(self).__name__)

    def __str__(self):
        return self.name

    @property
    def location(self):
        return (self.position.x, self.position.y) if self.position else None

    def add_abilities(self, *new_abilities):
        from ..abilities import ability_class

        for ability in new_abilities:
            self.abilities[ability] = ability_class(ability)(self)

    def next_turn(self):
        return Turn(self.abilities)

    def prepare_turn(self):
        self._current_turn = self.next_turn()
        self.play_turn(self._current_turn)

    def perform_turn(self):
        if self.position:
            for ability in list(self.abilities.values()):
                ability.pass_turn()
            if self._current_turn.action and not self.is_bound():
                name, *args = self._current_turn.action
                self.abilities[name].perform(*args)

    def play_turn(self, turn):
        pass  # to be overridden by subclass

    @property
    def abilities(self):
        return self._abilities
