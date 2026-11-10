class Player:
    def __init__(self):
        self.health = 20

    def play_turn(self, warrior):
        health = warrior.health()
        hurt = health < self.health
        space = warrior.feel()

        if space.is_wall():
            warrior.pivot()                 # mur devant : on se retourne
        elif space.is_captive():
            warrior.rescue()
        elif space.is_enemy():
            warrior.attack()
        elif hurt and health < 10:
            warrior.walk("backward")        # trop faible sous les flèches : on recule
        elif not hurt and health < 20:
            warrior.rest()                  # en sécurité : on se soigne
        else:
            warrior.walk()

        self.health = warrior.health()
