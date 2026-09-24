"""The board: a view model of the floor, drawn as tiles and sprites.

The engine state changes instantly during a turn; the board keeps its own
copy of every unit (position, health, bonds...) so events can be replayed
as animations, then it is re-synchronised with the real floor.
"""

import math
from dataclasses import dataclass, field

import pygame

from . import sprites, theme


@dataclass
class UnitView:
    unit: object
    kind: str
    x: float
    y: float
    direction: str
    health: int
    max_health: int
    bound: bool = False
    ticking: object = None
    alpha: float = 255.0
    flash: float = 0.0
    offset: tuple = (0.0, 0.0)
    dying: bool = False


@dataclass
class Effect:
    """Short-lived visual effect drawn over the board (non blocking)."""

    kind: str
    pos: tuple
    life: float
    data: dict = field(default_factory=dict)
    age: float = 0.0

    @property
    def progress(self):
        return min(1.0, self.age / self.life)


def unit_state(unit):
    explode = unit.abilities.get("explode!")
    return dict(
        x=unit.position.x,
        y=unit.position.y,
        direction=unit.position.direction,
        health=unit.health,
        max_health=unit.max_health,
        bound=unit.is_bound(),
        ticking=explode.time if explode is not None else None,
    )


class Board:
    def __init__(self):
        self.floor = None
        self.views = {}
        self.effects = []
        self.rect = pygame.Rect(0, 0, 100, 100)
        self.tile = 64
        self.origin = (0, 0)
        self.clock = 0.0

    # --- model -----------------------------------------------------------

    def load(self, floor):
        self.floor = floor
        self.views = {}
        self.effects = []
        self.sync()
        self.layout(self.rect)

    def sync(self):
        if not self.floor:
            return
        alive = set()
        for unit in self.floor.units:
            alive.add(id(unit))
            state = unit_state(unit)
            view = self.views.get(id(unit))
            if view is None:
                self.views[id(unit)] = UnitView(unit=unit, kind=type(unit).__name__, **state)
            else:
                for key, value in state.items():
                    setattr(view, key, value)
                view.alpha, view.flash, view.offset, view.dying = 255.0, 0.0, (0.0, 0.0), False
        for key in [k for k in self.views if k not in alive]:
            del self.views[key]

    def view_of(self, unit):
        view = self.views.get(id(unit))
        if view is None and unit.position is not None:
            self.views[id(unit)] = view = UnitView(unit=unit, kind=type(unit).__name__, **unit_state(unit))
        return view

    def remove(self, unit):
        self.views.pop(id(unit), None)

    # --- geometry --------------------------------------------------------

    def layout(self, rect):
        self.rect = pygame.Rect(rect)
        if not self.floor:
            return
        cols, rows = self.floor.width + 1, self.floor.height + 1  # +1: half a wall on each side
        self.tile = int(max(24, min(110, self.rect.w / cols, self.rect.h / rows)))
        width, height = self.floor.width * self.tile, self.floor.height * self.tile
        self.origin = (self.rect.centerx - width // 2, self.rect.centery - height // 2)

    def center(self, x, y):
        return (self.origin[0] + (x + 0.5) * self.tile, self.origin[1] + (y + 0.5) * self.tile)

    def tile_rect(self, x, y):
        return pygame.Rect(self.origin[0] + x * self.tile, self.origin[1] + y * self.tile, self.tile, self.tile)

    # --- effects ---------------------------------------------------------

    def add_effect(self, kind, pos, life, **data):
        self.effects.append(Effect(kind, pos, life, data))

    def update(self, dt):
        self.clock += dt
        for effect in self.effects:
            effect.age += dt
        self.effects = [e for e in self.effects if e.age < e.life]
        for view in self.views.values():
            if view.flash > 0:
                view.flash = max(0.0, view.flash - dt * 3)

    # --- drawing ---------------------------------------------------------

    def draw(self, surface):
        if not self.floor:
            return
        self._draw_walls(surface)
        self._draw_floor(surface)
        views = sorted(self.views.values(), key=lambda v: v.y)
        for view in views:
            self._draw_unit(surface, view)
        for effect in self.effects:
            self._draw_effect(surface, effect)

    def _draw_walls(self, surface):
        t = self.tile
        w, h = self.floor.width * t, self.floor.height * t
        border = max(10, t // 3)
        outer = pygame.Rect(self.origin[0] - border, self.origin[1] - border, w + border * 2, h + border * 2)
        pygame.draw.rect(surface, theme.WALL_MORTAR, outer, border_radius=6)
        brick_w, brick_h = max(12, t // 3), max(6, border // 2)
        clip = surface.get_clip()
        surface.set_clip(outer)
        for row, y in enumerate(range(outer.top, outer.bottom, brick_h)):
            shift = (brick_w // 2) if row % 2 else 0
            for x in range(outer.left - shift, outer.right, brick_w):
                brick = pygame.Rect(x + 1, y + 1, brick_w - 2, brick_h - 2)
                shade = 0.85 + 0.15 * ((x * 7 + y * 13) % 5) / 4
                pygame.draw.rect(surface, sprites.shade(theme.WALL_BRICK, shade), brick)
        surface.set_clip(clip)

    def _draw_floor(self, surface):
        stairs = self.floor.stairs_location
        for y in range(self.floor.height):
            for x in range(self.floor.width):
                rect = self.tile_rect(x, y)
                color = theme.FLOOR_A if (x + y) % 2 == 0 else theme.FLOOR_B
                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, theme.FLOOR_LINE, rect, 1)
                if (x, y) == tuple(stairs):
                    sprites.draw_stairs(surface, rect)

    def _draw_unit(self, surface, view):
        cx, cy = self.center(view.x + view.offset[0], view.y + view.offset[1])
        bob = math.sin(self.clock * 3 + id(view.unit) % 7) * self.tile * 0.015
        center = (cx, cy + bob)
        # shadow
        shadow = pygame.Rect(0, 0, self.tile * 0.6, self.tile * 0.18)
        shadow.center = (cx, cy + self.tile * 0.36)
        pygame.draw.ellipse(surface, (40, 38, 34), shadow)
        sprites.draw_unit(surface, view.kind, center, self.tile, view.direction, view.alpha, view.flash)
        if view.bound and view.alpha > 0:
            sprites.draw_chains(surface, center, self.tile)
        if view.ticking is not None and view.alpha > 0:
            pulse = (math.sin(self.clock * 8) + 1) / 2
            sprites.draw_bomb(surface, (cx + self.tile * 0.3, cy + self.tile * 0.25), self.tile, view.ticking, pulse)
        if view.alpha > 128 and view.kind != "Captive":
            sprites.draw_health_bar(surface, (cx, cy), self.tile, view.health, view.max_health)

    def _draw_effect(self, surface, effect):
        p = effect.progress
        t = self.tile
        if effect.kind == "text":
            x, y = effect.pos
            label = theme.font(max(18, int(t * 0.34)), True).render(effect.data["text"], True, effect.data["color"])
            label.set_alpha(int(255 * (1 - p ** 2)))
            surface.blit(label, label.get_rect(center=(x, y - t * 0.5 - p * t * 0.5)))
        elif effect.kind == "slash":
            x, y = effect.pos
            r = t * 0.35
            color = (255, 255, 255) if effect.data.get("hit", True) else (160, 160, 170)
            for i in range(3):
                off = (i - 1) * r * 0.35
                start = (x - r + off, y - r * (1 - p))
                end = (x + r * (1 - p) + off, y + r)
                pygame.draw.line(surface, color, start, end, max(2, int(t * 0.04 * (1 - p) + 1)))
        elif effect.kind == "blast":
            x, y = effect.pos
            r = t * (0.2 + 0.6 * p)
            layer = pygame.Surface((t * 2, t * 2), pygame.SRCALPHA)
            pygame.draw.circle(layer, (*theme.FIRE, int(220 * (1 - p))), (t, t), r)
            pygame.draw.circle(layer, (255, 240, 170, int(255 * (1 - p))), (t, t), r * 0.55)
            surface.blit(layer, (x - t, y - t))
        elif effect.kind == "sparkle":
            x, y = effect.pos
            for i in range(8):
                angle = i / 8 * 2 * math.pi + p
                d = t * 0.2 + t * 0.35 * p
                pos = (x + math.cos(angle) * d, y + math.sin(angle) * d)
                pygame.draw.circle(surface, (255, 236, 140), pos, max(1, t * 0.05 * (1 - p)))
        elif effect.kind == "ring":
            x, y = effect.pos
            pygame.draw.circle(surface, effect.data.get("color", theme.CHAIN), (x, y),
                               t * (0.3 + 0.25 * p), max(1, int(4 * (1 - p)) + 1))
        elif effect.kind == "screen_flash":
            layer = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            layer.fill((255, 170, 60, int(160 * (1 - p))))
            surface.blit(layer, (0, 0))
