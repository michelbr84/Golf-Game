"""
UI Style Module - Super Minigolf Premium Visual System
Provides modern UI components with glassmorphism, shadows, and premium aesthetics.
"""

import pygame
import math

# ============================================================================
# COLOR PALETTE - Premium Theme
# ============================================================================

class Colors:
    """Premium color palette with carefully selected colors"""
    
    # Background/Sky gradient
    SKY_TOP = (135, 180, 220)        # Soft pastel blue
    SKY_BOTTOM = (200, 220, 240)     # Very light blue
    
    # UI Colors (Glassmorphism)
    GLASS_BG = (255, 255, 255, 40)   # Semi-transparent white
    GLASS_BORDER = (255, 255, 255, 80)
    SHADOW = (0, 0, 0, 30)           # Soft shadow
    SHADOW_DARK = (0, 0, 0, 60)
    
    # Text Colors
    TEXT_PRIMARY = (45, 55, 72)      # Dark slate
    TEXT_SECONDARY = (100, 116, 139) # Slate gray
    TEXT_LIGHT = (255, 255, 255)     # White
    TEXT_ACCENT = (59, 130, 246)     # Blue accent
    
    # Accent Colors (for foreground elements - more saturated)
    ACCENT_GREEN = (34, 197, 94)     # Vibrant green
    ACCENT_RED = (239, 68, 68)       # Vibrant red
    ACCENT_ORANGE = (249, 115, 22)   # Vibrant orange
    ACCENT_PURPLE = (168, 85, 247)   # Vibrant purple
    ACCENT_BLUE = (59, 130, 246)     # Vibrant blue
    ACCENT_GOLD = (245, 158, 11)     # Gold for coins
    
    # UI States
    HOVER = (255, 255, 255, 60)
    PRESSED = (0, 0, 0, 20)
    
    # Score colors
    SCORE_GOOD = (34, 197, 94)       # Under par - green
    SCORE_BAD = (239, 68, 68)        # Over par - red
    SCORE_PAR = (100, 116, 139)      # Par - gray

# ============================================================================
# FONTS - Typography System
# ============================================================================

class Fonts:
    """Modern typography system - initialized after pygame.init()"""
    
    _initialized = False
    
    # Font names to try (in order of preference)
    DISPLAY_FONTS = ['Segoe UI Black', 'Arial Black', 'Impact', 'Helvetica Bold']
    UI_FONTS = ['Segoe UI', 'Arial', 'Helvetica', 'Verdana']
    
    @classmethod
    def init(cls):
        """Initialize fonts - call after pygame.init()"""
        if cls._initialized:
            return
            
        # Find best available display font
        display_font = None
        for font_name in cls.DISPLAY_FONTS:
            if font_name.lower() in [f.lower() for f in pygame.font.get_fonts()]:
                display_font = font_name
                break
        if not display_font:
            display_font = None  # Use pygame default
        
        # Find best available UI font
        ui_font = None
        for font_name in cls.UI_FONTS:
            if font_name.lower().replace(' ', '') in [f.lower() for f in pygame.font.get_fonts()]:
                ui_font = font_name
                break
        if not ui_font:
            ui_font = None  # Use pygame default
        
        # Create fonts
        cls.TITLE_LARGE = pygame.font.SysFont(display_font, 56, bold=True)
        cls.TITLE_MEDIUM = pygame.font.SysFont(display_font, 42, bold=True)
        cls.TITLE_SMALL = pygame.font.SysFont(display_font, 32, bold=True)
        
        cls.UI_LARGE = pygame.font.SysFont(ui_font, 28)
        cls.UI_MEDIUM = pygame.font.SysFont(ui_font, 22)
        cls.UI_SMALL = pygame.font.SysFont(ui_font, 18)
        cls.UI_TINY = pygame.font.SysFont(ui_font, 14)
        
        cls.HUD_LARGE = pygame.font.SysFont(ui_font, 26, bold=True)
        cls.HUD_MEDIUM = pygame.font.SysFont(ui_font, 20, bold=True)
        cls.HUD_SMALL = pygame.font.SysFont(ui_font, 16, bold=True)
        
        cls._initialized = True
        print("[UI] Fonts initialized successfully")

# ============================================================================
# DRAWING UTILITIES
# ============================================================================

def draw_rounded_rect(surface, color, rect, radius, width=0):
    """
    Draw a rounded rectangle on a surface.
    
    Args:
        surface: Pygame surface to draw on
        color: Color of the rectangle (RGB or RGBA)
        rect: (x, y, width, height) tuple
        radius: Corner radius in pixels
        width: Border width (0 = filled)
    """
    x, y, w, h = rect
    radius = min(radius, w // 2, h // 2)
    
    if len(color) == 4:  # RGBA
        # Create a temporary surface with alpha
        temp_surface = pygame.Surface((w, h), pygame.SRCALPHA)
        
        # Draw the rounded rectangle on temp surface
        pygame.draw.rect(temp_surface, color, (radius, 0, w - 2 * radius, h), width)
        pygame.draw.rect(temp_surface, color, (0, radius, w, h - 2 * radius), width)
        pygame.draw.circle(temp_surface, color, (radius, radius), radius, width)
        pygame.draw.circle(temp_surface, color, (w - radius, radius), radius, width)
        pygame.draw.circle(temp_surface, color, (radius, h - radius), radius, width)
        pygame.draw.circle(temp_surface, color, (w - radius, h - radius), radius, width)
        
        surface.blit(temp_surface, (x, y))
    else:
        # Regular RGB - use pygame's built-in if available
        pygame.draw.rect(surface, color, rect, width, radius)


def create_gradient_surface(width, height, top_color, bottom_color):
    """
    Create a vertical gradient surface.
    
    Args:
        width: Width of the surface
        height: Height of the surface
        top_color: RGB color at the top
        bottom_color: RGB color at the bottom
    
    Returns:
        Pygame surface with gradient
    """
    surface = pygame.Surface((width, height))
    
    for y in range(height):
        # Calculate interpolation factor
        factor = y / height
        
        # Interpolate between colors
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * factor)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * factor)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * factor)
        
        pygame.draw.line(surface, (r, g, b), (0, y), (width, y))
    
    return surface


def create_vignette(width, height, intensity=80, radius_factor=0.7):
    """
    Create a vignette overlay surface.
    
    Args:
        width: Width of the surface
        height: Height of the surface
        intensity: Maximum darkness at corners (0-255)
        radius_factor: How far the vignette extends (0-1)
    
    Returns:
        Pygame surface with vignette effect
    """
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    
    center_x, center_y = width // 2, height // 2
    max_dist = math.sqrt(center_x ** 2 + center_y ** 2)
    start_dist = max_dist * radius_factor
    
    for y in range(0, height, 4):  # Skip pixels for performance
        for x in range(0, width, 4):
            dist = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
            
            if dist > start_dist:
                alpha = int((dist - start_dist) / (max_dist - start_dist) * intensity)
                alpha = min(alpha, intensity)
                pygame.draw.rect(surface, (0, 0, 0, alpha), (x, y, 4, 4))
    
    return surface


def draw_shadow(surface, rect, radius=8, offset=(4, 4), blur=3):
    """
    Draw a soft shadow for a rectangular element.
    
    Args:
        surface: Surface to draw on
        rect: (x, y, width, height) of the element
        radius: Corner radius of the shadow
        offset: (x, y) offset of shadow from element
        blur: Blur amount (number of shadow layers)
    """
    x, y, w, h = rect
    shadow_x = x + offset[0]
    shadow_y = y + offset[1]
    
    # Draw multiple layers for blur effect
    for i in range(blur):
        alpha = int(30 / (i + 1))
        expand = i * 2
        draw_rounded_rect(
            surface,
            (0, 0, 0, alpha),
            (shadow_x - expand, shadow_y - expand, w + expand * 2, h + expand * 2),
            radius + expand
        )


def draw_ball_shadow(surface, ball_pos, ball_radius=5, ground_y=None):
    """
    Draw an elliptical shadow beneath the ball.
    
    Args:
        surface: Surface to draw on
        ball_pos: (x, y) position of the ball
        ball_radius: Radius of the ball
        ground_y: Y position of the ground (if None, uses ball_pos[1] + offset)
    """
    x, y = ball_pos
    
    if ground_y is None:
        shadow_y = y + ball_radius + 2
    else:
        shadow_y = ground_y
    
    # Calculate shadow size based on distance from ground
    distance = shadow_y - y
    scale = max(0.3, 1 - distance / 100)
    
    shadow_width = int(ball_radius * 2.5 * scale)
    shadow_height = int(ball_radius * 0.6 * scale)
    
    # Create shadow surface with alpha
    shadow_surface = pygame.Surface((shadow_width * 2, shadow_height * 2), pygame.SRCALPHA)
    
    # Draw ellipse shadow
    pygame.draw.ellipse(
        shadow_surface,
        (0, 0, 0, int(40 * scale)),
        (shadow_width // 2, shadow_height // 2, shadow_width, shadow_height)
    )
    
    surface.blit(shadow_surface, (x - shadow_width, shadow_y - shadow_height // 2))


def draw_ball_premium(surface, pos, color, radius=5):
    """
    Draw a premium ball with highlight and depth.
    
    Args:
        surface: Surface to draw on
        pos: (x, y) center position
        color: Base color of the ball
        radius: Radius of the ball
    """
    x, y = pos
    
    # Draw outer ring (slightly darker)
    darker = tuple(max(0, c - 40) for c in color[:3])
    pygame.draw.circle(surface, (0, 0, 0), (x, y), radius + 1)
    pygame.draw.circle(surface, darker, (x, y), radius)
    
    # Draw main ball
    pygame.draw.circle(surface, color, (x, y), radius - 1)
    
    # Draw highlight (top-left)
    highlight_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    highlight_pos = (radius - 2, radius - 2)
    pygame.draw.circle(highlight_surface, (255, 255, 255, 120), highlight_pos, radius // 2)
    surface.blit(highlight_surface, (x - radius, y - radius))


# ============================================================================
# UI COMPONENTS
# ============================================================================

class GlassCard:
    """A modern glass-effect card component"""
    
    def __init__(self, x, y, width, height, radius=16):
        self.rect = (x, y, width, height)
        self.radius = radius
        self.surface = None
        self._create_surface()
    
    def _create_surface(self):
        """Create the card surface with glass effect"""
        x, y, w, h = self.rect
        self.surface = pygame.Surface((w, h), pygame.SRCALPHA)
        
        # Background
        draw_rounded_rect(self.surface, Colors.GLASS_BG, (0, 0, w, h), self.radius)
        
        # Border (lighter top, gives 3D effect)
        border_surface = pygame.Surface((w, h), pygame.SRCALPHA)
        draw_rounded_rect(border_surface, (255, 255, 255, 30), (0, 0, w, 2), self.radius)
        self.surface.blit(border_surface, (0, 0))
    
    def draw(self, target_surface, with_shadow=True):
        """Draw the card on the target surface"""
        x, y, w, h = self.rect
        
        if with_shadow:
            draw_shadow(target_surface, self.rect, self.radius, (3, 3), 2)
        
        target_surface.blit(self.surface, (x, y))
    
    def draw_text(self, target_surface, text, font, color, align='center', padding=10):
        """Draw text inside the card"""
        x, y, w, h = self.rect
        text_surface = font.render(text, True, color)
        
        if align == 'center':
            text_x = x + (w - text_surface.get_width()) // 2
        elif align == 'left':
            text_x = x + padding
        else:  # right
            text_x = x + w - text_surface.get_width() - padding
        
        text_y = y + (h - text_surface.get_height()) // 2
        target_surface.blit(text_surface, (text_x, text_y))


class HUDCard:
    """A compact HUD card for displaying game info"""
    
    def __init__(self, x, y, icon, value, width=120, height=45):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.icon = icon
        self.value = value
        self.radius = 12
    
    def update_value(self, value):
        self.value = value
    
    def draw(self, surface, font):
        """Draw the HUD card"""
        # Shadow
        draw_shadow(surface, (self.x, self.y, self.width, self.height), self.radius, (2, 2), 2)
        
        # Card background
        draw_rounded_rect(
            surface,
            Colors.GLASS_BG,
            (self.x, self.y, self.width, self.height),
            self.radius
        )
        
        # Border highlight
        draw_rounded_rect(
            surface,
            (255, 255, 255, 50),
            (self.x, self.y, self.width, 2),
            self.radius
        )
        
        # Icon
        icon_surface = font.render(self.icon, True, Colors.TEXT_SECONDARY)
        surface.blit(icon_surface, (self.x + 12, self.y + (self.height - icon_surface.get_height()) // 2))
        
        # Value
        value_surface = font.render(str(self.value), True, Colors.TEXT_PRIMARY)
        surface.blit(value_surface, (self.x + 45, self.y + (self.height - value_surface.get_height()) // 2))


class ModernButton:
    """A modern pill-style button"""
    
    def __init__(self, x, y, width, height, text, color=None, radius=20):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color or Colors.ACCENT_BLUE
        self.radius = radius
        self.hovered = False
        self.pressed = False
    
    def update(self, mouse_pos, mouse_pressed):
        """Update button state based on mouse"""
        self.hovered = self.rect.collidepoint(mouse_pos)
        self.pressed = self.hovered and mouse_pressed
        return self.hovered
    
    def draw(self, surface, font):
        """Draw the button"""
        x, y, w, h = self.rect
        
        # Determine color based on state
        if self.pressed:
            color = tuple(max(0, c - 30) for c in self.color)
        elif self.hovered:
            color = tuple(min(255, c + 20) for c in self.color)
        else:
            color = self.color
        
        # Shadow
        if not self.pressed:
            draw_shadow(surface, (x, y, w, h), self.radius, (2, 3), 2)
        
        # Button background
        pygame.draw.rect(surface, color, self.rect, 0, self.radius)
        
        # Highlight on top
        if not self.pressed:
            highlight = pygame.Surface((w, h // 3), pygame.SRCALPHA)
            pygame.draw.rect(highlight, (255, 255, 255, 40), (0, 0, w, h // 3), 0, self.radius)
            surface.blit(highlight, (x, y))
        
        # Text
        text_surface = font.render(self.text, True, Colors.TEXT_LIGHT)
        text_x = x + (w - text_surface.get_width()) // 2
        text_y = y + (h - text_surface.get_height()) // 2
        surface.blit(text_surface, (text_x, text_y))


# ============================================================================
# BACKGROUND SYSTEM
# ============================================================================

class PremiumBackground:
    """Manages the premium background with gradient and vignette"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.gradient = None
        self.vignette = None
        self.original_bg = None
        self._create_layers()
    
    def _create_layers(self):
        """Create background layers"""
        # Create sky gradient
        self.gradient = create_gradient_surface(
            self.width, 
            self.height,
            Colors.SKY_TOP,
            Colors.SKY_BOTTOM
        )
        
        # Create vignette
        self.vignette = create_vignette(self.width, self.height, intensity=60, radius_factor=0.6)
        
        print("[UI] Background layers created")
    
    def set_original_background(self, bg_surface):
        """Set the original background image (will be blended)"""
        self.original_bg = bg_surface
    
    def draw(self, surface, original_bg=None):
        """Draw the complete background"""
        # Draw gradient first
        surface.blit(self.gradient, (0, 0))
        
        # Blend original background if available
        bg = original_bg or self.original_bg
        if bg:
            # Create a semi-transparent version of the original
            bg_copy = bg.copy()
            bg_copy.set_alpha(180)  # Blend with gradient
            surface.blit(bg_copy, (-200, -100))
        
        # Draw vignette on top
        surface.blit(self.vignette, (0, 0))


# ============================================================================
# INITIALIZATION
# ============================================================================

def init_ui():
    """Initialize all UI systems - call after pygame.init()"""
    Fonts.init()
    print("[UI] UI Style system initialized")


# Export commonly used items
__all__ = [
    'Colors', 'Fonts', 
    'draw_rounded_rect', 'create_gradient_surface', 'create_vignette',
    'draw_shadow', 'draw_ball_shadow', 'draw_ball_premium',
    'GlassCard', 'HUDCard', 'ModernButton', 'PremiumBackground',
    'init_ui'
]
