"""
Wind System - Affects ball trajectory with horizontal wind force.
Includes HUD indicator and visual wind particles.
"""

import pygame
import random
import math
from ui_style import Colors, Fonts, draw_rounded_rect, draw_shadow


class WindParticle:
    """A single drifting dot used for wind visual feedback."""

    def __init__(self, screen_w, screen_h, wind_speed):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self._reset(initial=True, wind_speed=wind_speed)

    def _reset(self, initial=False, wind_speed=0):
        self.y = random.randint(0, self.screen_h)
        if initial:
            self.x = random.randint(0, self.screen_w)
        else:
            # Spawn at the leading edge based on direction
            self.x = 0 if wind_speed > 0 else self.screen_w
        self.speed = abs(wind_speed) * random.uniform(0.6, 1.4)
        self.direction = 1 if wind_speed >= 0 else -1
        self.alpha = random.randint(40, 110)
        self.size = random.randint(1, 3)
        self.life = random.randint(60, 180)
        self.age = 0

    def update(self, wind_speed):
        self.x += wind_speed * 0.8 * self.direction
        self.age += 1
        if self.age >= self.life or self.x < -10 or self.x > self.screen_w + 10:
            self._reset(wind_speed=wind_speed)

    def draw(self, surface):
        if self.speed < 0.1:
            return
        fade = 1.0 - self.age / max(self.life, 1)
        alpha = int(self.alpha * fade)
        if alpha <= 0:
            return
        dot_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(dot_surf, (255, 255, 255, alpha), (self.size, self.size), self.size)
        surface.blit(dot_surf, (int(self.x) - self.size, int(self.y) - self.size))


class WindSystem:
    """
    Manages wind speed/direction, applies force to the ball, and draws the HUD.
    """

    PARTICLE_COUNT = 40

    def __init__(self):
        self.wind_speed = 0.0        # positive = right, negative = left
        self.wind_direction = 1      # 1 = right, -1 = left
        self._particles = []
        self._screen_w = 1080
        self._screen_h = 600

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def randomize(self):
        """Set a new random wind speed between -3.0 and 3.0."""
        self.wind_speed = random.uniform(-3.0, 3.0)
        self.wind_direction = 1 if self.wind_speed >= 0 else -1
        self._init_particles()

    def apply_wind(self, x, y, dt):
        """
        Return new (x, y) after applying wind displacement.

        Args:
            x, y: Current ball position
            dt:   Delta time in seconds

        Returns:
            (new_x, new_y) tuple
        """
        new_x = x + self.wind_speed * dt * 15
        return new_x, y

    def draw_indicator(self, surface, x=540, y=12):
        """
        Draw a glass-card wind indicator HUD element centred at (x, y).

        Args:
            surface: Pygame surface to draw on
            x: Horizontal centre of the card
            y: Top y of the card
        """
        Fonts.init()

        CARD_W = 160
        CARD_H = 36
        cx = x - CARD_W // 2
        cy = y

        # Shadow + card
        draw_shadow(surface, (cx, cy, CARD_W, CARD_H), radius=10, offset=(2, 3), blur=2)
        card_surf = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
        card_surf.fill((30, 40, 60, 180))
        surface.blit(card_surf, (cx, cy))
        draw_rounded_rect(surface, (255, 255, 255, 50), (cx, cy, CARD_W, CARD_H), 10, width=1)

        speed = abs(self.wind_speed)

        if speed < 0.1:
            # Calm — just show label
            label = Fonts.HUD_SMALL.render("~ Calm ~", True, Colors.TEXT_LIGHT)
            surface.blit(label, (cx + CARD_W // 2 - label.get_width() // 2,
                                 cy + CARD_H // 2 - label.get_height() // 2))
            return

        # Arrow proportional to speed (max 3.0 → arrow_len 28)
        arrow_len = int(8 + speed / 3.0 * 20)
        arrow_color = self._speed_color(speed)
        mid_y = cy + CARD_H // 2

        # Draw arrow body and head
        arrow_cx = cx + 22
        if self.wind_direction > 0:
            # Right-pointing arrow
            pygame.draw.line(surface, arrow_color,
                             (arrow_cx - arrow_len // 2, mid_y),
                             (arrow_cx + arrow_len // 2, mid_y), 2)
            pygame.draw.polygon(surface, arrow_color, [
                (arrow_cx + arrow_len // 2,     mid_y),
                (arrow_cx + arrow_len // 2 - 6, mid_y - 5),
                (arrow_cx + arrow_len // 2 - 6, mid_y + 5),
            ])
        else:
            # Left-pointing arrow
            pygame.draw.line(surface, arrow_color,
                             (arrow_cx - arrow_len // 2, mid_y),
                             (arrow_cx + arrow_len // 2, mid_y), 2)
            pygame.draw.polygon(surface, arrow_color, [
                (arrow_cx - arrow_len // 2,     mid_y),
                (arrow_cx - arrow_len // 2 + 6, mid_y - 5),
                (arrow_cx - arrow_len // 2 + 6, mid_y + 5),
            ])

        # Speed text
        spd_text = Fonts.HUD_SMALL.render(f"{speed:.1f}", True, arrow_color)
        surface.blit(spd_text, (cx + CARD_W - spd_text.get_width() - 8,
                                cy + CARD_H // 2 - spd_text.get_height() // 2))

    def get_description(self):
        """Return a human-readable wind description."""
        s = abs(self.wind_speed)
        if s < 0.5:
            return "Calm"
        elif s < 1.5:
            return "Light Breeze"
        elif s < 2.5:
            return "Moderate Wind"
        else:
            return "Strong Wind"

    def update(self):
        """Apply subtle wind speed drift and update particles."""
        # Small random drift ±0.1, clamped to [-3, 3]
        drift = random.uniform(-0.1, 0.1)
        self.wind_speed = max(-3.0, min(3.0, self.wind_speed + drift))
        self.wind_direction = 1 if self.wind_speed >= 0 else -1

        # Update particles
        for p in self._particles:
            p.update(self.wind_speed)

    def draw_particles(self, surface):
        """Draw wind particles on the given surface for visual feedback."""
        for p in self._particles:
            p.draw(surface)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _init_particles(self):
        self._particles = [
            WindParticle(self._screen_w, self._screen_h, self.wind_speed)
            for _ in range(self.PARTICLE_COUNT)
        ]

    @staticmethod
    def _speed_color(speed):
        """Return a colour that transitions green → orange → red by speed."""
        t = min(speed / 3.0, 1.0)
        if t < 0.5:
            # green → orange
            f = t * 2
            r = int(Colors.ACCENT_GREEN[0] + (Colors.ACCENT_ORANGE[0] - Colors.ACCENT_GREEN[0]) * f)
            g = int(Colors.ACCENT_GREEN[1] + (Colors.ACCENT_ORANGE[1] - Colors.ACCENT_GREEN[1]) * f)
            b = int(Colors.ACCENT_GREEN[2] + (Colors.ACCENT_ORANGE[2] - Colors.ACCENT_GREEN[2]) * f)
        else:
            # orange → red
            f = (t - 0.5) * 2
            r = int(Colors.ACCENT_ORANGE[0] + (Colors.ACCENT_RED[0] - Colors.ACCENT_ORANGE[0]) * f)
            g = int(Colors.ACCENT_ORANGE[1] + (Colors.ACCENT_RED[1] - Colors.ACCENT_ORANGE[1]) * f)
            b = int(Colors.ACCENT_ORANGE[2] + (Colors.ACCENT_RED[2] - Colors.ACCENT_ORANGE[2]) * f)
        return (r, g, b)
