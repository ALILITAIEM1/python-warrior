class Player:
    def play_turn(self, warrior):
        # Premier élément visible devant nous (jusqu'à 3 cases).
        target = None
        for space in warrior.look():
            if not space.is_empty():
                target = space
                break

        if warrior.feel().is_captive():
            warrior.rescue()                # libérer le captif d'abord
        elif target is not None and target.is_enemy():
            warrior.shoot()                 # un sorcier en vue : on tire
        else:
            warrior.walk()
