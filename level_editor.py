"""
Level Editor - Super Minigolf
Visual drag-and-drop level editor. Call run_editor(win) to launch.
Returns level data (list of objects) when Test is clicked, or None on ESC/close.
"""

import pygame
import json
import os
from ui_style import Colors, Fonts, draw_rounded_rect

# ── Layout ────────────────────────────────────────────────────────────────────
CANVAS_W = 850
CANVAS_H = 600
TOOLBAR_X = CANVAS_W
TOOLBAR_W = 230
GRID = 16
MAX_UNDO = 20

# ── Object colours (editor representation) ───────────────────────────────────
OBJ_COLORS = {
    'floor':  (139, 90,  43),   # wood brown
    'wall':   (80,  80,  80),   # dark grey
    'water':  (30, 120, 200),   # blue
    'sand':   (210, 180, 100),  # sandy
    'laser':  (220,  50,  50),  # red
    'sticky': (160,  80, 200),  # purple
    'green':  (50,  180,  80),  # bright green
    'coin':   (245, 158,  11),  # gold
    'flag':   (239,  68,  68),  # red flag
}

TOOL_ORDER = ['floor', 'wall', 'water', 'sand', 'laser', 'sticky', 'green', 'coin', 'flag']

SAVE_PATH = os.path.join(os.path.dirname(__file__), 'custom_levels.json')


# ── Helpers ───────────────────────────────────────────────────────────────────

def snap(v):
    return (v // GRID) * GRID


def make_obj(x, y, w, h, otype):
    """Return an object list in courses.py format."""
    w = max(GRID, w)
    h = max(GRID, h)
    if otype == 'coin':
        return [x, y, w, h, 'coin', True]
    return [x, y, w, h, otype]


def calc_start(objects):
    """Auto-calculate start position from leftmost floor platform."""
    floors = [o for o in objects if o[4] == 'floor']
    if not floors:
        return (50, 500)
    leftmost = min(floors, key=lambda o: o[0])
    return (leftmost[0] + leftmost[2] // 2, leftmost[1] - 12)


def calc_par(objects):
    """3 + obstacle_count // 2."""
    obstacles = [o for o in objects if o[4] in ('wall', 'water', 'sand', 'laser', 'sticky')]
    return 3 + len(obstacles) // 2


def has_flag(objects):
    return any(o[4] == 'flag' for o in objects)


def has_green(objects):
    return any(o[4] == 'green' for o in objects)


def draw_object(surface, obj, offset=(0, 0)):
    """Render a single level object on the editor canvas."""
    ox, oy = offset
    x, y, w, h = obj[0] + ox, obj[1] + oy, obj[2], obj[3]
    otype = obj[4]
    color = OBJ_COLORS.get(otype, (200, 200, 200))

    rect = pygame.Rect(x, y, w, h)

    if otype == 'floor':
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, (100, 60, 20), rect, 1)
        # Top highlight stripe
        pygame.draw.rect(surface, (180, 130, 70), (x, y, w, 4))
    elif otype == 'wall':
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, (50, 50, 50), rect, 1)
        for i in range(y, y + h, 8):
            pygame.draw.line(surface, (100, 100, 100), (x, i), (x + w, i), 1)
    elif otype == 'water':
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, (10, 80, 160), rect, 1)
        for i in range(x, x + w, 12):
            pygame.draw.arc(surface, (80, 170, 255), (i, y + h // 2 - 3, 12, 6), 0, 3.14, 2)
    elif otype == 'sand':
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, (160, 130, 60), rect, 1)
    elif otype == 'laser':
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, (255, 100, 100), rect, 2)
        cx = x + w // 2
        pygame.draw.line(surface, (255, 200, 200), (cx, y), (cx, y + h), 1)
    elif otype == 'sticky':
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, (120, 50, 180), rect, 2)
        for i in range(y, y + h, 10):
            pygame.draw.line(surface, (200, 150, 255), (x, i), (x + w, i), 1)
    elif otype == 'green':
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, (20, 140, 50), rect, 1)
    elif otype == 'coin':
        cx, cy = x + w // 2, y + h // 2
        r = min(w, h) // 2
        pygame.draw.circle(surface, color, (cx, cy), max(r, 6))
        pygame.draw.circle(surface, (200, 120, 5), (cx, cy), max(r, 6), 2)
    elif otype == 'flag':
        # Pole
        pygame.draw.rect(surface, (60, 60, 60), (x + w // 2 - 2, y, 4, h))
        # Flag cloth
        flag_pts = [
            (x + w // 2 + 2, y + 4),
            (x + w // 2 + 24, y + 12),
            (x + w // 2 + 2, y + 20),
        ]
        pygame.draw.polygon(surface, color, flag_pts)


# ── Toolbar button helper ─────────────────────────────────────────────────────

class ToolbarButton:
    def __init__(self, label, rect, color=None, action=None):
        self.label = label
        self.rect = pygame.Rect(rect)
        self.color = color
        self.action = action

    def draw(self, surface, selected=False, hover=False):
        bg = Colors.ACCENT_BLUE if selected else (60, 70, 90) if hover else (40, 50, 65)
        draw_rounded_rect(surface, bg, self.rect, 6)
        draw_rounded_rect(surface, (80, 100, 130), self.rect, 6, width=1)

        if self.color:
            swatch = pygame.Rect(self.rect.x + 6, self.rect.centery - 8, 16, 16)
            pygame.draw.rect(surface, self.color, swatch, border_radius=3)

        label_surf = Fonts.UI_SMALL.render(self.label, True, Colors.TEXT_LIGHT)
        lx = self.rect.x + (28 if self.color else 10)
        ly = self.rect.centery - label_surf.get_height() // 2
        surface.blit(label_surf, (lx, ly))

    def is_hovered(self, pos):
        return self.rect.collidepoint(pos)


# ── Main editor function ──────────────────────────────────────────────────────

def run_editor(win):
    """
    Run the level editor. Returns level data list when Test is pressed,
    or None when ESC is pressed / window closed.
    """
    pygame.init()
    Fonts.init()

    clock = pygame.time.Clock()

    # State
    objects = []          # list of obj lists
    undo_stack = []       # list of snapshots
    selected_tool = 'floor'
    show_grid = True
    drag_start = None     # (canvas_x, canvas_y) snap-aligned
    drag_current = None
    hover_obj = None
    message = ''
    message_timer = 0
    camera_offset = [0, 0]  # future scrolling

    # Build tool buttons (right panel)
    tool_buttons = []
    by = 10
    for t in TOOL_ORDER:
        btn = ToolbarButton(t.capitalize(), (TOOLBAR_X + 10, by, 210, 34), OBJ_COLORS[t], t)
        tool_buttons.append(btn)
        by += 38

    # Bottom action buttons
    save_btn  = ToolbarButton('Save',  (TOOLBAR_X + 10, 400, 95, 36))
    load_btn  = ToolbarButton('Load',  (TOOLBAR_X + 115, 400, 95, 36))
    test_btn  = ToolbarButton('Test',  (TOOLBAR_X + 10,  444, 95, 36))
    clear_btn = ToolbarButton('Clear', (TOOLBAR_X + 115, 444, 95, 36))
    action_buttons = [save_btn, load_btn, test_btn, clear_btn]

    # Grid toggle label
    grid_label = Fonts.UI_TINY.render('G = toggle grid', True, Colors.TEXT_SECONDARY)

    def push_undo():
        snap_copy = [list(o) for o in objects]
        undo_stack.append(snap_copy)
        if len(undo_stack) > MAX_UNDO:
            undo_stack.pop(0)

    def object_at(mx, my):
        """Return first object under canvas mouse position."""
        for obj in reversed(objects):
            r = pygame.Rect(obj[0], obj[1], obj[2], obj[3])
            if r.collidepoint(mx, my):
                return obj
        return None

    def set_message(msg, duration=120):
        nonlocal message, message_timer
        message = msg
        message_timer = duration

    def do_save():
        if not has_flag(objects):
            set_message('Need a Flag before saving!', 150)
            return
        if not has_green(objects):
            set_message('Need a Green before saving!', 150)
            return
        start = calc_start(objects)
        par = calc_par(objects)
        level_data = {
            'objects': [list(o) for o in objects],
            'start': list(start),
            'par': par,
        }
        try:
            existing = []
            if os.path.exists(SAVE_PATH):
                with open(SAVE_PATH, 'r') as f:
                    existing = json.load(f)
            existing.append(level_data)
            with open(SAVE_PATH, 'w') as f:
                json.dump(existing, f, indent=2)
            set_message('Level saved!', 120)
        except Exception as e:
            set_message(f'Save error: {e}', 180)

    def do_load():
        nonlocal objects
        if not os.path.exists(SAVE_PATH):
            set_message('No custom_levels.json found.', 120)
            return
        try:
            with open(SAVE_PATH, 'r') as f:
                data = json.load(f)
            if not data:
                set_message('File is empty.', 120)
                return
            push_undo()
            objects = [list(o) for o in data[-1]['objects']]
            set_message(f'Loaded {len(data)} level(s). Showing last.', 120)
        except Exception as e:
            set_message(f'Load error: {e}', 180)

    def do_test():
        if not has_flag(objects):
            set_message('Need a Flag to test!', 150)
            return None
        if not has_green(objects):
            set_message('Need a Green to test!', 150)
            return None
        start = calc_start(objects)
        par = calc_par(objects)
        return {
            'objects': [list(o) for o in objects],
            'start': list(start),
            'par': par,
        }

    running = True
    test_result = None

    while running:
        mx, my = pygame.mouse.get_pos()
        canvas_mx = mx - camera_offset[0]
        canvas_my = my - camera_offset[1]
        on_canvas = 0 <= mx < CANVAS_W

        # Hover detection
        hover_obj = None
        if on_canvas and drag_start is None:
            hover_obj = object_at(canvas_mx, canvas_my)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_g:
                    show_grid = not show_grid
                elif event.key == pygame.K_z and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    if undo_stack:
                        objects = undo_stack.pop()
                        set_message('Undo', 60)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left-click
                    if on_canvas:
                        push_undo()
                        sx, sy = snap(canvas_mx), snap(canvas_my)
                        drag_start = (sx, sy)
                        drag_current = (sx, sy)
                    else:
                        # Toolbar clicks
                        for btn in tool_buttons:
                            if btn.is_hovered((mx, my)):
                                selected_tool = btn.action
                        if save_btn.is_hovered((mx, my)):
                            do_save()
                        elif load_btn.is_hovered((mx, my)):
                            do_load()
                        elif test_btn.is_hovered((mx, my)):
                            result = do_test()
                            if result is not None:
                                test_result = result
                                running = False
                        elif clear_btn.is_hovered((mx, my)):
                            push_undo()
                            objects.clear()
                            set_message('Canvas cleared.', 90)

                elif event.button == 3:  # Right-click — delete
                    if on_canvas:
                        obj = object_at(canvas_mx, canvas_my)
                        if obj:
                            push_undo()
                            objects.remove(obj)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and drag_start is not None and on_canvas:
                    sx, sy = drag_start
                    ex, ey = snap(canvas_mx), snap(canvas_my)
                    x = min(sx, ex)
                    y = min(sy, ey)
                    w = max(abs(ex - sx), GRID)
                    h = max(abs(ey - sy), GRID)
                    obj = make_obj(x, y, w, h, selected_tool)
                    objects.append(obj)
                    drag_start = None
                    drag_current = None

            elif event.type == pygame.MOUSEMOTION:
                if drag_start is not None:
                    drag_current = (snap(canvas_mx), snap(canvas_my))

        # ── Drawing ───────────────────────────────────────────────────────────
        win.fill((25, 30, 40))

        # Canvas background
        canvas_surf = pygame.Surface((CANVAS_W, CANVAS_H))
        canvas_surf.fill((35, 42, 55))

        # Grid
        if show_grid:
            for gx in range(0, CANVAS_W, GRID):
                pygame.draw.line(canvas_surf, (45, 55, 70), (gx, 0), (gx, CANVAS_H), 1)
            for gy in range(0, CANVAS_H, GRID):
                pygame.draw.line(canvas_surf, (45, 55, 70), (0, gy), (CANVAS_W, gy), 1)

        # Objects
        for obj in objects:
            draw_object(canvas_surf, obj)

        # Hover highlight
        if hover_obj:
            r = pygame.Rect(hover_obj[0], hover_obj[1], hover_obj[2], hover_obj[3])
            pygame.draw.rect(canvas_surf, (255, 255, 255), r, 2)
            # Label
            lbl = Fonts.UI_TINY.render(hover_obj[4], True, (255, 255, 200))
            canvas_surf.blit(lbl, (hover_obj[0] + 2, hover_obj[1] + 2))

        # Drag preview
        if drag_start is not None and drag_current is not None:
            sx, sy = drag_start
            ex, ey = drag_current
            x = min(sx, ex)
            y = min(sy, ey)
            w = max(abs(ex - sx), GRID)
            h = max(abs(ey - sy), GRID)
            color = OBJ_COLORS.get(selected_tool, (200, 200, 200))
            preview = pygame.Surface((w, h), pygame.SRCALPHA)
            preview.fill((*color, 120))
            canvas_surf.blit(preview, (x, y))
            pygame.draw.rect(canvas_surf, color, (x, y, w, h), 2)

        win.blit(canvas_surf, (0, 0))

        # Canvas border
        pygame.draw.rect(win, (60, 80, 110), (0, 0, CANVAS_W, CANVAS_H), 2)

        # ── Toolbar background ─────────────────────────────────────────────
        tb_rect = pygame.Rect(TOOLBAR_X, 0, TOOLBAR_W, CANVAS_H)
        pygame.draw.rect(win, (30, 38, 52), tb_rect)
        pygame.draw.line(win, (60, 80, 110), (TOOLBAR_X, 0), (TOOLBAR_X, CANVAS_H), 2)

        # Title
        title = Fonts.HUD_SMALL.render('LEVEL EDITOR', True, Colors.ACCENT_BLUE)
        win.blit(title, (TOOLBAR_X + 10, CANVAS_H - 590))

        # Tool buttons
        for btn in tool_buttons:
            hovered = btn.is_hovered((mx, my))
            selected = (btn.action == selected_tool)
            btn.draw(win, selected=selected, hover=hovered)

        # Separator
        pygame.draw.line(win, (60, 80, 110), (TOOLBAR_X + 10, 375), (TOOLBAR_X + 220, 375), 1)

        # Action buttons
        for btn in action_buttons:
            btn.draw(win, hover=btn.is_hovered((mx, my)))

        # Grid toggle hint
        win.blit(grid_label, (TOOLBAR_X + 10, 490))

        # Object count info
        info_y = 510
        cnt_surf = Fonts.UI_TINY.render(f'Objects: {len(objects)}', True, Colors.TEXT_SECONDARY)
        win.blit(cnt_surf, (TOOLBAR_X + 10, info_y))

        flag_ok = has_flag(objects)
        green_ok = has_green(objects)
        flag_col = Colors.ACCENT_GREEN if flag_ok else Colors.ACCENT_RED
        green_col = Colors.ACCENT_GREEN if green_ok else Colors.ACCENT_RED
        f_surf = Fonts.UI_TINY.render(f'Flag: {"OK" if flag_ok else "missing"}', True, flag_col)
        g_surf = Fonts.UI_TINY.render(f'Green: {"OK" if green_ok else "missing"}', True, green_col)
        win.blit(f_surf, (TOOLBAR_X + 10, info_y + 16))
        win.blit(g_surf, (TOOLBAR_X + 10, info_y + 30))

        par_val = calc_par(objects)
        p_surf = Fonts.UI_TINY.render(f'Par: {par_val}', True, Colors.TEXT_SECONDARY)
        win.blit(p_surf, (TOOLBAR_X + 10, info_y + 46))

        # Message overlay
        if message_timer > 0:
            message_timer -= 1
            alpha = min(255, message_timer * 4)
            msg_surf = Fonts.UI_MEDIUM.render(message, True, (255, 220, 100))
            msg_surf.set_alpha(alpha)
            win.blit(msg_surf, (CANVAS_W // 2 - msg_surf.get_width() // 2, CANVAS_H - 40))

        pygame.display.flip()
        clock.tick(60)

    return test_result  # None on ESC, dict on Test
