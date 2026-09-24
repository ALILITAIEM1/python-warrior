"""Generates player.py (first level) and the README of each level."""

import os
import shutil

from .config import Config
from .engine.abilities import player_method


class PlayerGenerator:
    def __init__(self, level):
        self.level = level

    def generate(self):
        if self.level.number == 1:
            os.makedirs(self.level.player_path, exist_ok=True)
            shutil.copy(os.path.join(Config.templates_dir(), "player.py"), self.level.player_path)
        with open(os.path.join(self.level.player_path, "README"), "w") as f:
            f.write(self.readme())

    def readme(self):
        level = self.level
        lines = [f"Level {level.number}", "", f"{level.description}", "", f"Tip: {level.tip}", ""]
        text = "\n".join(lines) + "\n" + level.floor.character
        text += "\n  > = Stairs\n"
        for unit in level.floor.unique_units:
            text += f"  {unit.character} = {unit.name} ({unit.max_health} HP)\n"
        text += "\n\nWarrior Abilities:\n"
        for name, ability in level.warrior.abilities.items():
            text += f"\n  warrior.{player_method(name)}()\n    {ability.description}\n"
        if level.warrior.has_golem():
            text += "\n\nGolem Abilities:\n"
            for name, ability in level.warrior.base_golem().abilities.items():
                text += f"\n  golem.{player_method(name)}()\n    {ability.description}\n"
        text += "\n\nWhen you're done editing player.py, run the pywarrior command again.\n"
        return text
