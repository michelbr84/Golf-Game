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
# ETAPA 2 - PARTICLE SYSTEM
# ============================================================================

class Particle:
    """Individual particle for effects"""
    
    def __init__(self, x, y, vx, vy, color, size, lifetime, gravity=0.1, fade=True):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.gravity = gravity
        self.fade = fade
        self.alive = True
    
    def update(self):
        """Update particle position and lifetime"""
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.lifetime -= 1
        
        if self.lifetime <= 0:
            self.alive = False
    
    def draw(self, surface):
        """Draw the particle"""
        if not self.alive:
            return
            
        # Calculate alpha based on lifetime
        if self.fade:
            alpha = int(255 * (self.lifetime / self.max_lifetime))
        else:
            alpha = 255
        
        # Create particle surface
        size = max(1, int(self.size * (self.lifetime / self.max_lifetime)))
        if size > 0:
            particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            color_with_alpha = (*self.color[:3], alpha)
            pygame.draw.circle(particle_surf, color_with_alpha, (size, size), size)
            surface.blit(particle_surf, (int(self.x) - size, int(self.y) - size))


class ParticleSystem:
    """Manages multiple particles for various effects"""
    
    def __init__(self, max_particles=200):
        self.particles = []
        self.max_particles = max_particles
    
    def emit_dust(self, x, y, count=5):
        """Emit dust particles (ball hitting ground)"""
        import random
        for _ in range(count):
            vx = random.uniform(-1.5, 1.5)
            vy = random.uniform(-2, -0.5)
            size = random.randint(2, 4)
            lifetime = random.randint(15, 30)
            color = (180, 160, 140)  # Dusty brown
            self._add_particle(x, y, vx, vy, color, size, lifetime, gravity=0.1)
    
    def emit_splash(self, x, y, count=10):
        """Emit water splash particles"""
        import random
        for _ in range(count):
            vx = random.uniform(-3, 3)
            vy = random.uniform(-5, -2)
            size = random.randint(3, 6)
            lifetime = random.randint(20, 40)
            color = (100, 180, 255)  # Water blue
            self._add_particle(x, y, vx, vy, color, size, lifetime, gravity=0.15)
    
    def emit_sparkle(self, x, y, count=8):
        """Emit coin sparkle particles"""
        import random
        for _ in range(count):
            angle = random.uniform(0, 6.28)
            speed = random.uniform(1, 3)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            size = random.randint(2, 4)
            lifetime = random.randint(15, 25)
            color = (255, 215, 0)  # Gold
            self._add_particle(x, y, vx, vy, color, size, lifetime, gravity=0)
    
    def emit_hit(self, x, y, count=3):
        """Emit hit particles (ball collision)"""
        import random
        for _ in range(count):
            vx = random.uniform(-1, 1)
            vy = random.uniform(-1.5, -0.5)
            size = random.randint(1, 3)
            lifetime = random.randint(10, 20)
            color = (255, 255, 255)
            self._add_particle(x, y, vx, vy, color, size, lifetime, gravity=0.05)
    
    def _add_particle(self, x, y, vx, vy, color, size, lifetime, gravity):
        """Add a particle to the system"""
        if len(self.particles) < self.max_particles:
            self.particles.append(Particle(x, y, vx, vy, color, size, lifetime, gravity))
    
    def update(self):
        """Update all particles"""
        for particle in self.particles:
            particle.update()
        # Remove dead particles
        self.particles = [p for p in self.particles if p.alive]
    
    def draw(self, surface):
        """Draw all particles"""
        for particle in self.particles:
            particle.draw(surface)
    
    def clear(self):
        """Clear all particles"""
        self.particles = []


# ============================================================================
# ETAPA 2 - BALL TRAIL EFFECT
# ============================================================================

class BallTrail:
    """Creates a trail effect behind the ball"""
    
    def __init__(self, max_length=12):
        self.positions = []
        self.max_length = max_length
    
    def add_position(self, x, y):
        """Add a new position to the trail"""
        self.positions.append((x, y))
        if len(self.positions) > self.max_length:
            self.positions.pop(0)
    
    def draw(self, surface, color):
        """Draw the trail with fading effect"""
        if len(self.positions) < 2:
            return
        
        for i, pos in enumerate(self.positions):
            # Calculate alpha and size based on position in trail
            alpha = int(120 * (i / len(self.positions)))
            size = max(1, int(3 * (i / len(self.positions))))
            
            trail_surf = pygame.Surface((size * 2 + 2, size * 2 + 2), pygame.SRCALPHA)
            trail_color = (*color[:3], alpha)
            pygame.draw.circle(trail_surf, trail_color, (size + 1, size + 1), size)
            surface.blit(trail_surf, (int(pos[0]) - size - 1, int(pos[1]) - size - 1))
    
    def clear(self):
        """Clear the trail"""
        self.positions = []


# ============================================================================
# ETAPA 2 - PARALLAX BACKGROUND
# ============================================================================

class ParallaxLayer:
    """Single layer of a parallax background"""
    
    def __init__(self, width, y_offset, color, cloud_count=5, speed_factor=0.3):
        self.width = width
        self.y_offset = y_offset
        self.color = color
        self.speed_factor = speed_factor
        self.offset_x = 0
        self.clouds = self._generate_clouds(cloud_count)
    
    def _generate_clouds(self, count):
        """Generate cloud positions"""
        import random
        clouds = []
        for i in range(count):
            x = random.randint(0, self.width)
            w = random.randint(60, 150)
            h = random.randint(20, 40)
            clouds.append({'x': x, 'y': self.y_offset + random.randint(-20, 20), 
                          'w': w, 'h': h, 'alpha': random.randint(20, 50)})
        return clouds
    
    def update(self, camera_offset=0):
        """Update layer position based on camera"""
        self.offset_x = -camera_offset * self.speed_factor
    
    def draw(self, surface):
        """Draw the layer"""
        for cloud in self.clouds:
            x = (cloud['x'] + self.offset_x) % self.width
            
            cloud_surf = pygame.Surface((cloud['w'], cloud['h']), pygame.SRCALPHA)
            cloud_color = (*self.color, cloud['alpha'])
            pygame.draw.ellipse(cloud_surf, cloud_color, (0, 0, cloud['w'], cloud['h']))
            surface.blit(cloud_surf, (x, cloud['y']))


class ParallaxBackground:
    """Multi-layer parallax background system"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # Create 3 layers: far clouds, mid clouds, near details
        self.layers = [
            ParallaxLayer(width, 50, (255, 255, 255), cloud_count=4, speed_factor=0.1),
            ParallaxLayer(width, 100, (230, 240, 250), cloud_count=5, speed_factor=0.2),
            ParallaxLayer(width, 150, (200, 220, 240), cloud_count=3, speed_factor=0.35),
        ]
        
        # Floating animation for clouds
        self.time = 0
    
    def update(self, camera_offset=0):
        """Update parallax layers"""
        self.time += 0.02
        for layer in self.layers:
            layer.update(camera_offset)
    
    def draw(self, surface):
        """Draw all parallax layers"""
        for layer in self.layers:
            layer.draw(surface)


# ============================================================================
# ETAPA 3 - SCREEN TRANSITIONS
# ============================================================================

class ScreenTransition:
    """Handles fade in/out transitions between screens"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.alpha = 0
        self.target_alpha = 0
        self.speed = 10
        self.active = False
        self.callback = None
    
    def fade_in(self, speed=10, callback=None):
        """Start fade from black to transparent"""
        self.alpha = 255
        self.target_alpha = 0
        self.speed = speed
        self.active = True
        self.callback = callback
    
    def fade_out(self, speed=10, callback=None):
        """Start fade from transparent to black"""
        self.alpha = 0
        self.target_alpha = 255
        self.speed = speed
        self.active = True
        self.callback = callback
    
    def update(self):
        """Update transition state"""
        if not self.active:
            return False
        
        if self.alpha < self.target_alpha:
            self.alpha = min(self.alpha + self.speed, self.target_alpha)
        elif self.alpha > self.target_alpha:
            self.alpha = max(self.alpha - self.speed, self.target_alpha)
        
        if self.alpha == self.target_alpha:
            self.active = False
            if self.callback:
                self.callback()
            return True  # Transition complete
        return False
    
    def draw(self, surface):
        """Draw the transition overlay"""
        if self.alpha > 0:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, self.alpha))
            surface.blit(overlay, (0, 0))
    
    def is_active(self):
        return self.active


# ============================================================================
# ETAPA 3 - CAMERA SHAKE
# ============================================================================

class CameraShake:
    """Creates screen shake effect for impacts"""
    
    def __init__(self):
        self.offset_x = 0
        self.offset_y = 0
        self.intensity = 0
        self.duration = 0
        self.decay = 0.9
    
    def shake(self, intensity=5, duration=10):
        """Start a shake effect"""
        self.intensity = intensity
        self.duration = duration
    
    def update(self):
        """Update shake effect"""
        import random
        if self.duration > 0:
            self.offset_x = random.randint(-int(self.intensity), int(self.intensity))
            self.offset_y = random.randint(-int(self.intensity), int(self.intensity))
            self.intensity *= self.decay
            self.duration -= 1
        else:
            self.offset_x = 0
            self.offset_y = 0
            self.intensity = 0
    
    def get_offset(self):
        """Get current shake offset for rendering"""
        return (self.offset_x, self.offset_y)


# ============================================================================
# ETAPA 3 - SCREEN FLASH
# ============================================================================

class ScreenFlash:
    """Creates a brief flash effect for feedback"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.alpha = 0
        self.color = (255, 255, 255)
        self.decay = 25
    
    def flash(self, color=(255, 255, 255), intensity=80):
        """Trigger a flash"""
        self.color = color
        self.alpha = intensity
    
    def update(self):
        """Update flash effect"""
        if self.alpha > 0:
            self.alpha = max(0, self.alpha - self.decay)
    
    def draw(self, surface):
        """Draw the flash overlay"""
        if self.alpha > 0:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((*self.color, self.alpha))
            surface.blit(overlay, (0, 0))


# ============================================================================
# ETAPA 3 - ANIMATED VALUE
# ============================================================================

class AnimatedValue:
    """Smoothly animates between values (for UI elements)"""
    
    def __init__(self, initial_value=0, speed=0.1):
        self.current = initial_value
        self.target = initial_value
        self.speed = speed
    
    def set_target(self, value):
        """Set the target value to animate to"""
        self.target = value
    
    def update(self):
        """Update the current value towards target"""
        diff = self.target - self.current
        self.current += diff * self.speed
        
        # Snap to target if close enough
        if abs(diff) < 0.01:
            self.current = self.target
    
    def get(self):
        """Get current animated value"""
        return self.current
    
    def is_animating(self):
        """Check if still animating"""
        return abs(self.target - self.current) > 0.01


# ============================================================================
# ETAPA 3 - FLAG ANIMATION
# ============================================================================

class FlagAnimation:
    """Animates flag with wind effect"""
    
    def __init__(self):
        self.time = 0
        self.wave_speed = 0.15
        self.wave_amount = 3
    
    def update(self):
        """Update animation timer"""
        self.time += self.wave_speed
    
    def get_offset(self):
        """Get current wave offset for flag rendering"""
        offset = math.sin(self.time) * self.wave_amount
        return offset


# ============================================================================
# ETAPA 3 - CONFETTI EFFECT
# ============================================================================

class ConfettiSystem:
    """Creates confetti particles for celebrations"""
    
    def __init__(self, max_particles=100):
        self.particles = []
        self.max_particles = max_particles
        self.colors = [
            (255, 100, 100),  # Red
            (100, 255, 100),  # Green
            (100, 100, 255),  # Blue
            (255, 255, 100),  # Yellow
            (255, 100, 255),  # Pink
            (100, 255, 255),  # Cyan
        ]
    
    def emit(self, x, y, count=30):
        """Emit confetti from a position"""
        import random
        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                break
            
            vx = random.uniform(-4, 4)
            vy = random.uniform(-8, -3)
            color = random.choice(self.colors)
            size = random.randint(4, 8)
            rotation = random.uniform(0, 6.28)
            rot_speed = random.uniform(-0.2, 0.2)
            
            self.particles.append({
                'x': x, 'y': y,
                'vx': vx, 'vy': vy,
                'color': color,
                'size': size,
                'rotation': rotation,
                'rot_speed': rot_speed,
                'lifetime': random.randint(60, 120)
            })
    
    def update(self):
        """Update all confetti particles"""
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.12  # Gravity
            p['vx'] *= 0.99  # Air resistance
            p['rotation'] += p['rot_speed']
            p['lifetime'] -= 1
        
        # Remove dead particles
        self.particles = [p for p in self.particles if p['lifetime'] > 0]
    
    def draw(self, surface):
        """Draw confetti"""
        for p in self.particles:
            alpha = min(255, p['lifetime'] * 4)
            s = p['size']
            
            # Create rotated rectangle
            confetti_surf = pygame.Surface((s * 2, s), pygame.SRCALPHA)
            pygame.draw.rect(confetti_surf, (*p['color'], alpha), (0, 0, s * 2, s))
            
            # Rotate
            rotated = pygame.transform.rotate(confetti_surf, math.degrees(p['rotation']))
            rect = rotated.get_rect(center=(int(p['x']), int(p['y'])))
            surface.blit(rotated, rect)
    
    def clear(self):
        """Clear all particles"""
        self.particles = []


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
    'Particle', 'ParticleSystem', 'BallTrail', 'ParallaxLayer', 'ParallaxBackground',
    'ScreenTransition', 'CameraShake', 'ScreenFlash', 'AnimatedValue', 
    'FlagAnimation', 'ConfettiSystem',
    'init_ui'
]


