DIRECTIONS = ["forward", "left", "right", "backward"]


class Player:
    def __init__(self):
        self.bound = set()

    def play_turn(self, warrior):
        enemies = [d for d in DIRECTIONS if warrior.feel(d).is_enemy()]
        captives = [d for d in DIRECTIONS if warrior.feel(d).is_captive()]
        tied = [d for d in captives if warrior.feel(d).location in self.bound]
        captives = [d for d in captives if d not in tied]
        ticking = [s for s in warrior.listen() if s.is_ticking()]
        path = warrior.direction_of(ticking[0]) if ticking else None

        if len(enemies) >= 2:
            # ligoter ceux qui ne bloquent pas le chemin de la bombe
            side = [d for d in enemies if d != path]
            self.bind(warrior, side[0])
        elif ticking:
            self.defuse(warrior, path)
        elif enemies:
            warrior.attack(enemies[0])
        elif captives:
            warrior.rescue(captives[0])
        elif warrior.health() < 15 or (tied and warrior.health() < 20):
            warrior.rest()
        elif tied:
            self.bound.discard(warrior.feel(tied[0]).location)
            warrior.attack(tied[0])
        elif warrior.listen():
            self.walk_towards(warrior, warrior.direction_of(warrior.listen()[0]))
        else:
            warrior.walk(warrior.direction_of_stairs())

    def bind(self, warrior, direction):
        self.bound.add(warrior.feel(direction).location)
        warrior.bind(direction)

    def defuse(self, warrior, direction):
        space = warrior.feel(direction)
        if space.location in self.bound:
            self.bound.discard(space.location)
            warrior.attack(direction)  # ennemi ligoté sur le chemin
        elif space.is_captive():
            warrior.rescue(direction)
        elif space.is_enemy():
            warrior.attack(direction)
        else:
            self.walk_towards(warrior, direction)

    def walk_towards(self, warrior, direction):
        """Marcher vers une unité sans monter l'escalier par accident."""
        if warrior.feel(direction).is_stairs():
            for other in DIRECTIONS:
                space = warrior.feel(other)
                if space.is_empty() and not space.is_stairs():
                    return warrior.walk(other)
        warrior.walk(direction)
