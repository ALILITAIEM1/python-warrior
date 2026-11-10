class Player:
    def play_turn(self, warrior):
        if warrior.feel().is_empty():
            warrior.walk()
        else:
            warrior.attack()
