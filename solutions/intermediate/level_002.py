DIRECTIONS = ["forward", "left", "right", "backward"]


class Player:
    def play_turn(self, warrior):
        enemies = [d for d in DIRECTIONS if warrior.feel(d).is_enemy()]
        if enemies:
            warrior.attack(enemies[0])
        elif warrior.health() < 15:
            warrior.rest()
        else:
            warrior.walk(warrior.direction_of_stairs())
