"""Turns engine events into timed animations played on the board."""

import math

import pygame

from . import theme


def ease(p):
    return p * p * (3 - 2 * p)


class Animation:
    duration = 0.25

    def update(self, p):
        pass

    def finish(self):
        self.update(1.0)

    def draw(self, surface):
        pass


class Instant(Animation):
    duration = 0.0

    def __init__(self, callback):
        self.callback = callback
        self.done = False

    def update(self, p):
        if not self.done:
            self.done = True
            self.callback()


class Pause(Animation):
    def __init__(self, duration):
        self.duration = duration


class Move(Animation):
    duration = 0.28

    def __init__(self, view, start, end):
        self.view, self.start, self.end = view, start, end

    def update(self, p):
        q = ease(p)
        self.view.x = self.start[0] + (self.end[0] - self.start[0]) * q
        self.view.y = self.start[1] + (self.end[1] - self.start[1]) * q


class Lunge(Animation):
    """Quick move toward a target and back; ``on_hit`` fires at the peak."""

    duration = 0.26

    def __init__(self, view, target, amount=0.3, on_hit=None):
        self.view, self.target, self.amount, self.on_hit = view, target, amount, on_hit
        self.hit_done = False

    def update(self, p):
        dx, dy = self.target[0] - self.view.x, self.target[1] - self.view.y
        norm = math.hypot(dx, dy) or 1
        k = math.sin(p * math.pi) * self.amount
        self.view.offset = (dx / norm * k, dy / norm * k)
        if p >= 0.5 and not self.hit_done:
            self.hit_done = True
            if self.on_hit:
                self.on_hit()
        if p >= 1:
            self.view.offset = (0.0, 0.0)


class Projectile(Animation):
    duration = 0.3

    def __init__(self, board, start, end, style, on_hit=None):
        self.board, self.start, self.end, self.style, self.on_hit = board, start, end, style, on_hit
        self.p = 0.0
        self.hit_done = False
        distance = math.hypot(end[0] - start[0], end[1] - start[1])
        self.duration = 0.12 + 0.08 * distance

    def update(self, p):
        self.p = p
        if p >= 1 and not self.hit_done:
            self.hit_done = True
            if self.on_hit:
                self.on_hit()

    def draw(self, surface):
        if self.p >= 1:
            return
        sx, sy = self.board.center(*self.start)
        ex, ey = self.board.center(*self.end)
        x, y = sx + (ex - sx) * self.p, sy + (ey - sy) * self.p
        angle = math.atan2(ey - sy, ex - sx)
        t = self.board.tile
        if self.style == "magic":
            for i in range(4):
                back = i * t * 0.08
                pos = (x - math.cos(angle) * back, y - math.sin(angle) * back)
                pygame.draw.circle(surface, (200, 140, 255) if i else (255, 240, 255), pos, max(2, t * (0.1 - i * 0.02)))
        else:
            length = t * 0.4
            tail = (x - math.cos(angle) * length, y - math.sin(angle) * length)
            pygame.draw.line(surface, (220, 200, 150), tail, (x, y), max(2, int(t * 0.035)))
            head = [(x + math.cos(angle) * t * 0.08, y + math.sin(angle) * t * 0.08),
                    (x + math.cos(angle + 2.5) * t * 0.08, y + math.sin(angle + 2.5) * t * 0.08),
                    (x + math.cos(angle - 2.5) * t * 0.08, y + math.sin(angle - 2.5) * t * 0.08)]
            pygame.draw.polygon(surface, (235, 235, 245), head)


class Fade(Animation):
    duration = 0.35

    def __init__(self, board, view, fade_in=False):
        self.board, self.view, self.fade_in = board, view, fade_in

    def update(self, p):
        self.view.alpha = 255 * (p if self.fade_in else 1 - p)
        if p >= 1 and not self.fade_in:
            self.board.remove(self.view.unit)


def build(event, board):
    """Animations for one engine event (may be empty)."""
    kind, unit = event.kind, event.unit
    view = board.view_of(unit) if unit is not None and kind not in ("level_started",) else None

    if kind == "moved" and view:
        return [Move(view, event["start"], event["end"])]

    if kind == "bumped" and view:
        return [Lunge(view, event["target"], 0.18)]

    if kind == "attacked" and view:
        target = event["target"]

        def hit():
            board.add_effect("slash", board.center(*target), 0.3, hit=event["hit"])

        return [Lunge(view, target, 0.35, hit)]

    if kind == "shot" and view:
        style = "magic" if view.kind == "Wizard" else "arrow"
        target = event["target"]
        on_hit = (lambda: board.add_effect("ring", board.center(*target), 0.3, color=(255, 220, 160))) \
            if event["hit"] else None
        return [Projectile(board, (view.x, view.y), target, style, on_hit)]

    if kind == "damaged" and view:
        def apply():
            view.health = event["health"]
            view.bound = False
            view.flash = 1.0
            board.add_effect("text", board.center(view.x, view.y), 0.9, text=f"-{event['amount']}",
                             color=theme.DAMAGE)

        return [Instant(apply), Pause(0.08)]

    if kind == "died" and view:
        view.dying = True
        return [Fade(board, view)]

    if kind == "healed" and view:
        def apply():
            view.health = event["health"]
            board.add_effect("text", board.center(view.x, view.y), 0.9, text=f"+{event['amount']}", color=theme.HEAL)

        return [Instant(apply), Pause(0.12)]

    if kind == "released" and view:
        return [Instant(lambda: setattr(view, "bound", False))]

    if kind == "bound" and view:
        def apply():
            view.bound = True
            board.add_effect("ring", board.center(view.x, view.y), 0.35, color=theme.CHAIN)

        return [Instant(apply), Pause(0.15)]

    if kind == "rescued" and view:
        return [Instant(lambda: board.add_effect("sparkle", board.center(view.x, view.y), 0.6)), Fade(board, view)]

    if kind == "pivoted" and view:
        return [Instant(lambda: setattr(view, "direction", event["direction"])), Pause(0.12)]

    if kind == "ticking" and view:
        return [Instant(lambda: setattr(view, "ticking", event["time"]))]

    if kind == "detonated":
        def boom():
            for location in event["spaces"]:
                if not board.floor.out_of_bounds(*location):
                    board.add_effect("blast", board.center(*location), 0.5)

        return [Instant(boom), Pause(0.2)]

    if kind == "exploded":
        def boom():
            board.add_effect("screen_flash", (0, 0), 0.6)
            for y in range(board.floor.height):
                for x in range(board.floor.width):
                    board.add_effect("blast", board.center(x, y), 0.7)

        return [Instant(boom), Pause(0.35)]

    if kind == "formed" and view:
        view.alpha = 0
        return [Fade(board, view, fade_in=True)]

    return []
