"""Port of the RSpec specs for units and abilities."""

import pytest

from python_warrior.engine import Floor
from python_warrior.engine.abilities import (Attack, Bind, Detonate, Explode, Form, Listen, Look,
                                             Pivot, Rescue, Rest, Shoot, Walk)
from python_warrior.engine.units import (Archer, Base, Captive, Golem, Sludge, ThickSludge,
                                         Warrior, Wizard)
from python_warrior.events import bus


@pytest.fixture
def floor():
    floor = Floor()
    floor.width, floor.height = 6, 3
    return floor


def test_unit_stats():
    assert (Warrior().max_health, Warrior().attack_power, Warrior().shoot_power) == (20, 5, 3)
    assert (Sludge().max_health, Sludge().attack_power, Sludge().character) == (12, 3, "s")
    assert (ThickSludge().max_health, ThickSludge().character, ThickSludge().name) == (24, "S", "Thick Sludge")
    assert (Archer().max_health, Archer().shoot_power, Archer().character) == (7, 3, "a")
    assert (Wizard().max_health, Wizard().shoot_power, Wizard().character) == (3, 11, "w")
    assert (Captive().max_health, Captive().is_bound(), Captive().character) == (1, True, "C")
    assert (Golem().attack_power, Golem().character) == (3, "G")


def test_take_damage_and_die(floor):
    unit = Sludge()
    floor.add(unit, 0, 0)
    unit.take_damage(5)
    assert unit.health == 7 and unit.is_alive()
    unit.take_damage(7)
    assert not unit.is_alive()


def test_damage_unbinds(floor):
    unit = Sludge()
    floor.add(unit, 0, 0)
    unit.bind()
    unit.take_damage(1)
    assert not unit.is_bound()


def test_warrior_name_and_points():
    warrior = Warrior()
    assert warrior.name == "Warrior"
    warrior.name = "Joe"
    assert str(warrior) == "Joe"
    warrior.earn_points(5)
    assert warrior.score == 5


def test_attack_forward_and_backward(floor):
    warrior = Warrior()
    floor.add(warrior, 1, 0, "east")
    front, back = Sludge(), Sludge()
    floor.add(front, 2, 0)
    floor.add(back, 0, 0)
    Attack(warrior).perform()
    assert front.health == 7
    Attack(warrior).perform("backward")
    assert back.health == 9  # ceil(5 / 2) = 3


def test_attack_awards_points_on_kill(floor):
    warrior = Warrior()
    floor.add(warrior, 1, 0, "east")
    floor.add(Captive(), 2, 0)
    Attack(warrior).perform()
    assert warrior.score == 1


def test_attack_nothing(floor):
    warrior = Warrior()
    floor.add(warrior, 1, 0, "east")
    Attack(warrior).perform()


def test_invalid_direction(floor):
    warrior = Warrior()
    floor.add(warrior, 1, 0, "east")
    with pytest.raises(ValueError, match="Unknown direction"):
        Walk(warrior).perform("up")


def test_walk_and_bump(floor):
    warrior = Warrior()
    floor.add(warrior, 0, 0, "east")
    Walk(warrior).perform()
    assert warrior.location == (1, 0)
    floor.add(Sludge(), 2, 0)
    Walk(warrior).perform()
    assert warrior.location == (1, 0)


def test_rest(floor):
    warrior = Warrior()
    rest = Rest(warrior)
    warrior.health = 10
    rest.perform()
    assert warrior.health == 12
    warrior.health = 19
    rest.perform()
    assert warrior.health == 20
    rest.perform()
    assert warrior.health == 20


def test_shoot_first_unit_only(floor):
    warrior = Warrior()
    floor.add(warrior, 0, 0, "east")
    first, second = Sludge(), Sludge()
    floor.add(first, 2, 0)
    floor.add(second, 3, 0)
    Shoot(warrior).perform()
    assert first.health == 9 and second.health == 12
    Shoot(warrior).perform("backward")


def test_look_returns_three_spaces(floor):
    warrior = Warrior()
    floor.add(warrior, 0, 0, "east")
    assert [s.location for s in Look(warrior).perform()] == [(1, 0), (2, 0), (3, 0)]


def test_listen(floor):
    warrior = Warrior()
    floor.add(warrior, 0, 0)
    floor.add(Base(), 0, 1)
    assert len(Listen(warrior).perform()) == 1


def test_rescue_and_bind(floor):
    warrior = Warrior()
    floor.add(warrior, 0, 0, "east")
    captive = Captive()
    floor.add(captive, 1, 0)
    Rescue(warrior).perform()
    assert not captive.is_alive() and warrior.score == 20
    sludge = Sludge()
    floor.add(sludge, 1, 0)
    Bind(warrior).perform()
    assert sludge.is_bound()
    Rescue(warrior).perform()
    assert not sludge.is_bound() and sludge.is_alive() and warrior.score == 20


def test_pivot(floor):
    warrior = Warrior()
    floor.add(warrior, 0, 0, "east")
    Pivot(warrior).perform()
    assert warrior.position.direction == "west"
    Pivot(warrior).perform("right")
    assert warrior.position.direction == "north"


def test_explode(floor):
    captive = Captive()
    floor.add(captive, 0, 0)
    unit = Base()
    unit.health = 20
    floor.add(unit, 0, 1)
    captive.health = 10
    explode = Explode(captive)
    explode.time = 3
    explode.pass_turn()
    explode.pass_turn()
    assert captive.health == 10
    explode.pass_turn()
    assert captive.health == -90 and unit.health == -80


def test_detonate(floor):
    warrior = Warrior()
    floor.add(warrior, 0, 1, "east")
    center, side, behind = Sludge(), Sludge(), Sludge()
    floor.add(center, 1, 1)
    floor.add(side, 1, 0)
    floor.add(behind, 2, 1)
    Detonate(warrior).perform()
    assert (center.health, side.health, behind.health, warrior.health) == (4, 8, 8, 16)


def test_detonate_triggers_ticking_captive(floor):
    warrior = Warrior()
    floor.add(warrior, 0, 1, "east")
    captive = Captive()
    captive.add_abilities("explode!")
    floor.add(captive, 1, 1)
    Detonate(warrior).perform()
    assert not warrior.is_alive()


def test_form_golem(floor):
    warrior = Warrior()
    floor.add(warrior, 0, 0, "east")
    warrior.health = 19
    seen = []
    Form(warrior).perform("forward", seen.append)
    golem = floor.get(1, 0)
    assert isinstance(golem, Golem)
    assert warrior.health == 10 and golem.max_health == 9
    assert golem.position.direction == "east"
    golem.play_turn("turn")
    assert seen == ["turn"]
    Form(warrior).perform("forward")
    assert len(floor.units) == 2


def test_events_are_emitted(floor):
    events = []
    bus.subscribe(events.append)
    warrior = Warrior()
    floor.add(warrior, 0, 0, "east")
    floor.add(Captive(), 2, 0)
    Walk(warrior).perform()
    Attack(warrior).perform()
    kinds = [e.kind for e in events if e.kind != "said"]
    assert kinds == ["moved", "attacked", "released", "damaged", "died"]
    assert events[1].unit is warrior and events[1]["end"] == (1, 0)


def test_sludge_attacks_player(floor):
    warrior = Warrior()
    sludge = Sludge()
    floor.add(warrior, 0, 0, "east")
    floor.add(sludge, 1, 0, "west")
    sludge.prepare_turn()
    sludge.perform_turn()
    assert warrior.health == 17


def test_archer_shoots_player_in_range(floor):
    warrior = Warrior()
    archer = Archer()
    floor.add(warrior, 0, 0, "east")
    floor.add(archer, 3, 0, "west")
    archer.prepare_turn()
    archer.perform_turn()
    assert warrior.health == 17
