"""Port of the Cucumber features: full game sessions through the CLI."""

import io
import os
import shutil

import pytest

from conftest import FIXTURES
from python_warrior.cli import run
from python_warrior.config import Config


class Session:
    def __init__(self, tmp_path):
        self.root = str(tmp_path)

    def run(self, answers="", *options):
        out = io.StringIO()
        Config.reset()
        run(["-d", self.root, "-t", "0", *options], io.StringIO(answers), out)
        self.output = out.getvalue()
        return self.output

    def player_dir(self, name):
        return os.path.join(self.root, "pywarrior", name)

    def copy_walking_player(self, name):
        shutil.copy(os.path.join(FIXTURES, "walking_player.py"), os.path.join(self.player_dir(name), "player.py"))

    def choice(self, label):
        for line in self.output.splitlines():
            if label in line and line.startswith("["):
                return line[1:line.index("]")]
        raise AssertionError(f"{label!r} not in {self.output}")


@pytest.fixture
def session(tmp_path):
    return Session(tmp_path)


@pytest.fixture
def short_tower(tmp_path, monkeypatch):
    towers = tmp_path / "towers"
    shutil.copytree(Config.towers_dir(), towers)
    shutil.copytree(os.path.join(FIXTURES, "short-tower"), towers / "short")
    original_reset = Config.reset

    def reset():
        original_reset()
        Config.towers_path = str(towers)

    monkeypatch.setattr(Config, "reset", classmethod(lambda cls: reset()))
    return towers


def create_profile(session, name, tower):
    session.run("y\n" + "\n".join(["2" if tower == "intermediate" else "1", name]) + "\n")
    assert "generated" in session.output


def test_create_profile_and_readme(session):
    create_profile(session, "Joe", "beginner")
    assert os.path.exists(os.path.join(session.player_dir("joe-beginner"), "README"))
    assert os.path.exists(os.path.join(session.player_dir("joe-beginner"), "player.py"))


def test_pass_first_level_fail_second(session):
    create_profile(session, "Joe", "beginner")
    session.copy_walking_player("joe-beginner")
    session.run("1\ny\n")
    assert "the updated README in the pywarrior/joe-beginner directory" in session.output
    session.run("1\ny\n")
    assert "Sorry, you failed level 2" in session.output
    assert "warrior.feel().is_empty()" in session.output


def test_retry_first_level(session):
    create_profile(session, "Joe", "beginner")
    session.copy_walking_player("joe-beginner")
    session.run("1\nn\n")
    assert "Staying on current level." in session.output
    session.run("")
    assert "Joe - beginner - level 1" in session.output


def test_skip_option(session):
    create_profile(session, "Joe", "beginner")
    session.copy_walking_player("joe-beginner")
    session.run("1\n", "-s")
    assert "Remove --skip option" in session.output


def test_epic_mode_with_grades(session, short_tower):
    session.run("y\n3\nBill\n")
    session.copy_walking_player("bill-short")
    session.run("1\ny\n")
    assert "the updated README in the pywarrior/bill-short directory" in session.output
    session.run("1\ny\n")
    assert "epic mode" in session.output
    session.run("1\n")
    assert "Level Grade: S" in session.output
    session.run("1\n")
    assert "grade for this tower" in session.output
    session.run("")
    assert "Bill - short - first score 34 - epic score 34" in session.output


def test_back_to_normal_mode_when_level_added(session, short_tower):
    session.run("y\n3\nBob\n")
    session.copy_walking_player("bob-short")
    session.run("1\ny\n")
    session.run("1\ny\n")
    assert "epic mode" in session.output
    shutil.copy(short_tower / "short" / "level_002.py", short_tower / "short" / "level_003.py")
    session.run("1\n")
    assert "Another level" in session.output
    session.run("1\ny\n")
    assert "epic mode" in session.output


def test_practice_level_requires_epic(session):
    create_profile(session, "Joe", "beginner")
    session.run("1\n", "-l", "2")
    assert "Unable to practice level while not in epic mode" in session.output
