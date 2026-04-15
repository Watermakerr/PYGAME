# ui.py - UI components (Button, HUD)
import pygame
from config import DISPLAYSURF, WINDOWWIDTH, COLORS, key_image
from levels import LEVELS
from sounds import play_sound


# =============================================================================
# BUTTON - Interactive button component
# =============================================================================
class Button:
    """Interactive button với hover và click effects"""
    def __init__(self, x, y, image=None, scale=1, text="", width=200, height=60):
        if image:
            w = image.get_width()
            h = image.get_height()
            self.image = pygame.transform.scale(image, (int(w * scale), int(h * scale)))
            self.rect = self.image.get_rect()
        else:
            self.image = None
            self.rect = pygame.Rect(x, y, width, height)
        
        self.rect.topleft = (x, y)
        self.clicked = False
        self.was_clicked = False
        self.was_hovered = False
        self.hovered = False
        self.text = text
        self.font = pygame.font.SysFont("consolas", 24, bold=True)
    
    def draw(self):
        pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(pos)
        
        if self.hovered and not self.was_hovered:
            play_sound('button_hover')
        self.was_hovered = self.hovered
        
        if self.image:
            if self.hovered:
                hover_surf = pygame.Surface((self.rect.width + 10, self.rect.height + 10), pygame.SRCALPHA)
                hover_surf.fill((255, 255, 255, 30))
                DISPLAYSURF.blit(hover_surf, (self.rect.x - 5, self.rect.y - 5))
            DISPLAYSURF.blit(self.image, (self.rect.x, self.rect.y))
        else:
            color = COLORS['button_hover'] if self.hovered else COLORS['button_normal']
            if self.clicked:
                color = COLORS['button_pressed']
            
            # Shadow
            pygame.draw.rect(DISPLAYSURF, (20, 20, 30), 
                           (self.rect.x + 4, self.rect.y + 4, self.rect.width, self.rect.height), 
                           border_radius=10)
            # Main button
            pygame.draw.rect(DISPLAYSURF, color, self.rect, border_radius=10)
            # Border
            pygame.draw.rect(DISPLAYSURF, COLORS['gold_dark'], self.rect, 2, border_radius=10)
            
            # Text
            if self.text:
                text_surf = self.font.render(self.text, True, COLORS['white'])
                text_rect = text_surf.get_rect(center=self.rect.center)
                DISPLAYSURF.blit(text_surf, text_rect)
    
    def is_click(self):
        action = False
        pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0] == 1
        
        if self.rect.collidepoint(pos):
            if mouse_pressed and not self.was_clicked:
                self.clicked = True
            elif not mouse_pressed and self.clicked:
                action = True
                self.clicked = False
                play_sound('button_click')
        else:
            self.clicked = False
        
        if not mouse_pressed:
            self.clicked = False
        
        self.was_clicked = mouse_pressed
        return action


# =============================================================================
# HUD CACHE - Cached surfaces for performance
# =============================================================================
class HUDCache:
    """Cache cho các text surfaces không đổi để tránh render mỗi frame"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        self.font = pygame.font.SysFont("consolas", 20, bold=True)
        self.small_font = pygame.font.SysFont("consolas", 14)
        
        self.hud_bg = pygame.Surface((WINDOWWIDTH, 60), pygame.SRCALPHA)
        self.hud_bg.fill((20, 20, 35, 220))
        
        self.key_icon = pygame.transform.scale(key_image, (30, 30))
        
        self.controls_text = self.small_font.render(
            "Arrows/WASD: Move | SHIFT: Sprint | SPACE: Dash", True, (120, 120, 140))
        
        self.stamina_label = self.small_font.render("STAMINA", True, COLORS['white'])
        
        self.dash_bg = pygame.Surface((130, 22), pygame.SRCALPHA)
        self.dash_bg.fill((150, 100, 255, 100))
        
        self.dash_text = self.small_font.render("DASH READY [SPACE]", True, COLORS['white'])
        
        self.text_cache = {}
        self.level_text_cache = {}
    
    def get_text(self, text, color, font_type='normal'):
        key = (text, color, font_type)
        if key not in self.text_cache:
            font = self.font if font_type == 'normal' else self.small_font
            self.text_cache[key] = font.render(text, True, color)
            if len(self.text_cache) > 200:
                keys_to_remove = list(self.text_cache.keys())[:100]
                for k in keys_to_remove:
                    del self.text_cache[k]
        return self.text_cache[key]
    
    def get_level_text(self, level_index):
        if level_index not in self.level_text_cache:
            text = f"Level {level_index + 1}: {LEVELS[level_index]['name']}"
            self.level_text_cache[level_index] = self.font.render(text, True, COLORS['gold'])
        return self.level_text_cache[level_index]


# Global HUD cache instance
hud_cache = HUDCache()


# =============================================================================
# HUD DRAWING FUNCTION
# =============================================================================
def draw_hud(knight, score, key_count, total_keys, current_level):
    """Vẽ HUD với cached elements"""
    # Background panel
    DISPLAYSURF.blit(hud_cache.hud_bg, (0, 0))
    
    # Level indicator
    level_text = hud_cache.get_level_text(current_level)
    DISPLAYSURF.blit(level_text, (10, 5))
    
    # Key counter
    DISPLAYSURF.blit(hud_cache.key_icon, (10, 28))
    key_text = hud_cache.get_text(f"{key_count}/{total_keys}", COLORS['white'])
    DISPLAYSURF.blit(key_text, (45, 32))
    
    # Time
    time_text = hud_cache.get_text(f"Time: {score.time}s", COLORS['white'])
    DISPLAYSURF.blit(time_text, (WINDOWWIDTH - 150, 5))
    
    # Stamina bar
    stamina_width = 150
    stamina_height = 12
    stamina_x = WINDOWWIDTH - 160
    stamina_y = 35
    
    pygame.draw.rect(DISPLAYSURF, (40, 40, 50), (stamina_x, stamina_y, stamina_width, stamina_height), border_radius=5)
    fill_width = int((knight.stamina / knight.max_stamina) * stamina_width)
    pygame.draw.rect(DISPLAYSURF, COLORS['stamina_blue'], (stamina_x, stamina_y, fill_width, stamina_height), border_radius=5)
    pygame.draw.rect(DISPLAYSURF, COLORS['white'], (stamina_x, stamina_y, stamina_width, stamina_height), 1, border_radius=5)
    
    DISPLAYSURF.blit(hud_cache.stamina_label, (stamina_x + stamina_width // 2 - 30, stamina_y - 2))
    
    # Controls hint
    DISPLAYSURF.blit(hud_cache.controls_text, (120, 32))
    
    # Dash indicator
    if knight.dash_cooldown <= 0 and knight.stamina >= 30:
        DISPLAYSURF.blit(hud_cache.dash_bg, (WINDOWWIDTH // 2 - 65, 5))
        DISPLAYSURF.blit(hud_cache.dash_text, (WINDOWWIDTH // 2 - 60, 8))
