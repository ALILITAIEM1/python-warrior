"""The pygame application: a UI backend driving the unchanged game flow.

``Game`` stays sequential (it asks questions and plays levels). The
graphical backend answers these calls with modal dialogs and replays each
turn's engine events as animations, pumping the pygame loop meanwhile.
"""

import traceback

import pygame

from ...config import Config
from ...events import bus
from ..base import Backend, UI
from . import animations, theme
from .board import Board
from .hud import Button, LogView, draw_panel, draw_side_panel, draw_text, draw_wrapped, wrap

SPEEDS = [0.25, 0.5, 1.0, 2.0, 4.0, 8.0]
TURN_PAUSE = 0.35
INTRO_TIME = 2.6


class QuitRequested(Exception):
    """The window was closed."""


class GuiBackend(Backend):
    def __init__(self, size=theme.WINDOW_SIZE):
        pygame.init()
        pygame.display.set_caption("Python Warrior")
        self.screen = pygame.display.set_mode(size)
        self.clock = pygame.time.Clock()
        self.board = Board()
        self.log = LogView()
        self.level = None
        self.turn = 0
        self.speed_index = 2
        self.paused = False
        self.step_requested = False
        self.in_turn = False
        self.queue = []
        self.current = None  # animation being played
        self.overlay = None  # intro card / result banner
        self.modal = None
        self.context_mark = 0
        self.quitting = False
        self.buttons = [
            Button("pause", "Pause", "Espace"),
            Button("step", "Pas à pas", "N"),
            Button("slower", "Plus lent", "-"),
            Button("faster", "Plus vite", "+"),
            Button("quit", "Quitter", "Échap"),
        ]
        self._layout()
        bus.subscribe(self._on_event)

    # --- layout ------------------------------------------------------------

    def _layout(self):
        w, h = self.screen.get_size()
        side_w = 360
        self.header_rect = pygame.Rect(16, 10, w - 32, 50)
        self.board_rect = pygame.Rect(16, 68, w - side_w - 44, int(h * 0.56))
        self.side_rect = pygame.Rect(w - side_w - 16, 68, side_w, h - 84)
        log_top = self.board_rect.bottom + 12
        self.log_rect = pygame.Rect(16, log_top, self.board_rect.w, h - log_top - 72)
        self.controls_rect = pygame.Rect(16, h - 58, self.board_rect.w, 44)
        self.board.layout(self.board_rect.inflate(-40, -40))
        gap = 8
        bw = (self.controls_rect.w - gap * (len(self.buttons) - 1)) // len(self.buttons)
        for i, button in enumerate(self.buttons):
            button.rect = pygame.Rect(self.controls_rect.left + i * (bw + gap), self.controls_rect.top, bw, 44)

    @property
    def speed(self):
        return SPEEDS[self.speed_index]

    # --- Backend API -----------------------------------------------------------

    def puts(self, msg):
        if self.in_turn:
            self.queue.append(("log", str(msg)))
        else:
            self.log.add(msg)
            self._frame()

    def print(self, msg):
        pass  # the ASCII floor is replaced by the board

    def gets(self):
        return ""

    def request(self, msg):
        return self._run_modal({"kind": "request", "message": msg.strip(), "text": ""})

    def ask(self, msg):
        return self._run_modal({"kind": "ask", "message": msg, "options": [(True, "Oui", "O"), (False, "Non", "N")]})

    def choose(self, item, options):
        if len(options) == 1:
            response = options[0]
            return response[0] if isinstance(response, tuple) else response
        entries = [(option[0] if isinstance(option, tuple) else option,
                    option[-1] if isinstance(option, tuple) else str(option), str(i + 1))
                   for i, option in enumerate(options)]
        title = {"profile": "Choisissez un profil", "tower": "Choisissez une tour"}.get(item, f"Choisissez : {item}")
        return self._run_modal({"kind": "choose", "message": title, "options": entries})

    def level_started(self, level):
        self.level = level
        self.turn = 0
        self.board.load(level.floor)
        self.board.layout(self.board_rect.inflate(-40, -40))
        self.log.add(f"=== Niveau {level.number} ===")
        self._show_overlay({"kind": "intro", "level": level}, INTRO_TIME)

    def turn_started(self, level, number):
        self.turn = number
        self.board.sync()
        while self.paused and not self.step_requested:
            self._frame()
        self.step_requested = False
        self.queue = []
        self.in_turn = True

    def turn_finished(self, level, number):
        self.in_turn = False
        queue, self.queue = self.queue, []
        for kind, item in queue:
            if kind == "log":
                self.log.add(item)
            else:
                for animation in animations.build(item, self.board):
                    self._play(animation)
        self.board.sync()
        self.wait(TURN_PAUSE)

    def level_finished(self, level):
        if self.quitting:
            return
        try:
            passed = level.passed()
        except Exception:
            passed = False
        self.board.sync()
        self._show_overlay({"kind": "result", "passed": passed}, 1.4)
        self.context_mark = self.log.total

    def wait(self, seconds):
        elapsed = 0.0
        while elapsed < seconds / self.speed:
            elapsed += self._frame()

    # --- engine events ------------------------------------------------------

    def _on_event(self, event):
        if self.in_turn and event.kind not in ("said", "level_started"):
            self.queue.append(("event", event))

    # --- main loop pieces -----------------------------------------------------

    def _play(self, animation):
        duration = animation.duration / self.speed
        if duration <= 0:
            animation.update(1.0)
            return
        self.current = animation
        elapsed = 0.0
        while elapsed < duration:
            animation.update(min(1.0, elapsed / duration))
            elapsed += self._frame()
        animation.finish()
        self.current = None

    def _show_overlay(self, overlay, seconds):
        self.overlay = dict(overlay, skip=False)
        elapsed = 0.0
        while elapsed < seconds / min(self.speed, 2.0) and not self.overlay["skip"]:
            elapsed += self._frame()
        self.overlay = None

    def _run_modal(self, modal):
        modal.update(result=None, done=False, selected=0,
                     context=[line for line in self.log.since(self.context_mark) if line.strip()][-7:])
        self.modal = modal
        if modal["kind"] == "request":
            pygame.key.start_text_input()
        while not modal["done"]:
            self._frame()
        if modal["kind"] == "request":
            pygame.key.stop_text_input()
        self.modal = None
        self.context_mark = self.log.total
        return modal["result"]

    def _frame(self):
        self._handle_events()
        self._draw()
        pygame.display.flip()
        dt = self.clock.tick(theme.FPS) / 1000.0
        self.board.update(dt * min(self.speed, 3.0))
        return dt

    # --- input ------------------------------------------------------------------

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quitting = True
                raise QuitRequested()
            if self.modal:
                self._modal_event(event)
            elif event.type == pygame.KEYDOWN:
                self._key(event)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.overlay:
                    self.overlay["skip"] = True
                for button in self.buttons:
                    if button.rect.collidepoint(event.pos):
                        self._action(button.action)

    def _key(self, event):
        if self.overlay and event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER):
            self.overlay["skip"] = True
            return
        actions = {
            pygame.K_SPACE: "pause", pygame.K_p: "pause", pygame.K_n: "step", pygame.K_RIGHT: "step",
            pygame.K_MINUS: "slower", pygame.K_KP_MINUS: "slower", pygame.K_DOWN: "slower",
            pygame.K_PLUS: "faster", pygame.K_EQUALS: "faster", pygame.K_KP_PLUS: "faster", pygame.K_UP: "faster",
            pygame.K_ESCAPE: "quit", pygame.K_q: "quit",
        }
        if event.key in actions:
            self._action(actions[event.key])

    def _action(self, action):
        if action == "pause":
            self.paused = not self.paused
        elif action == "step":
            self.paused = True
            self.step_requested = True
        elif action == "slower":
            self.speed_index = max(0, self.speed_index - 1)
        elif action == "faster":
            self.speed_index = min(len(SPEEDS) - 1, self.speed_index + 1)
        elif action == "quit":
            self.quitting = True
            raise QuitRequested()

    def _modal_event(self, event):
        modal = self.modal
        if modal["kind"] == "request":
            if event.type == pygame.TEXTINPUT:
                modal["text"] += event.text
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    modal["text"] = modal["text"][:-1]
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and modal["text"].strip():
                    self._close_modal(modal["text"].strip())
            elif event.type == pygame.MOUSEBUTTONDOWN and modal.get("ok_rect") and modal["ok_rect"].collidepoint(event.pos):
                if modal["text"].strip():
                    self._close_modal(modal["text"].strip())
            return
        options = modal["options"]
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_LEFT):
                modal["selected"] = (modal["selected"] - 1) % len(options)
            elif event.key in (pygame.K_DOWN, pygame.K_RIGHT, pygame.K_TAB):
                modal["selected"] = (modal["selected"] + 1) % len(options)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self._close_modal(options[modal["selected"]][0])
            elif modal["kind"] == "ask" and event.key in (pygame.K_y, pygame.K_o):
                self._close_modal(True)
            elif modal["kind"] == "ask" and event.key in (pygame.K_n, pygame.K_ESCAPE):
                self._close_modal(False)
            elif event.unicode and event.unicode.isdigit():
                index = int(event.unicode) - 1
                if 0 <= index < len(options):
                    self._close_modal(options[index][0])
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(modal.get("rects", [])):
                if rect.collidepoint(event.pos):
                    self._close_modal(options[i][0])
        elif event.type == pygame.MOUSEMOTION:
            for i, rect in enumerate(modal.get("rects", [])):
                if rect.collidepoint(event.pos):
                    modal["selected"] = i

    def _close_modal(self, result):
        self.modal["result"] = result
        self.modal["done"] = True

    # --- drawing ------------------------------------------------------------------

    def _draw(self):
        screen = self.screen
        screen.fill(theme.BACKGROUND)
        self._draw_header(screen)
        draw_panel(screen, self.board_rect)
        clip = screen.get_clip()
        screen.set_clip(self.board_rect.inflate(-4, -4))
        if self.level:
            self.board.draw(screen)
            if self.current:
                self.current.draw(screen)
        else:
            self._draw_splash(screen)
        screen.set_clip(clip)
        warrior_view = self.board.views.get(id(self.level.warrior)) if self.level and self.level.warrior else None
        draw_side_panel(screen, self.side_rect, self.level, self.turn, warrior_view)
        self.log.draw(screen, self.log_rect)
        mouse = pygame.mouse.get_pos()
        for button in self.buttons:
            button.active = (button.action == "pause" and self.paused)
            button.label = {"pause": "Lecture" if self.paused else "Pause"}.get(button.action, button.label)
            button.draw(screen, mouse)
        if self.overlay:
            self._draw_overlay(screen)
        if self.modal:
            self._draw_modal(screen)

    def _draw_header(self, screen):
        rect = self.header_rect
        draw_text(screen, "PYTHON WARRIOR", (rect.left, rect.centery), 40, theme.ACCENT, True, "midleft")
        if self.level:
            info = f"{self.level.profile.tower.name.capitalize()}  ·  Niveau {self.level.number}  ·  Tour {self.turn}"
            draw_text(screen, info, (rect.left + 330, rect.centery), 26, theme.TEXT, anchor="midleft")
        state = "EN PAUSE" if self.paused else f"Vitesse x{self.speed:g}"
        draw_text(screen, state, (self.board_rect.right, rect.centery), 24,
                  theme.ACCENT if self.paused else theme.TEXT_DIM, True, "midright")

    def _draw_splash(self, screen):
        rect = self.board_rect
        draw_text(screen, "Python Warrior", (rect.centerx, rect.centery - 40), 72, theme.ACCENT, True, "center")
        draw_text(screen, "Programmez votre guerrier en Python pour atteindre le sommet de la tour.",
                  (rect.centerx, rect.centery + 20), 24, theme.TEXT_DIM, anchor="center")

    def _card(self, screen, width, height, border=theme.ACCENT):
        shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        shade.fill((8, 9, 14, 170))
        screen.blit(shade, (0, 0))
        card = pygame.Rect(0, 0, width, height)
        card.center = (screen.get_width() // 2, screen.get_height() // 2)
        pygame.draw.rect(screen, theme.PANEL, card, border_radius=14)
        pygame.draw.rect(screen, border, card, 2, border_radius=14)
        return card

    def _draw_overlay(self, screen):
        overlay = self.overlay
        if overlay["kind"] == "intro":
            level = overlay["level"]
            fnt = theme.font(24)
            text = level.description or ""
            lines = len(wrap(text, fnt, 560)) + (len(wrap("Astuce : " + (level.tip or ""), theme.font(22), 560)) if level.tip else 0)
            card = self._card(screen, 620, 150 + lines * 24)
            draw_text(screen, f"Niveau {level.number}", (card.centerx, card.top + 40), 48, theme.ACCENT, True, "center")
            y = draw_wrapped(screen, text, pygame.Rect(card.left + 30, card.top + 76, 560, 200), 24)
            if level.tip:
                draw_wrapped(screen, "Astuce : " + level.tip, pygame.Rect(card.left + 30, y + 8, 560, 200), 22, theme.TEXT_DIM)
            draw_text(screen, "Espace ou clic pour commencer", (card.centerx, card.bottom - 20), 18, theme.TEXT_DIM,
                      anchor="center")
        elif overlay["kind"] == "result":
            passed = overlay["passed"]
            color = theme.LOG_COLORS["success"] if passed else theme.LOG_COLORS["failure"]
            card = self._card(screen, 460, 110, color)
            draw_text(screen, "Niveau réussi !" if passed else "Niveau échoué", card.center, 52, color, True, "center")

    def _draw_modal(self, screen):
        modal = self.modal
        context = modal["context"]
        fnt = theme.font(22)
        message_lines = wrap(modal["message"], theme.font(28, True), 580)
        options = modal.get("options", [])
        height = 70 + len(context) * 24 + len(message_lines) * 30
        height += 60 if modal["kind"] in ("request", "ask") else len(options) * 50 + 4
        card = self._card(screen, 660, height)
        y = card.top + 24
        for line in context:
            color = theme.LOG_COLORS.get("success" if line.startswith(("Success", "Total", "Level", "Time", "Clear", "CONGRAT"))
                                         else "failure" if line.startswith("Sorry") else "info")
            screen.blit(fnt.render(line[:80], True, color), (card.left + 30, y))
            y += 24
        if context:
            y += 8
        for line in message_lines:
            draw_text(screen, line, (card.left + 30, y), 28, theme.TEXT, True)
            y += 30
        y += 12
        mouse = pygame.mouse.get_pos()
        if modal["kind"] == "request":
            field = pygame.Rect(card.left + 30, y, 460, 44)
            pygame.draw.rect(screen, theme.BACKGROUND, field, border_radius=8)
            pygame.draw.rect(screen, theme.ACCENT, field, 2, border_radius=8)
            caret = "|" if (pygame.time.get_ticks() // 500) % 2 else ""
            draw_text(screen, modal["text"] + caret, (field.left + 12, field.centery), 28, theme.TEXT, anchor="midleft")
            ok = pygame.Rect(field.right + 12, y, 128, 44)
            modal["ok_rect"] = ok
            pygame.draw.rect(screen, theme.BUTTON_ACTIVE, ok, border_radius=8)
            draw_text(screen, "Valider", ok.center, 24, (30, 26, 20), True, "center")
            return
        rects = []
        horizontal = modal["kind"] == "ask"
        for i, (_, label, key) in enumerate(options):
            if horizontal:
                rect = pygame.Rect(card.left + 30 + i * 200, y, 184, 46)
            else:
                rect = pygame.Rect(card.left + 30, y + i * 50, card.w - 60, 42)
            rects.append(rect)
            selected = i == modal["selected"] or rect.collidepoint(mouse)
            pygame.draw.rect(screen, theme.BUTTON_ACTIVE if selected else theme.BUTTON, rect, border_radius=8)
            color = (30, 26, 20) if selected else theme.TEXT
            draw_text(screen, f"[{key}]  {label}", (rect.left + 16, rect.centery), 24, color, selected, "midleft")
        modal["rects"] = rects

    # --- session end -------------------------------------------------------------

    def end_screen(self, message):
        self.log.add(message)
        return self._run_modal({
            "kind": "choose",
            "message": "Session terminée. Modifiez player.py puis relancez.",
            "options": [(True, "Rejouer (recharge player.py)", "1"), (False, "Quitter", "2")],
        })

    def close(self):
        bus.unsubscribe(self._on_event)
        theme.clear_fonts()
        pygame.quit()


def run_gui(game_factory, backend=None):
    """Run games in the window until the player quits."""
    backend = backend or GuiBackend()
    UI.use(backend)
    Config.delay = None  # pacing is handled by the animations
    try:
        while True:
            try:
                game_factory().start()
                message = "Fin de la partie."
            except QuitRequested:
                break
            except SystemExit:
                message = "Fin de la partie."
            except Exception:
                backend.in_turn = False
                backend.log.add("Error in your code:")
                for line in traceback.format_exc().strip().split("\n")[-6:]:
                    backend.log.add(line)
                message = "Sorry, an error stopped the game."
            try:
                if not backend.end_screen(message):
                    break
            except QuitRequested:
                break
            backend.level = None
            backend.board.floor = None
    finally:
        backend.close()

