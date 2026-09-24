"""Player profile, saved as base64-encoded JSON in ``.profile``."""

import base64
import json
import os
import re

from .config import Config

FIELDS = [
    "tower_path", "warrior_name", "score", "current_epic_score", "current_epic_grades",
    "epic_score", "average_grade", "abilities", "level_number", "last_level_number", "epic",
]


class Profile:
    def __init__(self):
        self.tower_path = None
        self.warrior_name = None
        self.score = 0
        self.current_epic_score = 0
        self.current_epic_grades = {}
        self.epic_score = 0
        self.average_grade = None
        self.abilities = []
        self.level_number = 0
        self.last_level_number = None
        self.epic = False
        self._player_path = None

    def encode(self):
        data = {name: getattr(self, name) for name in FIELDS}
        data["current_epic_grades"] = {str(k): v for k, v in self.current_epic_grades.items()}
        return base64.encodebytes(json.dumps(data).encode()).decode()

    def save(self):
        self.update_epic_score()
        if self.is_epic():
            self.level_number = 0
        with open(os.path.join(self.player_path, ".profile"), "w") as f:
            f.write(self.encode())

    @classmethod
    def decode(cls, text):
        data = json.loads(base64.decodebytes(text.encode()))
        profile = cls()
        for name in FIELDS:
            if name in data:
                setattr(profile, name, data[name])
        profile.current_epic_grades = {int(k): v for k, v in profile.current_epic_grades.items()}
        return profile

    @classmethod
    def load(cls, path):
        with open(path) as f:
            profile = cls.decode(f.read())
        profile.player_path = os.path.dirname(path)
        return profile

    @property
    def player_path(self):
        return self._player_path or f"{Config.path_prefix}/pywarrior/{self.directory_name}"

    @player_path.setter
    def player_path(self, value):
        self._player_path = value

    @property
    def directory_name(self):
        return "-".join([re.sub(r"[^a-z0-9]+", "-", self.warrior_name.lower()), self.tower.name])

    def __str__(self):
        if self.is_epic():
            return " - ".join([
                self.warrior_name, self.tower.name, f"first score {self.score}",
                f"epic score {self.epic_score_with_grade()}",
            ])
        return " - ".join([self.warrior_name, self.tower.name, f"level {self.level_number}", f"score {self.score}"])

    def epic_score_with_grade(self):
        from .level import Level

        if self.average_grade:
            return f"{self.epic_score} ({Level.grade_letter(self.average_grade)})"
        return str(self.epic_score)

    @property
    def tower(self):
        from .tower import Tower

        return Tower(os.path.basename(self.tower_path))

    @property
    def current_level(self):
        from .level import Level

        return Level(self, self.level_number)

    @property
    def next_level(self):
        from .level import Level

        return Level(self, self.level_number + 1)

    def add_abilities(self, *abilities):
        for ability in abilities:
            if ability not in self.abilities:
                self.abilities.append(ability)

    def enable_epic_mode(self):
        self.epic = True
        self.epic_score = self.epic_score or 0
        self.current_epic_score = self.current_epic_score or 0
        if self.last_level_number is None:
            self.last_level_number = self.level_number

    def enable_normal_mode(self):
        self.epic = False
        self.epic_score = 0
        self.current_epic_score = 0
        self.current_epic_grades = {}
        self.average_grade = None
        self.level_number = self.last_level_number
        self.last_level_number = None

    def is_epic(self):
        return bool(self.epic)

    def is_level_after_epic(self):
        from .level import Level

        if self.last_level_number is not None:
            return Level(self, self.last_level_number + 1).exists()
        return False

    def update_epic_score(self):
        if self.current_epic_score > self.epic_score:
            self.epic_score = self.current_epic_score
            self.average_grade = self.calculate_average_grade()

    def calculate_average_grade(self):
        if self.current_epic_grades:
            return sum(self.current_epic_grades.values()) / len(self.current_epic_grades)
        return None
