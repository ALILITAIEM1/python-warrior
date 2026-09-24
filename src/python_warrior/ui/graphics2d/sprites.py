"""Vector-drawn sprites: every unit is drawn with pygame primitives.

No image asset is needed. Each function draws a unit centered on ``center``
for a tile of size ``tile`` facing ``direction``.
"""

import math

import pygame

from . import theme

VECTORS = {"north": (0, -1), "east": (1, 0), "south": (0, 1), "west": (-1, 0)}


def shade(color, factor):
    return tuple(max(0, min(255, int(c * factor))) for c in color)


def _facing_point(center, direction, distance):
    dx, dy = VECTORS[direction]
    return (center[0] + dx * distance, center[1] + dy * distance)


def _eyes(surface, center, direction, radius, color=(20, 20, 24)):
    dx, dy = VECTORS[direction]
    px, py = -dy, dx  # perpendicular
    look = radius * 0.35
    for side in (-1, 1):
        ex = center[0] + dx * look + px * side * radius * 0.28
        ey = center[1] + dy * look + py * side * radius * 0.28 - radius * 0.1
        pygame.draw.circle(surface, (250, 250, 250), (ex, ey), max(2, radius * 0.17))
        pygame.draw.circle(surface, color, (ex + dx * radius * 0.05, ey + dy * radius * 0.05), max(1, radius * 0.09))


def draw_warrior(surface, center, tile, direction, color):
    r = tile * 0.32
    cx, cy = center
    # sword
    tip = _facing_point(center, direction, r * 1.55)
    pygame.draw.line(surface, (220, 224, 235), center, tip, max(2, int(tile * 0.05)))
    guard = _facing_point(center, direction, r * 0.95)
    dx, dy = VECTORS[direction]
    pygame.draw.line(surface, (140, 100, 40), (guard[0] - dy * r * 0.35, guard[1] - dx * r * 0.35),
                     (guard[0] + dy * r * 0.35, guard[1] + dx * r * 0.35), max(2, int(tile * 0.05)))
    # body
    pygame.draw.circle(surface, shade(color, 0.6), (cx, cy + r * 0.08), r + 2)
    pygame.draw.circle(surface, color, center, r)
    # helmet
    helmet = pygame.Rect(0, 0, r * 1.7, r * 1.2)
    helmet.center = (cx, cy - r * 0.35)
    pygame.draw.arc(surface, (200, 205, 215), helmet, 0, math.pi, max(3, int(r * 0.35)))
    _eyes(surface, center, direction, r)


def draw_golem(surface, center, tile, direction, color):
    r = tile * 0.33
    rect = pygame.Rect(0, 0, r * 2, r * 2)
    rect.center = center
    pygame.draw.rect(surface, shade(color, 0.6), rect.move(0, 3), border_radius=int(r * 0.4))
    pygame.draw.rect(surface, color, rect, border_radius=int(r * 0.4))
    pygame.draw.line(surface, shade(color, 0.55), (rect.left + r * 0.4, rect.top + r * 0.3),
                     (rect.centerx, rect.centery + r * 0.2), 2)
    pygame.draw.line(surface, shade(color, 0.55), (rect.centerx, rect.centery + r * 0.2),
                     (rect.right - r * 0.5, rect.bottom - r * 0.3), 2)
    _eyes(surface, center, direction, r, (200, 60, 30))


def draw_sludge(surface, center, tile, direction, color, thick=False):
    r = tile * (0.36 if thick else 0.3)
    cx, cy = center
    body = pygame.Rect(0, 0, r * 2.2, r * 1.8)
    body.midbottom = (cx, cy + r * 0.95)
    pygame.draw.ellipse(surface, shade(color, 0.55), body.move(0, 3))
    pygame.draw.ellipse(surface, color, body)
    top = pygame.Rect(0, 0, r * 1.3, r * 1.2)
    top.midbottom = (cx, body.centery + r * 0.1)
    pygame.draw.ellipse(surface, color, top)
    # shine and bubbles
    pygame.draw.ellipse(surface, shade(color, 1.35), (body.left + r * 0.35, body.top + r * 0.3, r * 0.5, r * 0.3))
    if thick:
        for ox, oy in ((-0.5, 0.45), (0.55, 0.35), (0.1, 0.65)):
            pygame.draw.circle(surface, shade(color, 0.7), (cx + ox * r, cy + oy * r), r * 0.14)
    _eyes(surface, (cx, cy + r * 0.1), direction, r)


def draw_archer(surface, center, tile, direction, color):
    r = tile * 0.29
    cx, cy = center
    dx, dy = VECTORS[direction]
    # bow on the facing side
    bow_center = _facing_point(center, direction, r * 0.9)
    bow = pygame.Rect(0, 0, r * 1.6, r * 1.6)
    bow.center = bow_center
    start = math.atan2(-dy, dx) - math.pi / 2.2
    pygame.draw.arc(surface, (150, 100, 50), bow, start, start + math.pi / 1.1, max(2, int(tile * 0.045)))
    pygame.draw.circle(surface, shade(color, 0.6), (cx, cy + 3), r)
    pygame.draw.circle(surface, color, center, r)
    # hood
    hood = [(cx - r, cy - r * 0.1), (cx, cy - r * 1.45), (cx + r, cy - r * 0.1)]
    pygame.draw.polygon(surface, shade(color, 0.7), hood)
    _eyes(surface, center, direction, r)


def draw_wizard(surface, center, tile, direction, color):
    r = tile * 0.27
    cx, cy = center
    # wand
    tip = _facing_point(center, direction, r * 1.6)
    pygame.draw.line(surface, (110, 70, 40), center, tip, max(2, int(tile * 0.04)))
    pygame.draw.circle(surface, (255, 240, 140), tip, max(2, r * 0.22))
    # robe and hat
    robe = [(cx - r * 1.1, cy + r), (cx, cy - r * 0.6), (cx + r * 1.1, cy + r)]
    pygame.draw.polygon(surface, shade(color, 0.7), robe)
    pygame.draw.circle(surface, (236, 210, 180), center, r * 0.75)
    hat = [(cx - r * 0.95, cy - r * 0.35), (cx + r * 0.2, cy - r * 1.9), (cx + r * 0.95, cy - r * 0.35)]
    pygame.draw.polygon(surface, color, hat)
    pygame.draw.circle(surface, (255, 230, 120), (cx + r * 0.05, cy - r * 0.9), max(2, r * 0.14))
    _eyes(surface, center, direction, r * 0.75)


def draw_captive(surface, center, tile, direction, color):
    r = tile * 0.27
    cx, cy = center
    pygame.draw.circle(surface, shade(color, 0.6), (cx, cy + 3), r)
    pygame.draw.circle(surface, color, center, r)
    hair = pygame.Rect(0, 0, r * 2, r * 1.3)
    hair.midtop = (cx, cy - r)
    pygame.draw.ellipse(surface, (170, 90, 60), hair)
    pygame.draw.circle(surface, color, (cx, cy + r * 0.1), r * 0.8)
    _eyes(surface, (cx, cy + r * 0.1), "south", r * 0.8)


def draw_chains(surface, center, tile):
    r = tile * 0.36
    cx, cy = center
    link_w, link_h = max(4, tile * 0.1), max(3, tile * 0.07)
    for i in range(10):
        angle = i / 10 * 2 * math.pi
        rect = pygame.Rect(0, 0, link_w, link_h)
        rect.center = (cx + math.cos(angle) * r, cy + math.sin(angle) * r * 0.75 + r * 0.2)
        pygame.draw.ellipse(surface, theme.CHAIN, rect, 2)


def draw_bomb(surface, pos, tile, time, pulse):
    r = tile * 0.12 * (1 + 0.15 * pulse)
    pygame.draw.circle(surface, (30, 30, 34), pos, r)
    pygame.draw.circle(surface, (90, 90, 100), pos, r, 2)
    fuse_end = (pos[0] + r * 0.8, pos[1] - r * 1.2)
    pygame.draw.line(surface, (190, 160, 110), (pos[0] + r * 0.4, pos[1] - r * 0.8), fuse_end, 2)
    pygame.draw.circle(surface, theme.FIRE if pulse > 0.5 else (255, 230, 90), fuse_end, max(2, r * 0.35))
    if time is not None:
        label = theme.font(max(14, int(tile * 0.24)), True).render(str(time), True, (255, 235, 200))
        surface.blit(label, label.get_rect(center=(pos[0], pos[1] + 1)))


DRAWERS = {
    "Warrior": draw_warrior,
    "Golem": draw_golem,
    "Sludge": draw_sludge,
    "ThickSludge": lambda s, c, t, d, col: draw_sludge(s, c, t, d, col, thick=True),
    "Archer": draw_archer,
    "Wizard": draw_wizard,
    "Captive": draw_captive,
}


def draw_unit(surface, kind, center, tile, direction, alpha=255, flash=0.0):
    color = theme.UNIT_COLORS.get(kind, (200, 200, 200))
    if flash > 0:
        color = tuple(int(c + (255 - c) * flash * 0.8) if i == 0 else int(c * (1 - flash * 0.5))
                      for i, c in enumerate(color))
    drawer = DRAWERS.get(kind, draw_captive)
    if alpha >= 255:
        drawer(surface, center, tile, direction, color)
        return
    layer = pygame.Surface((tile * 2, tile * 2), pygame.SRCALPHA)
    drawer(layer, (tile, tile), tile, direction, color)
    layer.set_alpha(int(alpha))
    surface.blit(layer, (center[0] - tile, center[1] - tile))


def draw_stairs(surface, rect):
    steps = 4
    inner = rect.inflate(-rect.w * 0.2, -rect.h * 0.2)
    pygame.draw.rect(surface, theme.STAIRS_DARK, inner, border_radius=4)
    for i in range(steps):
        h = inner.h / steps
        w = inner.w * (1 - i / (steps + 1))
        step = pygame.Rect(0, 0, w, h - 2)
        step.bottomright = (inner.right, inner.bottom - i * h)
        pygame.draw.rect(surface, theme.STAIRS, step, border_radius=2)
        pygame.draw.line(surface, theme.STAIRS_DARK, step.topleft, step.topright, 2)


def draw_health_bar(surface, center, tile, health, max_health):
    if not max_health:
        return
    width, height = tile * 0.7, max(4, tile * 0.07)
    rect = pygame.Rect(0, 0, width, height)
    rect.center = (center[0], center[1] - tile * 0.46)
    ratio = max(0.0, min(1.0, health / max_health))
    color = theme.HP_GOOD if ratio > 0.6 else theme.HP_MID if ratio > 0.3 else theme.HP_LOW
    pygame.draw.rect(surface, theme.HP_BACK, rect.inflate(2, 2), border_radius=3)
    if ratio > 0:
        pygame.draw.rect(surface, color, (rect.x, rect.y, rect.w * ratio, rect.h), border_radius=3)
