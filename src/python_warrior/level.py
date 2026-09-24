"""A level of a tower: loading, playing turns and scoring."""

import importlib.util
import os

from .config import Config
from .engine.units import Warrior
from .events import emit
from .level_loader import LevelLoader
from .ui import UI
from .utils import ruby_round


class Level:
    @staticmethod
    def grade_letter(percent):
        if percent >= 1.0:
            return "S"
        if percent >= 0.9:
            return "A"
        if percent >= 0.8:
            return "B"
        if percent >= 0.7:
            return "C"
        if percent >= 0.6:
            return "D"
        return "F"

    def __init__(self, profile, number):
        self.profile = profile
        self.number = number
        self.time_bonus = 0
        self.description = None
        self.tip = None
        self.clue = None
        self.warrior = None
        self.floor = None
        self.ace_score = None

    @property
    def player_path(self):
        return self.profile.player_path

    @property
    def load_path(self):
        return os.path.join(
            Config.towers_dir(),
            os.path.basename(self.profile.tower_path),
            f"level_{self.number:03d}.py",
        )

    def load_level(self):
        with open(self.load_path) as f:
            LevelLoader(self).load(f.read(), self.load_path)

    def load_player(self):
        path = os.path.join(self.player_path, "player.py")
        spec = importlib.util.spec_from_file_location("player", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        Warrior.player_class = module.Player

    def generate_player_files(self):
        from .player_generator import PlayerGenerator

        self.load_level()
        PlayerGenerator(self).generate()

    def play(self, turns=1000, on_turn=None):
        self.load_level()
        UI.backend.level_started(self)
        emit("level_started", level=self)
        try:
            for n in range(turns):
                if self.passed() or self.failed():
                    return
                UI.puts(f"- turn {n + 1} -")
                UI.print(self.floor.character)
                UI.backend.turn_started(self, n + 1)
                units = self.floor.units
                for unit in units:
                    unit.prepare_turn()
                for unit in units:
                    unit.perform_turn()
                if on_turn:
                    on_turn()
                UI.backend.turn_finished(self, n + 1)
                if self.time_bonus > 0:
                    self.time_bonus -= 1
        finally:
            UI.backend.level_finished(self)

    def tally_points(self):
        score = 0

        UI.puts(f"Level Score: {self.warrior.score}")
        score += self.warrior.score

        UI.puts(f"Time Bonus: {self.time_bonus}")
        score += self.time_bonus

        if not self.floor.other_units:
            UI.puts(f"Clear Bonus: {self.clear_bonus()}")
            score += self.clear_bonus()

        if self.profile.is_epic():
            if self.grade_for(score):
                UI.puts(f"Level Grade: {self.grade_for(score)}")
            UI.puts("Total Score: " + self.score_calculation(self.profile.current_epic_score, score))
            if self.ace_score:
                self.profile.current_epic_grades[self.number] = score / float(self.ace_score)
            self.profile.current_epic_score += score
        else:
            UI.puts("Total Score: " + self.score_calculation(self.profile.score, score))
            self.profile.score += score
            self.profile.abilities = list(self.warrior.abilities.keys())

    def grade_for(self, score):
        if self.ace_score:
            return self.grade_letter(score / float(self.ace_score))
        return None

    def clear_bonus(self):
        return ruby_round((self.warrior.score + self.time_bonus) * 0.2)

    def score_calculation(self, current_score, addition):
        if current_score == 0:
            return str(addition)
        return f"{current_score} + {addition} = {current_score + addition}"

    def passed(self):
        return self.floor.stairs_space.is_warrior()

    def failed(self):
        return self.warrior not in self.floor.units

    def exists(self):
        return os.path.exists(self.load_path)

    def setup_warrior(self, warrior):
        self.warrior = warrior
        self.warrior.add_abilities(*self.profile.abilities)
        self.warrior.name = self.profile.warrior_name
