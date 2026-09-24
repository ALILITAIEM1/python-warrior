#  ------
# |>a S @|
#  ------

description("You feel a wall right in front of you and an opening behind you.")
tip("You are not as effective at attacking backward. Use warrior.feel().is_wall() and warrior.pivot() to turn around.")

time_bonus(30)
ace_score(50)
size(6, 1)
stairs(0, 0)

warrior(5, 0, "east", abilities=["pivot!"])

unit("archer", 1, 0, "east")
unit("thick_sludge", 3, 0, "east")
