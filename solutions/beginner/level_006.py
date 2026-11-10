class Player:
    def __init__(self):
        self.health = 20
        self.captive_rescued = False

    def play_turn(self, warrior):
        health = warrior.health()
        hurt = health < self.health

        # 1. D'abord, aller libérer le captif derrière nous.
        if not self.captive_rescued:
            if warrior.feel("backward").is_captive():
                warrior.rescue("backward")
                self.captive_rescued = True
            else:
                warrior.walk("backward")

        # 2. Ennemi au contact : on attaque.
        elif warrior.feel().is_enemy():
            warrior.attack()

        # 3. Touché à distance avec peu de vie : on recule hors de portée.
        elif hurt and health < 10:
            warrior.walk("backward")

        # 4. Blessé mais en sécurité : on se repose.
        elif not hurt and health < 20:
            warrior.rest()

        # 5. Sinon on avance.
        else:
            warrior.walk()

        self.health = warrior.health()
