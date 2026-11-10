class Player:
    def __init__(self):
        self.health = 20
        self.explored = False  # a-t-on touché le mur du fond ?

    def play_turn(self, warrior):
        hurt = warrior.health() < self.health
        space = warrior.feel()
        if space.is_wall():
            self.explored = True
            warrior.pivot()
        elif space.is_captive():
            warrior.rescue()
        elif space.is_enemy():
            warrior.attack()
        elif self.shooter_in_sight(warrior, "backward") and not self.shooter_in_sight(warrior, "forward"):
            warrior.pivot()  # un tireur dans le dos : lui faire face
        elif self.enemy_in_sight(warrior, "forward"):
            warrior.shoot()
        elif warrior.health() < 20 and not hurt:
            warrior.rest()
        elif space.is_stairs() and not self.explored:
            warrior.pivot()  # ne pas partir avant d'avoir tout nettoyé
        else:
            warrior.walk()
        self.health = warrior.health()

    def enemy_in_sight(self, warrior, direction):
        for space in warrior.look(direction):
            if space.is_captive():
                return False  # ne jamais tirer à travers un captif
            if space.is_enemy():
                return True
        return False

    def shooter_in_sight(self, warrior, direction):
        """Le premier occupant visible est-il un archer (a) ou un sorcier (w) ?"""
        for space in warrior.look(direction):
            if not space.is_empty():
                return space.is_enemy() and space.character in "aw"
        return False
