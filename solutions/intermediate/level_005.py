DIRECTIONS = ["forward", "left", "right", "backward"]


class Player:
    def __init__(self):
        self.bound = set()

    def play_turn(self, warrior):
        enemies = [d for d in DIRECTIONS if warrior.feel(d).is_enemy()]
        captives = [d for d in DIRECTIONS if warrior.feel(d).is_captive()]
        tied = [d for d in captives if warrior.feel(d).location in self.bound]
        captives = [d for d in captives if d not in tied]

        if len(enemies) >= 2:
            self.bound.add(warrior.feel(enemies[0]).location)
            warrior.bind(enemies[0])
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

    def walk_towards(self, warrior, direction):
        """Marcher vers une unité sans monter l'escalier par accident."""
        if warrior.feel(direction).is_stairs():
            for other in DIRECTIONS:
                space = warrior.feel(other)
                if space.is_empty() and not space.is_stairs():
                    return warrior.walk(other)
        warrior.walk(direction)
