class Player:
    def __init__(self):
        self.health = 20

    def play_turn(self, warrior):
        hurt = warrior.health() < self.health
        if warrior.feel().is_enemy():
            warrior.attack()
        elif warrior.health() < 20 and not hurt:
            warrior.rest()
        else:
            warrior.walk()
        self.health = warrior.health()
