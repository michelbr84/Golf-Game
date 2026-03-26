"""
Multiplayer Module - Super Minigolf
Local turn-based multiplayer for 2-4 players.
"""

import pygame
from ui_style import Colors, Fonts, draw_rounded_rect

# Ball colour options shown during setup
BALL_COLORS = [
    (255, 255, 255),   # White
    (239,  68,  68),   # Red
    (59,  130, 246),   # Blue
    (34,  197,  94),   # Green
    (245, 158,  11),   # Gold
    (168,  85, 247),   # Purple
    (249, 115,  22),   # Orange
    (20,  184, 166),   # Teal
]

COLOR_NAMES = ['White', 'Red', 'Blue', 'Green', 'Gold', 'Purple', 'Orange', 'Teal']


class MultiplayerManager:
    """Manages turn-based local multiplayer state."""

    def __init__(self, num_players=2):
        self.num_players = max(2, min(4, num_players))
        self.players = []          # list of player dicts
        self.current_index = 0    # whose turn it is
        self.current_hole = 1
        # scores[player_index][hole_num] = strokes
        self.scores = [{} for _ in range(self.num_players)]

    # ── Setup screen ──────────────────────────────────────────────────────────

    def setup_players(self, win):
        """
        Pygame screen where each player enters name and picks ball colour.
        Blocks until all players are configured. Updates self.players in place.
        """
        pygame.init()
        Fonts.init()

        clock = pygame.time.Clock()
        win_w, win_h = win.get_size()

        # State machine: filling in players one at a time
        setup_index = 0       # which player we're currently configuring
        name_input = ''
        selected_color = setup_index % len(BALL_COLORS)
        error_msg = ''
        error_timer = 0
        cursor_blink = 0

        def commit_player():
            nonlocal setup_index, name_input, selected_color, error_msg, error_timer
            name = name_input.strip() or f'Player {setup_index + 1}'
            # Prevent duplicate colours
            used_colors = [p['color'] for p in self.players]
            color = BALL_COLORS[selected_color]
            if color in used_colors:
                error_msg = 'Colour already taken!'
                error_timer = 90
                return False
            self.players.append({
                'name': name,
                'color': color,
                'color_name': COLOR_NAMES[selected_color],
                'strokes_total': 0,
                'strokes_per_hole': {},
                'is_active': False,
            })
            setup_index += 1
            name_input = ''
            selected_color = setup_index % len(BALL_COLORS)
            error_msg = ''
            return True

        running = True
        while running and setup_index < self.num_players:
            cursor_blink += 1
            if error_timer > 0:
                error_timer -= 1

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Fill remaining players with defaults
                    while len(self.players) < self.num_players:
                        i = len(self.players)
                        self.players.append({
                            'name': f'Player {i + 1}',
                            'color': BALL_COLORS[i % len(BALL_COLORS)],
                            'color_name': COLOR_NAMES[i % len(COLOR_NAMES)],
                            'strokes_total': 0,
                            'strokes_per_hole': {},
                            'is_active': False,
                        })
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        commit_player()
                    elif event.key == pygame.K_BACKSPACE:
                        name_input = name_input[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        # Skip remaining players with defaults
                        while len(self.players) < self.num_players:
                            i = len(self.players)
                            self.players.append({
                                'name': f'Player {i + 1}',
                                'color': BALL_COLORS[i % len(BALL_COLORS)],
                                'color_name': COLOR_NAMES[i % len(COLOR_NAMES)],
                                'strokes_total': 0,
                                'strokes_per_hole': {},
                                'is_active': False,
                            })
                        running = False
                    elif event.unicode and len(name_input) < 16:
                        name_input += event.unicode

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    # Colour circle clicks
                    cols_per_row = 4
                    swatch_r = 24
                    swatch_start_x = win_w // 2 - (cols_per_row * (swatch_r * 2 + 12)) // 2 + swatch_r
                    swatch_start_y = win_h // 2 + 40
                    for ci, col in enumerate(BALL_COLORS):
                        row = ci // cols_per_row
                        col_pos = ci % cols_per_row
                        cx = swatch_start_x + col_pos * (swatch_r * 2 + 12)
                        cy = swatch_start_y + row * (swatch_r * 2 + 12)
                        dist = ((mx - cx) ** 2 + (my - cy) ** 2) ** 0.5
                        if dist <= swatch_r:
                            selected_color = ci

            # ── Draw ──────────────────────────────────────────────────────────
            win.fill((25, 30, 40))

            # Background panel
            panel_w, panel_h = 480, 360
            panel_x = win_w // 2 - panel_w // 2
            panel_y = win_h // 2 - panel_h // 2
            draw_rounded_rect(win, (35, 45, 60), (panel_x, panel_y, panel_w, panel_h), 12)
            draw_rounded_rect(win, (60, 80, 110), (panel_x, panel_y, panel_w, panel_h), 12, width=2)

            # Title
            title = Fonts.TITLE_SMALL.render('PLAYER SETUP', True, Colors.ACCENT_BLUE)
            win.blit(title, (win_w // 2 - title.get_width() // 2, panel_y + 16))

            # Progress dots
            for pi in range(self.num_players):
                dot_x = win_w // 2 - (self.num_players * 20) // 2 + pi * 20
                dot_col = Colors.ACCENT_BLUE if pi == setup_index else (
                    Colors.ACCENT_GREEN if pi < setup_index else (60, 70, 90)
                )
                pygame.draw.circle(win, dot_col, (dot_x, panel_y + 62), 7)

            # Current player label
            p_label = Fonts.UI_MEDIUM.render(
                f'Player {setup_index + 1} of {self.num_players}', True, Colors.TEXT_SECONDARY)
            win.blit(p_label, (win_w // 2 - p_label.get_width() // 2, panel_y + 78))

            # Name input box
            input_rect = pygame.Rect(win_w // 2 - 160, panel_y + 108, 320, 40)
            draw_rounded_rect(win, (20, 28, 40), input_rect, 8)
            draw_rounded_rect(win, Colors.ACCENT_BLUE, input_rect, 8, width=2)

            display_name = name_input + ('|' if cursor_blink % 60 < 30 else '')
            name_surf = Fonts.UI_LARGE.render(display_name or 'Enter name...', True,
                                              Colors.TEXT_LIGHT if name_input else Colors.TEXT_SECONDARY)
            win.blit(name_surf, (input_rect.x + 10, input_rect.y + 8))

            hint = Fonts.UI_TINY.render('Press Enter to confirm', True, Colors.TEXT_SECONDARY)
            win.blit(hint, (win_w // 2 - hint.get_width() // 2, panel_y + 154))

            # Colour picker label
            color_label = Fonts.UI_SMALL.render('Pick ball colour:', True, Colors.TEXT_PRIMARY)
            win.blit(color_label, (win_w // 2 - color_label.get_width() // 2, panel_y + 178))

            # Colour circles
            cols_per_row = 4
            swatch_r = 24
            swatch_start_x = win_w // 2 - (cols_per_row * (swatch_r * 2 + 12)) // 2 + swatch_r
            swatch_start_y = win_h // 2 + 40
            used_colors = [p['color'] for p in self.players]
            for ci, col in enumerate(BALL_COLORS):
                row = ci // cols_per_row
                col_pos = ci % cols_per_row
                cx = swatch_start_x + col_pos * (swatch_r * 2 + 12)
                cy = swatch_start_y + row * (swatch_r * 2 + 12)
                is_used = col in used_colors
                is_selected = ci == selected_color
                draw_r = swatch_r - 4 if is_used else swatch_r
                draw_col = tuple(max(0, c - 80) for c in col) if is_used else col
                pygame.draw.circle(win, draw_col, (cx, cy), draw_r)
                if is_selected:
                    pygame.draw.circle(win, Colors.TEXT_LIGHT, (cx, cy), swatch_r, 3)
                elif is_used:
                    x_s = 4
                    pygame.draw.line(win, (200, 50, 50), (cx - x_s, cy - x_s), (cx + x_s, cy + x_s), 2)
                    pygame.draw.line(win, (200, 50, 50), (cx + x_s, cy - x_s), (cx - x_s, cy + x_s), 2)

            # Selected colour name
            sel_name = COLOR_NAMES[selected_color]
            sel_surf = Fonts.UI_TINY.render(sel_name, True, BALL_COLORS[selected_color])
            win.blit(sel_surf, (win_w // 2 - sel_surf.get_width() // 2, swatch_start_y + 70))

            # Error message
            if error_timer > 0:
                err_surf = Fonts.UI_SMALL.render(error_msg, True, Colors.ACCENT_RED)
                win.blit(err_surf, (win_w // 2 - err_surf.get_width() // 2, panel_y + panel_h - 30))

            # Previously set players preview
            if self.players:
                prev_label = Fonts.UI_TINY.render('Confirmed players:', True, Colors.TEXT_SECONDARY)
                win.blit(prev_label, (panel_x + 10, panel_y + panel_h + 10))
                for pi, p in enumerate(self.players):
                    pygame.draw.circle(win, p['color'], (panel_x + 20, panel_y + panel_h + 30 + pi * 22), 8)
                    p_surf = Fonts.UI_TINY.render(p['name'], True, Colors.TEXT_LIGHT)
                    win.blit(p_surf, (panel_x + 35, panel_y + panel_h + 22 + pi * 22))

            pygame.display.flip()
            clock.tick(60)

        # Mark first player active
        if self.players:
            self.players[0]['is_active'] = True

    # ── Turn management ───────────────────────────────────────────────────────

    def get_current_player(self):
        """Return current player dict."""
        if not self.players:
            return None
        return self.players[self.current_index]

    def next_turn(self):
        """Advance to next player; if all done with hole, increment hole."""
        if not self.players:
            return
        self.players[self.current_index]['is_active'] = False
        self.current_index = (self.current_index + 1) % self.num_players
        if self.current_index == 0:
            # Full round done — advance hole
            self.current_hole += 1
        self.players[self.current_index]['is_active'] = True

    def record_strokes(self, hole_num, strokes):
        """Record strokes for the current player on the given hole."""
        player = self.get_current_player()
        if player is None:
            return
        player['strokes_per_hole'][hole_num] = strokes
        player['strokes_total'] = sum(player['strokes_per_hole'].values())
        self.scores[self.current_index][hole_num] = strokes

    def all_finished_hole(self, hole_num):
        """True if every player has a score recorded for hole_num."""
        return all(
            hole_num in self.scores[i]
            for i in range(self.num_players)
        )

    def get_final_rankings(self):
        """Return list of player dicts sorted by total strokes ascending."""
        return sorted(self.players, key=lambda p: p['strokes_total'])

    def is_course_complete(self):
        """True if all players finished all holes (checks current_hole progression)."""
        return all(
            len(self.scores[i]) >= self.current_hole
            for i in range(self.num_players)
        )

    # ── HUD drawing ───────────────────────────────────────────────────────────

    def draw_turn_indicator(self, surface):
        """Draw 'Player X's Turn' HUD at top-centre of the surface."""
        player = self.get_current_player()
        if not player:
            return

        text = f"{player['name']}'s Turn"
        text_surf = Fonts.HUD_MEDIUM.render(text, True, Colors.TEXT_LIGHT)
        sw = surface.get_width()
        bg_w = text_surf.get_width() + 60
        bg_x = sw // 2 - bg_w // 2

        draw_rounded_rect(surface, (30, 40, 55), (bg_x, 6, bg_w, 32), 8)
        draw_rounded_rect(surface, player['color'], (bg_x, 6, bg_w, 32), 8, width=2)

        # Ball colour dot
        pygame.draw.circle(surface, player['color'], (bg_x + 20, 22), 10)
        pygame.draw.circle(surface, (255, 255, 255), (bg_x + 20, 22), 10, 2)

        surface.blit(text_surf, (bg_x + 36, 14))

    def draw_scoreboard(self, surface):
        """Draw full multiplayer scoreboard (end of course)."""
        Fonts.init()
        sw, sh = surface.get_width(), surface.get_height()

        # Dim background
        dim = pygame.Surface((sw, sh), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 160))
        surface.blit(dim, (0, 0))

        rankings = self.get_final_rankings()
        num_holes = max(
            (max(p['strokes_per_hole'].keys(), default=0) for p in self.players),
            default=0
        )

        col_hole_w = 40
        col_name_w = 160
        row_h = 32
        header_h = 40
        padding = 16

        cols = num_holes + 2  # name + holes + total
        board_w = col_name_w + cols * col_hole_w + padding * 2
        board_h = header_h + (self.num_players + 1) * row_h + padding * 2 + 50
        bx = sw // 2 - board_w // 2
        by = sh // 2 - board_h // 2

        draw_rounded_rect(surface, (30, 38, 52), (bx, by, board_w, board_h), 12)
        draw_rounded_rect(surface, Colors.ACCENT_BLUE, (bx, by, board_w, board_h), 12, width=2)

        # Title
        title = Fonts.TITLE_SMALL.render('FINAL SCORES', True, Colors.ACCENT_GOLD)
        surface.blit(title, (sw // 2 - title.get_width() // 2, by + padding))

        # Header row
        hx = bx + padding
        hy = by + padding + header_h
        name_h = Fonts.HUD_SMALL.render('Player', True, Colors.TEXT_SECONDARY)
        surface.blit(name_h, (hx, hy))
        for h in range(1, num_holes + 1):
            hx_col = hx + col_name_w + (h - 1) * col_hole_w
            h_surf = Fonts.UI_TINY.render(f'H{h}', True, Colors.TEXT_SECONDARY)
            surface.blit(h_surf, (hx_col, hy + 6))
        tot_x = hx + col_name_w + num_holes * col_hole_w
        tot_h = Fonts.HUD_SMALL.render('Tot', True, Colors.TEXT_SECONDARY)
        surface.blit(tot_h, (tot_x, hy))

        pygame.draw.line(surface, (60, 80, 110),
                         (bx + padding, hy + row_h - 4),
                         (bx + board_w - padding, hy + row_h - 4), 1)

        # Player rows
        medal_colors = [Colors.ACCENT_GOLD, (192, 192, 192), (180, 100, 60)]
        for ri, player in enumerate(rankings):
            ry = hy + row_h + ri * row_h
            row_col = (40, 52, 68) if ri % 2 == 0 else (35, 45, 60)
            draw_rounded_rect(surface, row_col,
                              (bx + padding, ry, board_w - padding * 2, row_h - 2), 4)

            # Medal
            if ri < 3:
                pygame.draw.circle(surface, medal_colors[ri],
                                   (bx + padding + 12, ry + row_h // 2), 8)

            # Name with ball colour dot
            pygame.draw.circle(surface, player['color'],
                               (bx + padding + 30, ry + row_h // 2), 8)
            n_surf = Fonts.UI_SMALL.render(player['name'], True, Colors.TEXT_LIGHT)
            surface.blit(n_surf, (bx + padding + 44, ry + 8))

            # Hole scores
            for h in range(1, num_holes + 1):
                hx_col = bx + padding + col_name_w + (h - 1) * col_hole_w
                score = player['strokes_per_hole'].get(h, '-')
                s_surf = Fonts.UI_SMALL.render(str(score), True, Colors.TEXT_LIGHT)
                surface.blit(s_surf, (hx_col, ry + 8))

            # Total
            tot_x2 = bx + padding + col_name_w + num_holes * col_hole_w
            t_col = Colors.ACCENT_GOLD if ri == 0 else Colors.TEXT_LIGHT
            t_surf = Fonts.HUD_SMALL.render(str(player['strokes_total']), True, t_col)
            surface.blit(t_surf, (tot_x2, ry + 7))

        # Winner banner
        if rankings:
            winner_text = f"{rankings[0]['name']} wins!"
            w_surf = Fonts.TITLE_SMALL.render(winner_text, True, Colors.ACCENT_GOLD)
            surface.blit(w_surf, (sw // 2 - w_surf.get_width() // 2,
                                  by + board_h - 40))
