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
            target = warrior.listen()[0]
            warrior.walk(warrior.direction_of(target))
        else:
            warrior.walk(warrior.direction_of_stairs())
