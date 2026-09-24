"""Panels, buttons, event log and text helpers of the 2D view."""

from collections import deque

import pygame

from . import sprites, theme


def wrap(text, fnt, width):
    lines = []
    for paragraph in str(text).split("\n"):
        words, line = paragraph.split(" "), ""
        for word in words:
            candidate = f"{line} {word}".strip()
            if fnt.size(candidate)[0] <= width or not line:
                line = candidate
            else:
                lines.append(line)
                line = word
        lines.append(line)
    return lines


def draw_text(surface, text, pos, size=22, color=theme.TEXT, bold=False, anchor="topleft"):
    label = theme.font(size, bold).render(str(text), True, color)
    rect = label.get_rect(**{anchor: pos})
    surface.blit(label, rect)
    return rect


def draw_wrapped(surface, text, rect, size=21, color=theme.TEXT, spacing=2, max_lines=None):
    fnt = theme.font(size)
    y = rect.top
    lines = wrap(text, fnt, rect.w)
    if max_lines is not None:
        lines = lines[:max_lines]
    for line in lines:
        surface.blit(fnt.render(line, True, color), (rect.left, y))
        y += fnt.get_linesize() + spacing
    return y


def draw_panel(surface, rect, title=None):
    pygame.draw.rect(surface, theme.PANEL, rect, border_radius=10)
    pygame.draw.rect(surface, theme.PANEL_BORDER, rect, 1, border_radius=10)
    if title:
        draw_text(surface, title.upper(), (rect.left + 14, rect.top + 10), 18, theme.TEXT_DIM, True)
        return rect.top + 32
    return rect.top + 10


class Button:
    def __init__(self, action, label, hint=""):
        self.action = action
        self.label = label
        self.hint = hint
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.active = False

    def draw(self, surface, mouse):
        hover = self.rect.collidepoint(mouse)
        color = theme.BUTTON_ACTIVE if self.active else theme.BUTTON_HOVER if hover else theme.BUTTON
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        text_color = (30, 26, 20) if self.active else theme.TEXT
        text = self.label + (f"  [{self.hint}]" if self.hint else "")
        draw_text(surface, text, self.rect.center, 20, text_color, anchor="center")


def classify(line):
    if line.startswith("- turn"):
        return "turn"
    if "damage" in line and "takes" in line or line.endswith(" dies") or "explodes" in line:
        return "damage"
    if "health from resting" in line or "rescues" in line or "earns" in line:
        return "heal"
    if line.startswith(("Success", "CONGRATULATIONS", "Total Score", "Level Grade")):
        return "success"
    if line.startswith(("Sorry", "Error", "Traceback")):
        return "failure"
    return "info"


class LogView:
    def __init__(self, size=400):
        self.lines = deque(maxlen=size)
        self.total = 0

    def add(self, text):
        for line in str(text).rstrip("\n").split("\n"):
            self.lines.append((line, classify(line)))
            self.total += 1

    def since(self, mark):
        count = self.total - mark
        return [line for line, _ in list(self.lines)[-count:]] if count > 0 else []

    def draw(self, surface, rect):
        top = draw_panel(surface, rect, "Journal")
        fnt = theme.font(20)
        line_h = fnt.get_linesize() + 1
        capacity = max(1, (rect.bottom - top - 8) // line_h)
        visible = list(self.lines)[-capacity:]
        y = top
        for line, category in visible:
            color = theme.LOG_COLORS.get(category, theme.TEXT)
            text = line if fnt.size(line)[0] < rect.w - 28 else line[: int((rect.w - 28) / 8)] + "…"
            surface.blit(fnt.render(text, True, color), (rect.left + 14, y))
            y += line_h


def draw_side_panel(surface, rect, level, turn, warrior_view):
    y = draw_panel(surface, rect, "Guerrier")
    left, width = rect.left + 16, rect.w - 32
    if not level or not level.warrior:
        draw_wrapped(surface, "Choisissez un profil pour commencer.", pygame.Rect(left, y, width, 60), 21,
                     theme.TEXT_DIM)
        return
    warrior = level.warrior
    health = warrior_view.health if warrior_view else max(0, warrior.health)
    draw_text(surface, warrior.name, (left, y), 30, theme.TEXT, True)
    y += 30
    bar = pygame.Rect(left, y, width, 16)
    pygame.draw.rect(surface, theme.HP_BACK, bar, border_radius=6)
    ratio = max(0, min(1, health / warrior.max_health))
    color = theme.HP_GOOD if ratio > 0.6 else theme.HP_MID if ratio > 0.3 else theme.HP_LOW
    if ratio:
        pygame.draw.rect(surface, color, (bar.x, bar.y, bar.w * ratio, bar.h), border_radius=6)
    label = f"{max(0, health)} / {warrior.max_health} PV"
    draw_text(surface, label, (bar.centerx + 1, bar.centery + 1), 18, (10, 10, 14), True, "center")
    draw_text(surface, label, bar.center, 18, (255, 255, 255), True, "center")
    y += 26
    stats = [("Score", warrior.score), ("Bonus temps", level.time_bonus), ("Tour", turn)]
    col = width // 3
    for i, (label, value) in enumerate(stats):
        draw_text(surface, label, (left + i * col, y), 17, theme.TEXT_DIM)
        draw_text(surface, value, (left + i * col, y + 16), 28, theme.ACCENT, True)
    y += 54

    draw_text(surface, "CAPACITÉS", (left, y), 18, theme.TEXT_DIM, True)
    y += 22
    x0 = left
    for name in warrior.abilities:
        label = name.rstrip("!") + "()"
        is_action = name.endswith("!")
        fnt = theme.font(19)
        w = fnt.size(label)[0] + 16
        if x0 + w > left + width:
            x0 = left
            y += 26
        chip = pygame.Rect(x0, y, w, 22)
        pygame.draw.rect(surface, (78, 62, 36) if is_action else (44, 62, 88), chip, border_radius=11)
        draw_text(surface, label, chip.center, 19, theme.TEXT, anchor="center")
        x0 += w + 6
    y += 36

    draw_text(surface, f"NIVEAU {level.number} · {level.profile.tower.name.upper()}", (left, y), 18, theme.TEXT_DIM, True)
    y += 22
    y = draw_wrapped(surface, level.description or "", pygame.Rect(left, y, width, 200), 20, theme.TEXT)
    y += 6
    if level.tip:
        y = draw_wrapped(surface, "Astuce : " + level.tip, pygame.Rect(left, y, width, 200), 19, theme.TEXT_DIM)
    y += 12

    draw_text(surface, "LÉGENDE", (left, y), 18, theme.TEXT_DIM, True)
    y += 24
    seen = []
    for unit in level.floor.units if level.floor else []:
        kind = type(unit).__name__
        if kind in seen:
            continue
        seen.append(kind)
        if y > rect.bottom - 34:
            break
        sprites.draw_unit(surface, kind, (left + 14, y + 12), 34, "east")
        draw_text(surface, f"{unit.name} · {unit.max_health} PV", (left + 38, y + 3), 19)
        y += 32
    if y < rect.bottom - 30:
        sprites.draw_stairs(surface, pygame.Rect(left, y - 2, 28, 28))
        draw_text(surface, "Escalier (sortie)", (left + 38, y + 3), 19)
