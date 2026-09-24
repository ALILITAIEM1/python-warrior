#  --------
# |@   s  >|
#  --------

description("It is too dark to see anything, but you smell sludge nearby.")
tip("Use warrior.feel().is_empty() to see if there is anything in front of you, and warrior.attack() to fight it. Remember, you can only do one action (walk, attack, rest...) per turn.")
clue("Add an if/else condition using warrior.feel().is_empty() to decide whether to warrior.attack() or warrior.walk().")

time_bonus(20)
ace_score(26)
size(8, 1)
stairs(7, 0)

warrior(0, 0, "east", abilities=["feel", "attack!"])

unit("sludge", 4, 0, "west")
