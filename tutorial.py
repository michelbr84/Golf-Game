"""
Tutorial Module - Interactive tutorial overlay for Super Minigolf Premium.
Guides new players through basic game mechanics step by step.
"""

import pygame
import math
from ui_style import Colors, Fonts, draw_rounded_rect, draw_shadow


class TutorialStep:
    """Represents a single tutorial step."""
    def __init__(self, message, key_hint, highlight_rect=None, advance_on=None):
        # advance_on: 'mouse_move', 'click', 'any', or None (manual only)
        self.message = message
        self.key_hint = key_hint
        self.highlight_rect = highlight_rect  # (x, y, w, h) or None
        self.advance_on = advance_on


STEPS = [
    TutorialStep(
        message="Move your mouse to aim the shot",
        key_hint="Move Mouse",
        advance_on="mouse_move",
    ),
    TutorialStep(
        message="Click to start the power meter",
        key_hint="Left Click",
        advance_on="click",
    ),
    TutorialStep(
        message="Click again to shoot!",
        key_hint="Left Click",
        advance_on="click",
    ),
    TutorialStep(
        message="Press P for Power Ball, S for Sticky, M for Mulligan",
        key_hint="P / S / M",
        advance_on="any",
    ),
    TutorialStep(
        message="Collect coins to buy new balls!",
        key_hint="Play & Collect",
        advance_on="any",
    ),
    TutorialStep(
        message="Avoid water, sand, and lasers!",
        key_hint="Good luck!",
        advance_on="any",
    ),
]


class Tutorial:
    """
    Interactive tutorial overlay system.

    Usage:
        tutorial = Tutorial()
        # In game loop:
        tutorial.update(events)
        tutorial.draw(surface)
        if tutorial.is_complete():
            # proceed normally
    """

    OVERLAY_ALPHA = 160          # Darkness of the dim overlay
    PANEL_W = 560
    PANEL_H = 130
    PANEL_MARGIN_BOTTOM = 30     # Distance from bottom of window
    ARROW_ANIM_SPEED = 0.05      # Radians per frame for floating arrow bob

    def __init__(self, win_width=1080, win_height=600):
        self.win_width = win_width
        self.win_height = win_height
        self._step_index = 0
        self._active = True
        self._complete = False
        self._mouse_moved = False
        self._anim_tick = 0.0
        self._fade_alpha = 0       # For fade-in of panel
        self._fading_in = True

        # Pre-build overlay surface (reused every frame, alpha set at draw time)
        self._overlay = pygame.Surface((win_width, win_height), pygame.SRCALPHA)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_active(self):
        """Returns True while the tutorial is running."""
        return self._active

    def is_complete(self):
        """Returns True when all steps have been shown."""
        return self._complete

    def skip(self):
        """End the tutorial immediately."""
        self._active = False
        self._complete = True

    def update(self, events):
        """
        Process events and advance tutorial steps as appropriate.
        Call every frame.
        """
        if not self._active:
            return

        # Fade in animation
        if self._fading_in:
            self._fade_alpha = min(255, self._fade_alpha + 15)
            if self._fade_alpha >= 255:
                self._fading_in = False

        self._anim_tick += self.ARROW_ANIM_SPEED

        step = self._current_step()

        for event in events:
            # Global skip keys
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_ESCAPE):
                    self.skip()
                    return

            # Step-specific advancement
            if step.advance_on == "mouse_move":
                if event.type == pygame.MOUSEMOTION:
                    if not self._mouse_moved:
                        self._mouse_moved = True
                        self._advance()
                        return

            elif step.advance_on == "click":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._advance()
                    return

            elif step.advance_on == "any":
                if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                    self._advance()
                    return

    def draw(self, surface):
        """Draw the tutorial overlay onto surface."""
        if not self._active:
            return

        step = self._current_step()

        # Dim overlay
        self._overlay.fill((0, 0, 0, self.OVERLAY_ALPHA))

        # If there's a highlight rect, cut a "hole" (lighter area) through the overlay
        if step.highlight_rect:
            hx, hy, hw, hh = step.highlight_rect
            pygame.draw.rect(self._overlay, (0, 0, 0, 0), (hx, hy, hw, hh))

        surface.blit(self._overlay, (0, 0))

        # Floating arrow (only when highlight rect present)
        if step.highlight_rect:
            self._draw_arrow(surface, step.highlight_rect)

        # Main info panel at bottom-center
        self._draw_panel(surface, step)

        # Step indicator dots
        self._draw_step_dots(surface)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _current_step(self):
        idx = min(self._step_index, len(STEPS) - 1)
        return STEPS[idx]

    def _advance(self):
        self._step_index += 1
        self._fading_in = True
        self._fade_alpha = 0
        if self._step_index >= len(STEPS):
            self.skip()

    def _draw_panel(self, surface, step):
        pw, ph = self.PANEL_W, self.PANEL_H
        px = (self.win_width - pw) // 2
        py = self.win_height - ph - self.PANEL_MARGIN_BOTTOM

        # Shadow
        draw_shadow(surface, (px, py, pw, ph), radius=14, offset=(4, 6), blur=4)

        # Panel background (dark glass)
        draw_rounded_rect(surface, (20, 25, 40, 220), (px, py, pw, ph), 14)
        draw_rounded_rect(surface, (255, 255, 255, 50), (px, py, pw, ph), 14, width=2)

        # Step label (e.g. "Step 2 of 6")
        step_num = self._step_index + 1
        total = len(STEPS)
        label_text = f"Step {step_num} of {total}"
        label_surf = Fonts.UI_TINY.render(label_text, True, Colors.TEXT_SECONDARY)
        surface.blit(label_surf, (px + 20, py + 12))

        # Main message
        msg_surf = Fonts.UI_LARGE.render(step.message, True, Colors.TEXT_LIGHT)
        msg_rect = msg_surf.get_rect(centerx=px + pw // 2, top=py + 34)
        surface.blit(msg_surf, msg_rect)

        # Key hint pill
        if step.key_hint:
            self._draw_key_hint(surface, step.key_hint, px + pw // 2, py + ph - 28)

        # Skip hint (bottom-right of panel)
        skip_surf = Fonts.UI_TINY.render("SPACE / ESC to skip", True, (150, 160, 180))
        surface.blit(skip_surf, (px + pw - skip_surf.get_width() - 14, py + 12))

    def _draw_key_hint(self, surface, hint_text, cx, cy):
        """Draw a small pill-shaped key hint."""
        font = Fonts.HUD_SMALL
        text_surf = font.render(hint_text, True, Colors.ACCENT_GOLD)
        tw, th = text_surf.get_size()
        pill_w = tw + 24
        pill_h = th + 10
        pill_x = cx - pill_w // 2
        pill_y = cy - pill_h // 2
        draw_rounded_rect(surface, (245, 158, 11, 50), (pill_x, pill_y, pill_w, pill_h), 8)
        draw_rounded_rect(surface, (245, 158, 11, 120), (pill_x, pill_y, pill_w, pill_h), 8, width=2)
        surface.blit(text_surf, (pill_x + 12, pill_y + 5))

    def _draw_step_dots(self, surface):
        """Draw progress dots below the panel."""
        total = len(STEPS)
        dot_r = 5
        spacing = 18
        total_w = total * (dot_r * 2) + (total - 1) * (spacing - dot_r * 2)
        start_x = (self.win_width - total_w) // 2
        dot_y = self.win_height - self.PANEL_MARGIN_BOTTOM // 2 + 8

        for i in range(total):
            cx = start_x + i * spacing + dot_r
            if i < self._step_index:
                color = Colors.ACCENT_GREEN
                r = dot_r
            elif i == self._step_index:
                color = Colors.ACCENT_GOLD
                r = dot_r + 2
            else:
                color = (80, 90, 110)
                r = dot_r
            pygame.draw.circle(surface, color, (cx, dot_y), r)

    def _draw_arrow(self, surface, highlight_rect):
        """Draw an animated pointing arrow above the highlight rect."""
        hx, hy, hw, hh = highlight_rect
        cx = hx + hw // 2
        # Bob up/down
        bob = int(math.sin(self._anim_tick) * 6)
        tip_y = hy - 18 + bob
        shaft_y = tip_y - 20

        # Arrow triangle pointing down toward highlight
        arrow_points = [
            (cx, tip_y),
            (cx - 12, shaft_y),
            (cx + 12, shaft_y),
        ]
        pygame.draw.polygon(surface, Colors.ACCENT_GOLD, arrow_points)
        pygame.draw.polygon(surface, Colors.TEXT_LIGHT, arrow_points, 2)
