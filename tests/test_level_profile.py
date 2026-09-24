"""Port of the RSpec specs for Level, Profile and PlayerGenerator."""

import os

import pytest

from python_warrior.config import Config
from python_warrior.engine import Floor
from python_warrior.engine.units import Base, Warrior
from python_warrior.level import Level
from python_warrior.profile import Profile


@pytest.fixture
def level():
    profile = Profile()
    level = Level(profile, 1)
    level.floor = Floor()
    return level


def test_passed_when_warrior_on_stairs(level):
    level.warrior = Warrior()
    level.floor.add(level.warrior, 0, 0, "north")
    level.floor.place_stairs(0, 0)
    assert level.passed()


def test_grades(level):
    assert level.time_bonus == 0
    assert level.grade_for(100) is None
    level.ace_score = 100
    expected = {110: "S", 100: "S", 99: "A", 89: "B", 79: "C", 69: "D", 59: "F"}
    for score, grade in expected.items():
        assert level.grade_for(score) == grade


def test_load_path(level):
    level.profile.tower_path = "path/to/tower"
    assert level.load_path == os.path.join(Config.towers_dir(), "tower", "level_001.py")


def test_setup_warrior(level):
    level.profile.abilities = ["walk!", "feel"]
    level.profile.warrior_name = "Joe"
    warrior = Warrior()
    level.setup_warrior(warrior)
    assert list(warrior.abilities) == ["walk!", "feel"] and warrior.name == "Joe"


def test_score_calculation(level):
    assert level.score_calculation(123, 45) == "123 + 45 = 168"
    assert level.score_calculation(0, 45) == "45"


def test_play_counts_down_time_bonus(level, monkeypatch):
    monkeypatch.setattr(level, "load_level", lambda: None)
    monkeypatch.setattr(level, "failed", lambda: False)
    level.floor.place_stairs(5, 5)
    calls = []
    unit = Base()
    unit.prepare_turn = lambda: calls.append("prepare")
    unit.perform_turn = lambda: calls.append("perform")
    level.floor.add(unit, 0, 0)
    level.time_bonus = 2
    turns = []
    level.play(5, on_turn=lambda: turns.append(1))
    assert level.time_bonus == 0 and len(turns) == 5
    assert calls.count("prepare") == 5 and calls.count("perform") == 5


class FakeWarrior:
    def __init__(self, score, abilities=None):
        self.score = score
        self.abilities = abilities or {}


def tally(level, score, others=True, time_bonus=0):
    level.warrior = FakeWarrior(score, {"foo": None, "bar": None})
    level.time_bonus = time_bonus
    if others:
        level.floor.add(Base(), 0, 0)
    level.tally_points()


def test_tally_normal(level):
    tally(level, 30)
    assert level.profile.score == 30
    assert set(level.profile.abilities) == {"foo", "bar"}


def test_tally_epic_with_grade(level):
    level.ace_score = 100
    level.profile.enable_epic_mode()
    tally(level, 30)
    assert level.profile.current_epic_score == 30
    assert level.profile.current_epic_grades == {1: 0.3}


def test_tally_clear_bonus(level):
    tally(level, 10, others=False, time_bonus=10)
    assert level.profile.score == 24


class TestProfile:
    def test_defaults(self):
        profile = Profile()
        assert profile.level_number == 0 and profile.score == 0 and profile.abilities == []

    def test_encode_decode(self):
        profile = Profile()
        profile.warrior_name = "Joe"
        profile.current_epic_grades = {1: 0.5}
        decoded = Profile.decode(profile.encode())
        assert decoded.warrior_name == "Joe" and decoded.current_epic_grades == {1: 0.5}

    def test_add_abilities_without_duplicates(self):
        profile = Profile()
        profile.add_abilities("foo", "bar", "blah", "bar")
        assert profile.abilities == ["foo", "bar", "blah"]

    def test_levels(self):
        profile = Profile()
        profile.level_number = 1
        assert profile.current_level.number == 1 and profile.next_level.number == 2

    def test_epic_score(self):
        profile = Profile()
        profile.enable_epic_mode()
        profile.current_epic_score = 123
        profile.current_epic_grades = {1: 0.7, 2: 0.9}
        profile.update_epic_score()
        assert profile.epic_score == 123 and profile.average_grade == pytest.approx(0.8)
        profile.current_epic_score = 100
        profile.update_epic_score()
        assert profile.epic_score == 123

    def test_normal_mode(self):
        profile = Profile()
        profile.level_number = 7
        profile.enable_epic_mode()
        assert profile.last_level_number == 7
        profile.enable_normal_mode()
        assert not profile.is_epic() and profile.level_number == 7 and profile.last_level_number is None
        assert not profile.is_level_after_epic()

    def test_string_representation(self):
        profile = Profile()
        profile.warrior_name = "Joe"
        profile.tower_path = "path/to/tower"
        assert str(profile) == "Joe - tower - level 0 - score 0"
        profile.enable_epic_mode()
        assert str(profile) == "Joe - tower - first score 0 - epic score 0"
        profile.average_grade = 0.7
        assert str(profile) == "Joe - tower - first score 0 - epic score 0 (C)"

    def test_player_path(self):
        profile = Profile()
        profile.warrior_name = "John Smith"
        profile.tower_path = "path/to/tower"
        assert profile.player_path == "./pywarrior/john-smith-tower"
        profile.player_path = "path/to/player"
        assert profile.player_path == "path/to/player"
