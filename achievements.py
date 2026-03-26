"""
Achievements Module - Achievement tracking and notification system.
Provides predefined achievements, unlock logic, animated popups, and a full list screen.
"""

import pygame
import math
import time
import profiles
from ui_style import Colors, Fonts, draw_rounded_rect, draw_shadow


# ============================================================================
# ACHIEVEMENT DEFINITIONS
# ============================================================================

ACHIEVEMENT_DEFS = [
    {
        "id": "first_hole_in_one",
        "title": "Ace!",
        "desc": "Get a Hole in One",
        "icon": "star",
    },
    {
        "id": "collector_10",
        "title": "Coin Collector",
        "desc": "Collect 10 coins total",
        "icon": "coin",
    },
    {
        "id": "collector_50",
        "title": "Gold Rush",
        "desc": "Collect 50 coins total",
        "icon": "coin",
    },
    {
        "id": "course_complete",
        "title": "Finisher",
        "desc": "Complete a full course",
        "icon": "flag",
    },
    {
        "id": "under_par",
        "title": "Pro Golfer",
        "desc": "Finish a course under par",
        "icon": "star",
    },
    {
        "id": "first_purchase",
        "title": "Shopper",
        "desc": "Buy your first ball",
        "icon": "bag",
    },
    {
        "id": "all_balls",
        "title": "Full Collection",
        "desc": "Unlock all 16 balls",
        "icon": "ball",
    },
    {
        "id": "no_water",
        "title": "Dry Run",
        "desc": "Complete a course without hitting water",
        "icon": "drop",
    },
    {
        "id": "seed_master",
        "title": "Explorer",
        "desc": "Complete a seed mode course",
        "icon": "map",
    },
    {
        "id": "daily_player",
        "title": "Daily Challenger",
        "desc": "Complete a daily challenge",
        "icon": "calendar",
    },
    {
        "id": "power_user",
        "title": "Power Player",
        "desc": "Use all 3 power-up types in one course",
        "icon": "bolt",
    },
    {
        "id": "perfect_hole",
        "title": "Perfectionist",
        "desc": "Get par or better on every hole in a course",
        "icon": "star",
    },
]

# Map icon name → color for the icon badge
_ICON_COLORS = {
    "star":     Colors.ACCENT_GOLD,
    "coin":     Colors.ACCENT_GOLD,
    "flag":     Colors.ACCENT_GREEN,
    "bag":      Colors.ACCENT_PURPLE,
    "ball":     Colors.ACCENT_BLUE,
    "drop":     Colors.ACCENT_BLUE,
    "map":      Colors.ACCENT_ORANGE,
    "calendar": Colors.ACCENT_ORANGE,
    "bolt":     Colors.ACCENT_PURPLE,
}


# ============================================================================
# POPUP ANIMATION STATE
# ============================================================================

class _PopupState:
    SLIDE_DURATION = 0.35   # seconds to slide in/out
    HOLD_DURATION = 3.0     # seconds to stay on screen

    def __init__(self, achievement_def):
        self.defn = achievement_def
        self.start_time = time.time()
        self.done = False

    def phase(self):
        """Returns ('in', t), ('hold', t), ('out', t), or 'done' where t in [0,1]."""
        elapsed = time.time() - self.start_time
        if elapsed < self.SLIDE_DURATION:
            return ("in", elapsed / self.SLIDE_DURATION)
        elapsed2 = elapsed - self.SLIDE_DURATION
        if elapsed2 < self.HOLD_DURATION:
            return ("hold", elapsed2 / self.HOLD_DURATION)
        elapsed3 = elapsed2 - self.HOLD_DURATION
        if elapsed3 < self.SLIDE_DURATION:
            return ("out", elapsed3 / self.SLIDE_DURATION)
        self.done = True
        return ("done", 1.0)


# ============================================================================
# ACHIEVEMENT MANAGER
# ============================================================================

class AchievementManager:
    """
    Central achievement tracker.

    Usage:
        manager = AchievementManager()
        manager.check_and_unlock("first_hole_in_one")

        # Every frame:
        manager.draw_popup(surface)

        # To show the full achievement screen:
        manager.draw_list(surface)
    """

    POPUP_W = 380
    POPUP_H = 74
    POPUP_MARGIN = 16      # From top of window
    POPUP_RIGHT_MARGIN = 20

    LIST_ITEM_H = 64
    LIST_ITEM_SPACING = 8
    LIST_COLS = 2
    LIST_PADDING = 30

    def __init__(self, win_width=1080, win_height=600):
        self.win_width = win_width
        self.win_height = win_height
        self._popup_queue = []   # list of _PopupState, FIFO
        # Build lookup by id
        self._defs_by_id = {d["id"]: d for d in ACHIEVEMENT_DEFS}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def check_and_unlock(self, achievement_id):
        """
        Unlock the achievement if not already unlocked.
        Triggers an animated popup notification.
        Returns True if newly unlocked.
        """
        if achievement_id not in self._defs_by_id:
            return False
        newly_unlocked = profiles.unlock_achievement(achievement_id)
        if newly_unlocked:
            self._popup_queue.append(_PopupState(self._defs_by_id[achievement_id]))
        return newly_unlocked

    def draw_popup(self, surface):
        """
        Draw the current animated achievement popup (slides in from top-right).
        Call every frame.
        """
        if not self._popup_queue:
            return

        popup = self._popup_queue[0]
        phase_info = popup.phase()

        if phase_info[0] == "done":
            self._popup_queue.pop(0)
            return

        phase, t = phase_info
        t_ease = self._ease_out(t)

        # Slide from right: off-screen right → on screen
        target_x = self.win_width - self.POPUP_W - self.POPUP_RIGHT_MARGIN
        offscreen_x = self.win_width + 10

        if phase == "in":
            x = int(offscreen_x + (target_x - offscreen_x) * t_ease)
        elif phase == "hold":
            x = target_x
        else:  # out — slide back right
            x = int(target_x + (offscreen_x - target_x) * t_ease)

        y = self.POPUP_MARGIN

        self._draw_popup_at(surface, popup.defn, x, y)

    def draw_list(self, surface):
        """
        Draw the full achievement list screen over the surface.
        Locked achievements are grayed out.
        """
        unlocked = profiles.get_achievements()

        # Background
        bg = pygame.Surface((self.win_width, self.win_height), pygame.SRCALPHA)
        bg.fill((10, 14, 26, 230))
        surface.blit(bg, (0, 0))

        # Title
        title_surf = Fonts.TITLE_MEDIUM.render("Achievements", True, Colors.TEXT_LIGHT)
        title_rect = title_surf.get_rect(centerx=self.win_width // 2, top=24)
        surface.blit(title_surf, title_rect)

        # Subtitle: X / total unlocked
        count = sum(1 for d in ACHIEVEMENT_DEFS if d["id"] in unlocked)
        total = len(ACHIEVEMENT_DEFS)
        sub_text = f"{count} / {total} unlocked"
        sub_surf = Fonts.UI_MEDIUM.render(sub_text, True, Colors.ACCENT_GOLD)
        sub_rect = sub_surf.get_rect(centerx=self.win_width // 2, top=title_rect.bottom + 6)
        surface.blit(sub_surf, sub_rect)

        # Grid of achievement cards
        cols = self.LIST_COLS
        pad = self.LIST_PADDING
        available_w = self.win_width - pad * 2
        item_w = (available_w - (cols - 1) * self.LIST_ITEM_SPACING) // cols
        item_h = self.LIST_ITEM_H
        start_y = sub_rect.bottom + 20

        for i, defn in enumerate(ACHIEVEMENT_DEFS):
            col = i % cols
            row = i // cols
            ix = pad + col * (item_w + self.LIST_ITEM_SPACING)
            iy = start_y + row * (item_h + self.LIST_ITEM_SPACING)
            is_unlocked = defn["id"] in unlocked
            self._draw_achievement_card(surface, defn, ix, iy, item_w, item_h, is_unlocked)

    # ------------------------------------------------------------------
    # Internal drawing helpers
    # ------------------------------------------------------------------

    def _draw_popup_at(self, surface, defn, x, y):
        pw, ph = self.POPUP_W, self.POPUP_H

        # Shadow
        draw_shadow(surface, (x, y, pw, ph), radius=12, offset=(3, 5), blur=3)

        # Background
        draw_rounded_rect(surface, (18, 22, 38, 235), (x, y, pw, ph), 12)
        draw_rounded_rect(surface, Colors.ACCENT_GOLD + (180,), (x, y, pw, ph), 12, width=2)

        # Icon badge
        badge_size = 44
        badge_x = x + 14
        badge_y = y + (ph - badge_size) // 2
        icon_color = _ICON_COLORS.get(defn.get("icon", "star"), Colors.ACCENT_GOLD)
        draw_rounded_rect(surface, icon_color + (60,), (badge_x, badge_y, badge_size, badge_size), 10)
        self._draw_icon(surface, defn.get("icon", "star"), badge_x + badge_size // 2, badge_y + badge_size // 2, icon_color)

        # "Achievement Unlocked!" label
        label_surf = Fonts.HUD_SMALL.render("Achievement Unlocked!", True, Colors.ACCENT_GOLD)
        surface.blit(label_surf, (badge_x + badge_size + 12, y + 12))

        # Title
        title_surf = Fonts.HUD_MEDIUM.render(defn["title"], True, Colors.TEXT_LIGHT)
        surface.blit(title_surf, (badge_x + badge_size + 12, y + 30))

        # Description
        desc_surf = Fonts.UI_TINY.render(defn["desc"], True, Colors.TEXT_SECONDARY)
        surface.blit(desc_surf, (badge_x + badge_size + 12, y + 50))

    def _draw_achievement_card(self, surface, defn, x, y, w, h, is_unlocked):
        if is_unlocked:
            bg_color = (28, 38, 60, 210)
            border_color = Colors.ACCENT_GOLD + (160,)
            text_color = Colors.TEXT_LIGHT
            desc_color = Colors.TEXT_SECONDARY
        else:
            bg_color = (20, 24, 34, 180)
            border_color = (60, 65, 80, 100)
            text_color = (90, 100, 120)
            desc_color = (60, 70, 85)

        draw_shadow(surface, (x, y, w, h), radius=10, offset=(2, 3), blur=2)
        draw_rounded_rect(surface, bg_color, (x, y, w, h), 10)
        draw_rounded_rect(surface, border_color, (x, y, w, h), 10, width=2)

        # Icon badge
        badge_size = 38
        badge_x = x + 12
        badge_y = y + (h - badge_size) // 2
        icon_color = _ICON_COLORS.get(defn.get("icon", "star"), Colors.ACCENT_GOLD)
        if is_unlocked:
            draw_rounded_rect(surface, icon_color + (70,), (badge_x, badge_y, badge_size, badge_size), 8)
            self._draw_icon(surface, defn.get("icon", "star"), badge_x + badge_size // 2, badge_y + badge_size // 2, icon_color)
        else:
            draw_rounded_rect(surface, (40, 45, 55, 80), (badge_x, badge_y, badge_size, badge_size), 8)
            self._draw_icon(surface, "lock", badge_x + badge_size // 2, badge_y + badge_size // 2, (70, 80, 100))

        # Title
        title_surf = Fonts.HUD_MEDIUM.render(defn["title"], True, text_color)
        text_x = badge_x + badge_size + 12
        title_y = y + 12
        surface.blit(title_surf, (text_x, title_y))

        # Description
        desc_surf = Fonts.UI_TINY.render(defn["desc"], True, desc_color)
        surface.blit(desc_surf, (text_x, title_y + title_surf.get_height() + 4))

        # Unlocked checkmark
        if is_unlocked:
            check_surf = Fonts.HUD_SMALL.render("Unlocked", True, Colors.ACCENT_GREEN)
            check_x = x + w - check_surf.get_width() - 12
            check_y = y + h - check_surf.get_height() - 8
            surface.blit(check_surf, (check_x, check_y))

    def _draw_icon(self, surface, icon_name, cx, cy, color):
        """Draw a simple vector icon at center (cx, cy) in the given color."""
        if icon_name == "star":
            self._draw_star(surface, cx, cy, 10, color)
        elif icon_name == "coin":
            pygame.draw.circle(surface, color, (cx, cy), 9)
            pygame.draw.circle(surface, (0, 0, 0, 60) if len(color) == 4 else (0, 0, 0), (cx, cy), 9, 2)
            # Dollar sign approximation — just a smaller inner circle
            pygame.draw.circle(surface, (255, 255, 255, 80) if len(color) == 3 else (255, 255, 255), (cx, cy), 5)
        elif icon_name == "flag":
            # Pole
            pygame.draw.line(surface, color, (cx - 4, cy + 10), (cx - 4, cy - 10), 2)
            # Flag triangle
            points = [(cx - 4, cy - 10), (cx + 8, cy - 5), (cx - 4, cy)]
            pygame.draw.polygon(surface, color, points)
        elif icon_name == "bolt":
            points = [(cx + 3, cy - 11), (cx - 4, cy - 1), (cx + 2, cy - 1), (cx - 3, cy + 11), (cx + 6, cy + 1), (cx - 1, cy + 1)]
            pygame.draw.polygon(surface, color, points)
        elif icon_name == "lock":
            # Simple padlock
            pygame.draw.rect(surface, color, (cx - 6, cy - 2, 12, 9), border_radius=2)
            pygame.draw.arc(surface, color, (cx - 5, cy - 10, 10, 12), 0, math.pi, 2)
        else:
            # Generic circle fallback
            pygame.draw.circle(surface, color, (cx, cy), 8)

    def _draw_star(self, surface, cx, cy, r, color):
        outer_r = r
        inner_r = r * 0.45
        points = []
        for i in range(10):
            angle = math.pi / 2 + i * math.pi / 5
            radius = outer_r if i % 2 == 0 else inner_r
            points.append((cx + math.cos(angle) * radius, cy - math.sin(angle) * radius))
        pygame.draw.polygon(surface, color, points)

    @staticmethod
    def _ease_out(t):
        """Cubic ease-out."""
        return 1 - (1 - t) ** 3
