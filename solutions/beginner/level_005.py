class Player:
    def __init__(self):
        self.health = 20

    def play_turn(self, warrior):
        space = warrior.feel()
        hurt = warrior.health() < self.health
        if space.is_captive():
            warrior.rescue()
        elif space.is_enemy():
            warrior.attack()
        elif warrior.health() < 20 and not hurt:
            warrior.rest()
        else:
            warrior.walk()
        self.health = warrior.health()
