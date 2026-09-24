"""Every level of both towers can be loaded, rendered and solved."""

import importlib.util
import io
import os

import pytest

from conftest import FIXTURES
from python_warrior.config import Config
from python_warrior.engine.units import Warrior
from python_warrior.level import Level
from python_warrior.player_generator import PlayerGenerator
from python_warrior.profile import Profile


def load_solution(tower):
    path = os.path.join(FIXTURES, "solutions", f"{tower}.py")
    spec = importlib.util.spec_from_file_location(f"solution_{tower}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Player


@pytest.mark.parametrize("tower", ["beginner", "intermediate"])
def test_tower_is_solvable(tower):
    Config.out_stream = io.StringIO()
    Warrior.player_class = load_solution(tower)
    profile = Profile()
    profile.tower_path = tower
    profile.warrior_name = "Tester"
    for number in range(1, 10):
        level = Level(profile, number)
        assert level.exists()
        level.play()
        assert level.passed(), f"{tower} level {number} failed"
        level.tally_points()
    assert not Level(profile, 10).exists()
    assert profile.score > 0


@pytest.mark.parametrize("tower", ["beginner", "intermediate"])
def test_readme_generation(tower):
    profile = Profile()
    profile.tower_path = tower
    profile.warrior_name = "Joe"
    for number in range(1, 10):
        level = Level(profile, number)
        level.load_level()
        readme = PlayerGenerator(level).readme()
        assert readme.startswith(f"Level {number}\n")
        assert "Warrior Abilities:" in readme and "> = Stairs" in readme
        profile.abilities = list(level.warrior.abilities)
