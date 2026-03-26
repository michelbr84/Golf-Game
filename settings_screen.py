"""
Settings Screen - Full settings UI with toggles and sliders.
Replaces the basic audio menu with a premium glass-card style interface.
"""

import pygame
from ui_style import Colors, Fonts, draw_rounded_rect, draw_shadow, create_gradient_surface


def show_settings(win, config):
    """
    Display the settings screen. Runs its own event loop.
    Returns when ESC is pressed.

    Args:
        win: Pygame display surface (1080x600)
        config: Config object with get(section, key) and set(section, key, value) methods
    """
    Fonts.init()
    clock = pygame.time.Clock()

    WIN_W, WIN_H = win.get_size()

    # Card dimensions
    CARD_W = 700
    CARD_H = 520
    CARD_X = (WIN_W - CARD_W) // 2
    CARD_Y = (WIN_H - CARD_H) // 2

    # -------------------------------------------------------------------------
    # Helper: load config values (with safe defaults)
    # -------------------------------------------------------------------------
    def _get_bool(section, key, default=True):
        try:
            v = config.get(section, key)
            if isinstance(v, bool):
                return v
            return str(v).lower() in ("1", "true", "yes", "on")
        except Exception:
            return default

    def _get_int(section, key, default=80):
        try:
            return int(config.get(section, key))
        except Exception:
            return default

    # -------------------------------------------------------------------------
    # State
    # -------------------------------------------------------------------------
    state = {
        "music_on":       _get_bool("audio", "music", True),
        "sfx_on":         _get_bool("audio", "sfx", True),
        "music_vol":      _get_int("audio",  "music_volume", 80),
        "sfx_vol":        _get_int("audio",  "sfx_volume",   80),
        "fullscreen":     _get_bool("display",  "fullscreen",  False),
        "show_fps":       _get_bool("display",  "show_fps",    False),
        "show_tutorial":  _get_bool("gameplay", "show_tutorial", True),
        "particles":      _get_bool("gameplay", "particles",    True),
    }

    # -------------------------------------------------------------------------
    # Layout helpers
    # -------------------------------------------------------------------------
    SECTION_COLOR = (45, 55, 72)
    LABEL_COLOR   = Colors.TEXT_PRIMARY
    HINT_COLOR    = Colors.TEXT_SECONDARY

    ROW_H      = 44
    TOGGLE_W   = 64
    TOGGLE_H   = 28
    SLIDER_W   = 180
    SLIDER_H   = 8
    PADDING    = 32

    # Track which slider is being dragged: None or key name
    dragging_slider = None

    # -------------------------------------------------------------------------
    # Background gradient (cached once)
    # -------------------------------------------------------------------------
    bg = create_gradient_surface(WIN_W, WIN_H, Colors.SKY_TOP, Colors.SKY_BOTTOM)

    # -------------------------------------------------------------------------
    # Draw helpers
    # -------------------------------------------------------------------------
    def draw_toggle(surface, cx, cy, value):
        """Draw a pill-shaped toggle button. Returns its rect."""
        rx = cx - TOGGLE_W // 2
        ry = cy - TOGGLE_H // 2
        color = Colors.ACCENT_GREEN if value else (150, 150, 160)
        draw_rounded_rect(surface, color, (rx, ry, TOGGLE_W, TOGGLE_H), TOGGLE_H // 2)
        # Knob
        knob_x = rx + TOGGLE_W - TOGGLE_H // 2 - 2 if value else rx + TOGGLE_H // 2 + 2
        knob_y = cy
        pygame.draw.circle(surface, (255, 255, 255), (knob_x, knob_y), TOGGLE_H // 2 - 3)
        return pygame.Rect(rx, ry, TOGGLE_W, TOGGLE_H)

    def draw_slider(surface, lx, cy, value, key):
        """Draw a horizontal slider (value 0-100). Returns its track rect."""
        track_rect = pygame.Rect(lx, cy - SLIDER_H // 2, SLIDER_W, SLIDER_H)
        # Track background
        draw_rounded_rect(surface, (180, 190, 210), (lx, cy - SLIDER_H // 2, SLIDER_W, SLIDER_H), SLIDER_H // 2)
        # Filled portion
        fill_w = int(SLIDER_W * value / 100)
        if fill_w > 0:
            draw_rounded_rect(surface, Colors.ACCENT_BLUE, (lx, cy - SLIDER_H // 2, fill_w, SLIDER_H), SLIDER_H // 2)
        # Knob
        knob_x = lx + fill_w
        knob_x = max(lx + 6, min(lx + SLIDER_W - 6, knob_x))
        pygame.draw.circle(surface, Colors.ACCENT_BLUE, (knob_x, cy), 9)
        pygame.draw.circle(surface, (255, 255, 255), (knob_x, cy), 5)
        return track_rect

    def draw_label(surface, text, x, y, font=None, color=None):
        if font is None:
            font = Fonts.UI_MEDIUM
        if color is None:
            color = LABEL_COLOR
        surf = font.render(text, True, color)
        surface.blit(surf, (x, y - surf.get_height() // 2))

    # -------------------------------------------------------------------------
    # Build section layout
    # Sections list: (section_title, rows)
    # Row: ("toggle", label, state_key, config_section, config_key)
    #      ("slider",  label, state_key, config_section, config_key)
    # -------------------------------------------------------------------------
    sections = [
        ("AUDIO", [
            ("toggle", "Music",        "music_on",  "audio", "music"),
            ("toggle", "Sound Effects","sfx_on",    "audio", "sfx"),
            ("slider", "Music Volume", "music_vol", "audio", "music_volume"),
            ("slider", "SFX Volume",   "sfx_vol",   "audio", "sfx_volume"),
        ]),
        ("DISPLAY", [
            ("toggle", "Fullscreen",   "fullscreen", "display", "fullscreen"),
            ("toggle", "Show FPS",     "show_fps",   "display", "show_fps"),
        ]),
        ("GAMEPLAY", [
            ("toggle", "Show Tutorial","show_tutorial","gameplay","show_tutorial"),
            ("toggle", "Particles",    "particles",    "gameplay","particles"),
        ]),
    ]

    # Pre-compute row y positions relative to card interior
    CONTENT_TOP = CARD_Y + 72   # below title
    row_data = []   # (row_dict, abs_y)
    y_cursor = CONTENT_TOP + 10

    for sec_title, rows in sections:
        # Section header
        row_data.append({"type": "section", "title": sec_title, "y": y_cursor})
        y_cursor += 30
        for row in rows:
            row_data.append({
                "type":       row[0],
                "label":      row[1],
                "key":        row[2],
                "cfg_section":row[3],
                "cfg_key":    row[4],
                "y":          y_cursor + ROW_H // 2,
            })
            y_cursor += ROW_H
        y_cursor += 8  # gap between sections

    # -------------------------------------------------------------------------
    # Main loop
    # -------------------------------------------------------------------------
    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        # --- Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for row in row_data:
                    if row["type"] == "section":
                        continue
                    row_y = row["y"]
                    if row["type"] == "toggle":
                        tx = CARD_X + CARD_W - PADDING - TOGGLE_W // 2
                        if abs(mx - tx) <= TOGGLE_W // 2 and abs(my - row_y) <= TOGGLE_H // 2:
                            state[row["key"]] = not state[row["key"]]
                            try:
                                config.set(row["cfg_section"], row["cfg_key"], state[row["key"]])
                            except Exception:
                                pass
                    elif row["type"] == "slider":
                        lx = CARD_X + CARD_W - PADDING - SLIDER_W
                        if lx <= mx <= lx + SLIDER_W and abs(my - row_y) <= 14:
                            dragging_slider = row["key"]
                            val = int((mx - lx) / SLIDER_W * 100)
                            val = max(0, min(100, val))
                            state[dragging_slider] = val
                            try:
                                config.set(row["cfg_section"], row["cfg_key"], val)
                            except Exception:
                                pass

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging_slider = None

            elif event.type == pygame.MOUSEMOTION:
                if dragging_slider:
                    mx, my = event.pos
                    # Find the row to get lx
                    for row in row_data:
                        if row.get("key") == dragging_slider:
                            lx = CARD_X + CARD_W - PADDING - SLIDER_W
                            val = int((mx - lx) / SLIDER_W * 100)
                            val = max(0, min(100, val))
                            state[dragging_slider] = val
                            try:
                                config.set(row["cfg_section"], row["cfg_key"], val)
                            except Exception:
                                pass
                            break

        # --- Draw ---
        win.blit(bg, (0, 0))

        # Card shadow
        draw_shadow(win, (CARD_X, CARD_Y, CARD_W, CARD_H), radius=20, offset=(6, 8), blur=4)

        # Card background (glass effect)
        card_surf = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
        card_surf.fill((255, 255, 255, 220))
        win.blit(card_surf, (CARD_X, CARD_Y))
        draw_rounded_rect(win, Colors.GLASS_BORDER, (CARD_X, CARD_Y, CARD_W, CARD_H), 20, width=2)

        # Title
        title_surf = Fonts.TITLE_SMALL.render("SETTINGS", True, Colors.TEXT_PRIMARY)
        win.blit(title_surf, (CARD_X + CARD_W // 2 - title_surf.get_width() // 2, CARD_Y + 20))

        # Divider
        pygame.draw.line(win, (200, 210, 220),
                         (CARD_X + PADDING, CARD_Y + 65),
                         (CARD_X + CARD_W - PADDING, CARD_Y + 65), 1)

        # Rows
        for row in row_data:
            ry = row["y"]

            if row["type"] == "section":
                sec_surf = Fonts.HUD_SMALL.render(row["title"], True, Colors.ACCENT_BLUE)
                win.blit(sec_surf, (CARD_X + PADDING, ry - 4))
                pygame.draw.line(win, (220, 228, 240),
                                 (CARD_X + PADDING, ry + 14),
                                 (CARD_X + CARD_W - PADDING, ry + 14), 1)
                continue

            # Label
            draw_label(win, row["label"], CARD_X + PADDING + 12, ry, Fonts.UI_MEDIUM, LABEL_COLOR)

            if row["type"] == "toggle":
                tx = CARD_X + CARD_W - PADDING - TOGGLE_W // 2
                draw_toggle(win, tx, ry, state[row["key"]])
                # Value text
                val_text = "ON" if state[row["key"]] else "OFF"
                val_color = Colors.ACCENT_GREEN if state[row["key"]] else HINT_COLOR
                val_surf = Fonts.UI_SMALL.render(val_text, True, val_color)
                win.blit(val_surf, (CARD_X + CARD_W - PADDING - TOGGLE_W - val_surf.get_width() - 10,
                                    ry - val_surf.get_height() // 2))

            elif row["type"] == "slider":
                lx = CARD_X + CARD_W - PADDING - SLIDER_W
                draw_slider(win, lx, ry, state[row["key"]], row["key"])
                pct_surf = Fonts.UI_SMALL.render(f"{state[row['key']]}%", True, HINT_COLOR)
                win.blit(pct_surf, (lx - pct_surf.get_width() - 10, ry - pct_surf.get_height() // 2))

        # ESC hint
        hint_surf = Fonts.UI_SMALL.render("ESC to close", True, HINT_COLOR)
        win.blit(hint_surf, (CARD_X + CARD_W // 2 - hint_surf.get_width() // 2,
                             CARD_Y + CARD_H - 28))

        pygame.display.flip()
