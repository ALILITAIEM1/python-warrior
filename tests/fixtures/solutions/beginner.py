"""Reference solution passing every level of the beginner tower."""


class Player:
    def __init__(self):
        self.last_health = None
        self.direction = "backward"

    def play_turn(self, warrior):
        can = lambda name: hasattr(warrior, name)
        if not can("feel"):
            return warrior.walk()
        health = warrior.health() if can("health") else 20
        hurt = self.last_health is not None and health < self.last_health
        self.last_health = health
        if not can("rescue"):
            self.direction = "forward"

        space = warrior.feel(self.direction)
        if space.is_wall():
            if can("pivot") and self.direction == "forward":
                return warrior.pivot()
            self.direction = "forward"
            space = warrior.feel(self.direction)

        if can("pivot") and self.direction == "backward" and not space.is_empty():
            self.direction = "forward"
            return warrior.pivot()

        if space.is_captive():
            return warrior.rescue(self.direction)
        if space.is_enemy():
            return warrior.attack(self.direction)
        if can("look") and self.direction == "forward":
            for ahead in warrior.look():
                if ahead.is_captive():
                    break
                if ahead.is_enemy():
                    return warrior.shoot()
        if can("rest") and not hurt and health < 20:
            return warrior.rest()
        if (can("rescue") and hurt and health < 10 and self.direction == "forward"
                and warrior.feel("backward").is_empty()):
            return warrior.walk("backward")
        return warrior.walk(self.direction)
