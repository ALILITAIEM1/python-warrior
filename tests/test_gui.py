"""Headless run of the 2D interface on real levels (SDL dummy video driver)."""

import os
import shutil

import pytest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
pygame = pytest.importorskip("pygame")

from conftest import FIXTURES  # noqa: E402
from python_warrior.config import Config  # noqa: E402
from python_warrior.game import Game  # noqa: E402
from python_warrior.level import Level  # noqa: E402
from python_warrior.profile import Profile  # noqa: E402
from python_warrior.ui.graphics2d import app  # noqa: E402


class AutoBackend(app.GuiBackend):
    """Answers every dialog automatically and records what happened."""

    def __init__(self):
        super().__init__()
        self.speed_index = len(app.SPEEDS) - 1
        self.modals = []
        self.animations = 0

    def _run_modal(self, modal):
        self.modals.append(modal)
        self._frame()
        answers = {"choose": modal.get("options", [(None,)])[0][0], "ask": False, "request": "Joe"}
        if modal["message"].startswith("Session"):
            return False
        return answers[modal["kind"]]

    def _play(self, animation):
        self.animations += 1
        super()._play(animation)


def prepare(tmp_path, tower, number):
    Config.path_prefix = str(tmp_path)
    profile = Profile()
    profile.tower_path = tower
    profile.warrior_name = "Joe"
    for n in range(1, number):
        level = Level(profile, n)
        level.load_level()
        profile.abilities = list(level.warrior.abilities)
    profile.level_number = number
    os.makedirs(profile.player_path)
    shutil.copy(os.path.join(FIXTURES, "solutions", f"{tower}.py"), os.path.join(profile.player_path, "player.py"))
    profile.save()


@pytest.mark.parametrize("tower,number", [("beginner", 8), ("intermediate", 8)])
def test_gui_plays_level(tmp_path, tower, number, monkeypatch):
    monkeypatch.setattr(app, "INTRO_TIME", 0.05)
    monkeypatch.setattr(app, "TURN_PAUSE", 0.0)
    prepare(tmp_path, tower, number)
    backend = AutoBackend()
    app.run_gui(Game, backend)
    lines = [line for line, _ in backend.log.lines]
    assert "Success! You have found the stairs." in lines
    assert backend.animations > 5
    assert backend.modals[-2]["message"] == "Would you like to continue on to the next level?"


def test_gui_reports_player_errors(tmp_path, monkeypatch):
    monkeypatch.setattr(app, "INTRO_TIME", 0.05)
    prepare(tmp_path, "beginner", 1)
    with open(os.path.join(tmp_path, "pywarrior", "joe-beginner", "player.py"), "w") as f:
        f.write("class Player:\n    def play_turn(self, warrior):\n        warrior.fly()\n")
    backend = AutoBackend()
    app.run_gui(Game, backend)
    assert any("AttributeError" in line for line, _ in backend.log.lines)
