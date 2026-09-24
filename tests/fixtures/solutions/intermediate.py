"""Reference solution passing every level of the intermediate tower."""

DIRECTIONS = ["forward", "left", "right", "backward"]


class Player:
    def __init__(self):
        self.bound = set()
        self.script = [
            ("bind", "left"), ("bind", "right"), ("detonate", "forward"), ("detonate", "forward"),
            ("rest",), ("rest",), ("rest",), ("detonate", "forward"), ("walk", "forward"),
            ("walk", "left"), ("rescue", "forward"), ("walk", "forward"), ("walk", "forward"),
        ]

    def play_turn(self, warrior):
        can = lambda name: hasattr(warrior, name)
        if can("distance_of"):  # last level: scripted plan
            name, *args = self.script.pop(0)
            return getattr(warrior, name)(*args)
        if not can("attack"):
            return warrior.walk(warrior.direction_of_stairs())

        enemies = [d for d in DIRECTIONS if warrior.feel(d).is_enemy()]
        captives = [d for d in DIRECTIONS if warrior.feel(d).is_captive()]
        prisoners = [d for d in captives if warrior.feel(d).location in self.bound]
        captives = [d for d in captives if d not in prisoners]
        units = warrior.listen() if can("listen") else []
        ticking = [s for s in units if s.is_ticking()]

        if can("bind") and len(enemies) >= 2:
            self.bound.add(warrior.feel(enemies[-1]).location)
            return warrior.bind(enemies[-1])

        if ticking:
            target = ticking[0]
            direction = warrior.direction_of(target)
            if warrior.feel(direction).is_captive():
                return warrior.rescue(direction)
            if can("detonate") and self.detonate_safe(warrior, direction, target):
                return warrior.detonate(direction)
            if warrior.feel(direction).is_enemy():
                return warrior.attack(direction)
            return self.walk_towards(warrior, direction)

        if enemies:
            return warrior.attack(enemies[0])
        if captives:
            return warrior.rescue(captives[0])
        if warrior.health() < (20 if prisoners else 15):
            return warrior.rest()
        if prisoners:
            self.bound.discard(warrior.feel(prisoners[0]).location)
            return warrior.attack(prisoners[0])
        units = [s for s in units if s.location not in self.bound]
        if units:
            direction = warrior.direction_of(units[0])
            if warrior.feel(direction).is_captive():
                return warrior.rescue(direction)
            return self.walk_towards(warrior, direction)
        return warrior.walk(warrior.direction_of_stairs())

    def detonate_safe(self, warrior, direction, target):
        if warrior.health() <= 4:
            return False
        ahead = warrior.look(direction) if can_look(warrior) else [warrior.feel(direction)]
        return (
            len(ahead) >= 2
            and ahead[0].is_enemy()
            and ahead[1].is_enemy()
            and target.location not in [space.location for space in ahead[:2]]
            and (not hasattr(warrior, "distance_of") or warrior.distance_of(target) > 2)
        )

    def walk_towards(self, warrior, direction):
        if warrior.feel(direction).is_stairs() and warrior.listen():
            for other in DIRECTIONS:
                if other != direction and warrior.feel(other).is_empty() and not warrior.feel(other).is_stairs():
                    return warrior.walk(other)
        return warrior.walk(direction)


def can_look(warrior):
    return hasattr(warrior, "look")
