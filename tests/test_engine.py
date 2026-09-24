"""Port of the RSpec specs for Position, Space, Floor and Turn."""

import pytest

from python_warrior.engine import Floor, Turn
from python_warrior.engine.abilities import Feel
from python_warrior.engine.units import Base, Captive, Golem, Sludge, Warrior


@pytest.fixture
def position_setup():
    unit = Base()
    floor = Floor()
    floor.width, floor.height = 6, 5
    floor.add(unit, 1, 2, "north")
    return floor, unit, unit.position


class TestPosition:
    def test_rotate_clockwise(self, position_setup):
        _, _, position = position_setup
        assert position.direction == "north"
        for direction in ["east", "south", "west", "north", "east"]:
            position.rotate(1)
            assert position.direction == direction

    def test_rotate_counterclockwise(self, position_setup):
        _, _, position = position_setup
        for direction in ["west", "south", "east", "north", "west"]:
            position.rotate(-1)
            assert position.direction == direction

    def test_relative_space_in_front(self, position_setup):
        floor, _, position = position_setup
        floor.add(Base(), 1, 1)
        assert not position.relative_space(1).is_empty()

    def test_relative_space_when_rotated(self, position_setup):
        floor, _, position = position_setup
        floor.add(Base(), 2, 2)
        position.rotate(1)
        assert not position.relative_space(1).is_empty()

    def test_relative_space_diagonally(self, position_setup):
        floor, _, position = position_setup
        floor.add(Base(), 0, 1)
        assert not position.relative_space(1, -1).is_empty()

    def test_relative_space_diagonally_when_rotating(self, position_setup):
        floor, _, position = position_setup
        floor.add(Base(), 0, 1)
        position.rotate(2)
        assert not position.relative_space(-1, 1).is_empty()

    def test_move_relatively(self, position_setup):
        floor, unit, position = position_setup
        assert floor.get(1, 2) is unit
        position.move(-1, 2)
        assert floor.get(1, 2) is None
        assert floor.get(3, 3) is unit
        position.rotate(1)
        position.move(-1)
        assert floor.get(3, 3) is None
        assert floor.get(2, 3) is unit

    def test_distance_from_stairs(self, position_setup):
        floor, _, position = position_setup
        floor.place_stairs(1, 2)
        assert position.distance_from_stairs() == 0
        floor.place_stairs(0, 3)
        assert position.distance_from_stairs() == 2

    def test_relative_direction_of_stairs(self, position_setup):
        floor, _, position = position_setup
        floor.place_stairs(0, 0)
        assert position.relative_direction_of_stairs() == "forward"

    def test_relative_direction_of_space(self, position_setup):
        floor, _, position = position_setup
        assert position.relative_direction_of(floor.space(5, 3)) == "right"
        position.rotate(1)
        assert position.relative_direction_of(floor.space(1, 4)) == "right"

    def test_relative_direction(self, position_setup):
        _, _, position = position_setup
        assert position.relative_direction("north") == "forward"
        assert position.relative_direction("south") == "backward"
        assert position.relative_direction("west") == "left"
        assert position.relative_direction("east") == "right"
        position.rotate(1)
        assert position.relative_direction("north") == "left"
        position.rotate(1)
        assert position.relative_direction("north") == "backward"
        position.rotate(1)
        assert position.relative_direction("north") == "right"

    def test_space_and_distance(self, position_setup):
        floor, _, position = position_setup
        assert position.space.location == (1, 2)
        assert position.distance_of(floor.space(5, 3)) == 5
        assert position.distance_of(floor.space(4, 2)) == 3


@pytest.fixture
def floor():
    floor = Floor()
    floor.width, floor.height = 2, 3
    return floor


class TestSpace:
    def test_empty_space(self, floor):
        space = floor.space(0, 0)
        assert not space.is_enemy()
        assert not space.is_warrior()
        assert space.is_empty()
        assert not space.is_wall()
        assert not space.is_stairs()
        assert not space.is_captive()
        assert not space.is_ticking()
        assert str(space) == "nothing"

    def test_out_of_bounds(self, floor):
        space = floor.space(-1, 1)
        assert space.is_wall()
        assert not space.is_empty()
        assert str(space) == "wall"

    def test_warrior(self, floor):
        floor.add(Warrior(), 0, 0)
        space = floor.space(0, 0)
        assert space.is_warrior() and space.is_player()
        assert not space.is_enemy() and not space.is_empty()
        assert isinstance(space.unit, Warrior)

    def test_enemy_and_bound(self, floor):
        floor.add(Sludge(), 0, 0)
        space = floor.space(0, 0)
        assert space.is_enemy() and not space.is_warrior() and not space.is_empty()
        assert str(space) == "Sludge"
        space.unit.bind()
        assert space.is_captive() and not space.is_enemy()

    def test_captive(self, floor):
        captive = Captive()
        floor.add(captive, 0, 0)
        space = floor.space(0, 0)
        assert space.is_captive() and not space.is_enemy() and not space.is_ticking()
        captive.add_abilities("explode!")
        assert space.is_ticking()

    def test_golem(self, floor):
        floor.add(Golem(), 0, 0)
        space = floor.space(0, 0)
        assert space.is_golem() and space.is_player() and not space.is_enemy()

    def test_stairs(self, floor):
        floor.place_stairs(0, 0)
        assert floor.space(0, 0).is_empty() and floor.space(0, 0).is_stairs()


class TestFloor:
    def test_add_and_get(self, floor):
        unit = Base()
        floor.add(unit, 0, 1, "north")
        assert floor.get(0, 1) is unit
        unit.position = None
        assert unit not in floor.units

    def test_other_units(self, floor):
        unit, warrior = Base(), Warrior()
        floor.add(unit, 0, 0)
        floor.add(warrior, 1, 0)
        assert warrior not in floor.other_units and unit in floor.other_units

    def test_bounds(self, floor):
        assert not any(floor.out_of_bounds(x, y) for x, y in [(0, 0), (1, 0), (1, 2), (0, 2)])
        assert all(floor.out_of_bounds(x, y) for x, y in [(-1, 0), (0, -1), (0, 3), (2, 0)])
        floor.place_stairs(1, 2)
        assert floor.stairs_location == (1, 2)

    def test_character_map(self):
        floor = Floor()
        floor.width, floor.height = 3, 1
        floor.add(Warrior(), 0, 0)
        floor.place_stairs(2, 0)
        assert floor.character == " ---\n|@ >|\n ---\n"

    def test_unique_units(self):
        floor = Floor()
        floor.width, floor.height = 3, 1
        u1 = Base()
        floor.add(u1, 0, 0)
        floor.add(Base(), 1, 0)
        assert floor.unique_units == [u1]


class TestTurn:
    def test_actions(self):
        turn = Turn({"walk!": None, "attack!": None})
        assert turn.action is None
        turn.walk("forward")
        assert turn.action == ("walk!", "forward")
        with pytest.raises(RuntimeError, match="Only one action can be performed per turn."):
            turn.attack()

    def test_senses(self, floor):
        warrior = Warrior()
        floor.add(warrior, 0, 0, "south")
        turn = Turn({"feel": Feel(warrior)})
        assert turn.feel().location == (0, 1)
        assert turn.feel("backward").is_wall()

    def test_locked_abilities_are_missing(self):
        turn = Turn({"walk!": None})
        assert not hasattr(turn, "attack")
