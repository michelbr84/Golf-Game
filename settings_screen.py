"""
Settings Screen - Full settings UI with toggles and sliders.
Replaces the basic audio menu with a premium glass-card style interface.
"""

import pygame
from ui_style import Colors, Fonts, draw_rounded_rect, draw_shadow, create_gradient_surface, Config


# Mapping from display labels to Config flat keys
SETTINGS_MAP = {
    "music_on":      "music_enabled",
    "sfx_on":        "sfx_enabled",
    "music_vol":     "music_volume",
    "sfx_vol":       "sfx_volume",
    "fullscreen":    "fullscreen",
    "show_fps":      "show_fps",
    "show_tutorial": "show_hints",
    "particles":     "particles_enabled",
}


def show_settings(win, config):
    """
    Display the settings screen. Runs its own event loop.
    Returns when ESC is pressed. Changes are applied immediately to Config
    and to pygame mixer.
    """
    clock = pygame.time.Clock()
    WIN_W, WIN_H = win.get_size()

    CARD_W = 700
    CARD_H = 520
    CARD_X = (WIN_W - CARD_W) // 2
    CARD_Y = (WIN_H - CARD_H) // 2

    # Load current state from Config (flat keys)
    state = {
        "music_on":      config.get("music_enabled", True),
        "sfx_on":        config.get("sfx_enabled", True),
        "music_vol":     int(config.get("music_volume", 0.5) * 100),
        "sfx_vol":       int(config.get("sfx_volume", 0.7) * 100),
        "fullscreen":    config.get("fullscreen", False),
        "show_fps":      config.get("show_fps", False),
        "show_tutorial": config.get("show_hints", True),
        "particles":     config.get("particles_enabled", True),
    }

    LABEL_COLOR = Colors.TEXT_PRIMARY
    HINT_COLOR  = Colors.TEXT_SECONDARY

    ROW_H    = 44
    TOGGLE_W = 64
    TOGGLE_H = 28
    SLIDER_W = 180
    SLIDER_H = 8
    PADDING  = 32

    dragging_slider = None

    bg = create_gradient_surface(WIN_W, WIN_H, Colors.SKY_TOP, Colors.SKY_BOTTOM)

    def draw_toggle(surface, cx, cy, value):
        rx = cx - TOGGLE_W // 2
        ry = cy - TOGGLE_H // 2
        color = Colors.ACCENT_GREEN if value else (150, 150, 160)
        draw_rounded_rect(surface, color, (rx, ry, TOGGLE_W, TOGGLE_H), TOGGLE_H // 2)
        knob_x = rx + TOGGLE_W - TOGGLE_H // 2 - 2 if value else rx + TOGGLE_H // 2 + 2
        pygame.draw.circle(surface, (255, 255, 255), (knob_x, cy), TOGGLE_H // 2 - 3)
        return pygame.Rect(rx, ry, TOGGLE_W, TOGGLE_H)

    def draw_slider(surface, lx, cy, value):
        draw_rounded_rect(surface, (180, 190, 210), (lx, cy - SLIDER_H // 2, SLIDER_W, SLIDER_H), SLIDER_H // 2)
        fill_w = int(SLIDER_W * value / 100)
        if fill_w > 0:
            draw_rounded_rect(surface, Colors.ACCENT_BLUE, (lx, cy - SLIDER_H // 2, fill_w, SLIDER_H), SLIDER_H // 2)
        knob_x = max(lx + 6, min(lx + SLIDER_W - 6, lx + fill_w))
        pygame.draw.circle(surface, Colors.ACCENT_BLUE, (knob_x, cy), 9)
        pygame.draw.circle(surface, (255, 255, 255), (knob_x, cy), 5)

    def apply_setting(state_key, value):
        """Apply a setting change to Config and pygame."""
        config_key = SETTINGS_MAP.get(state_key)
        if not config_key:
            return

        # For volume sliders, convert 0-100 to 0.0-1.0 for Config
        if state_key in ("music_vol", "sfx_vol"):
            config.set(config_key, value / 100.0)
        else:
            config.set(config_key, value)

        # Apply audio changes immediately
        try:
            if state_key == "music_on":
                if value:
                    pygame.mixer.music.unpause()
                else:
                    pygame.mixer.music.pause()
            elif state_key == "sfx_on":
                pass  # Applied when sounds play
            elif state_key == "music_vol":
                pygame.mixer.music.set_volume(value / 100.0)
            elif state_key == "sfx_vol":
                pass  # Applied per-sound when they play
            elif state_key == "fullscreen":
                if value:
                    pygame.display.set_mode((WIN_W, WIN_H), pygame.FULLSCREEN)
                else:
                    pygame.display.set_mode((WIN_W, WIN_H))
        except Exception:
            pass

    # Section layout
    sections = [
        ("AUDIO", [
            ("toggle", "Music",         "music_on"),
            ("toggle", "Sound Effects", "sfx_on"),
            ("slider", "Music Volume",  "music_vol"),
            ("slider", "SFX Volume",    "sfx_vol"),
        ]),
        ("DISPLAY", [
            ("toggle", "Fullscreen",    "fullscreen"),
            ("toggle", "Show FPS",      "show_fps"),
        ]),
        ("GAMEPLAY", [
            ("toggle", "Show Tutorial", "show_tutorial"),
            ("toggle", "Particles",     "particles"),
        ]),
    ]

    CONTENT_TOP = CARD_Y + 72
    row_data = []
    y_cursor = CONTENT_TOP + 10

    for sec_title, rows in sections:
        row_data.append({"type": "section", "title": sec_title, "y": y_cursor})
        y_cursor += 30
        for row in rows:
            row_data.append({
                "type":  row[0],
                "label": row[1],
                "key":   row[2],
                "y":     y_cursor + ROW_H // 2,
            })
            y_cursor += ROW_H
        y_cursor += 8

    running = True
    while running:
        clock.tick(60)

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
                            apply_setting(row["key"], state[row["key"]])
                    elif row["type"] == "slider":
                        lx = CARD_X + CARD_W - PADDING - SLIDER_W
                        if lx <= mx <= lx + SLIDER_W and abs(my - row_y) <= 14:
                            dragging_slider = row["key"]
                            val = max(0, min(100, int((mx - lx) / SLIDER_W * 100)))
                            state[dragging_slider] = val
                            apply_setting(dragging_slider, val)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging_slider = None

            elif event.type == pygame.MOUSEMOTION:
                if dragging_slider:
                    mx, my = event.pos
                    for row in row_data:
                        if row.get("key") == dragging_slider:
                            lx = CARD_X + CARD_W - PADDING - SLIDER_W
                            val = max(0, min(100, int((mx - lx) / SLIDER_W * 100)))
                            state[dragging_slider] = val
                            apply_setting(dragging_slider, val)
                            break

        # --- Draw ---
        win.blit(bg, (0, 0))
        draw_shadow(win, (CARD_X, CARD_Y, CARD_W, CARD_H), radius=20, offset=(6, 8), blur=4)

        card_surf = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
        card_surf.fill((255, 255, 255, 220))
        win.blit(card_surf, (CARD_X, CARD_Y))
        draw_rounded_rect(win, Colors.GLASS_BORDER, (CARD_X, CARD_Y, CARD_W, CARD_H), 20, width=2)

        title_surf = Fonts.TITLE_SMALL.render("SETTINGS", True, Colors.TEXT_PRIMARY)
        win.blit(title_surf, (CARD_X + CARD_W // 2 - title_surf.get_width() // 2, CARD_Y + 20))

        pygame.draw.line(win, (200, 210, 220),
                         (CARD_X + PADDING, CARD_Y + 65),
                         (CARD_X + CARD_W - PADDING, CARD_Y + 65), 1)

        for row in row_data:
            ry = row["y"]
            if row["type"] == "section":
                sec_surf = Fonts.HUD_SMALL.render(row["title"], True, Colors.ACCENT_BLUE)
                win.blit(sec_surf, (CARD_X + PADDING, ry - 4))
                pygame.draw.line(win, (220, 228, 240),
                                 (CARD_X + PADDING, ry + 14),
                                 (CARD_X + CARD_W - PADDING, ry + 14), 1)
                continue

            label_surf = Fonts.UI_MEDIUM.render(row["label"], True, LABEL_COLOR)
            win.blit(label_surf, (CARD_X + PADDING + 12, ry - label_surf.get_height() // 2))

            if row["type"] == "toggle":
                tx = CARD_X + CARD_W - PADDING - TOGGLE_W // 2
                draw_toggle(win, tx, ry, state[row["key"]])
                val_text = "ON" if state[row["key"]] else "OFF"
                val_color = Colors.ACCENT_GREEN if state[row["key"]] else HINT_COLOR
                val_surf = Fonts.UI_SMALL.render(val_text, True, val_color)
                win.blit(val_surf, (CARD_X + CARD_W - PADDING - TOGGLE_W - val_surf.get_width() - 10,
                                    ry - val_surf.get_height() // 2))

            elif row["type"] == "slider":
                lx = CARD_X + CARD_W - PADDING - SLIDER_W
                draw_slider(win, lx, ry, state[row["key"]])
                pct_surf = Fonts.UI_SMALL.render(f"{state[row['key']]}%", True, HINT_COLOR)
                win.blit(pct_surf, (lx - pct_surf.get_width() - 10, ry - pct_surf.get_height() // 2))

        hint_surf = Fonts.UI_SMALL.render("ESC to close", True, HINT_COLOR)
        win.blit(hint_surf, (CARD_X + CARD_W // 2 - hint_surf.get_width() // 2, CARD_Y + CARD_H - 28))

        pygame.display.flip()

    # Save config on exit
    try:
        config.save()
    except Exception:
        pass
