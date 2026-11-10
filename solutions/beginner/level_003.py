class Player:
    def play_turn(self, warrior):
        if warrior.feel().is_enemy():
            warrior.attack()
        elif warrior.health() < 20:
            warrior.rest()
        else:
            warrior.walk()
