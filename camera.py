# camera.py - Smooth follow camera system
import pygame
from config import WINDOWWIDTH, WINDOWHEIGHT


class Camera:
    """Smooth follow camera that keeps the player roughly centered."""
    def __init__(self, world_width, world_height):
        self.world_width = world_width
        self.world_height = world_height
        self.x = 0.0
        self.y = 0.0
        self.target_x = 0.0
        self.target_y = 0.0
        self.viewport_width = WINDOWWIDTH
        self.viewport_height = WINDOWHEIGHT
        self.lerp_speed = 0.08  # Smooth follow speed
    
    def update(self, player_x, player_y):
        """Update camera to smoothly follow the player, keeping them centered."""
        # Target: center player on screen
        self.target_x = player_x - self.viewport_width // 2
        self.target_y = player_y - self.viewport_height // 2
        
        # Clamp to world bounds (don't show outside the map)
        max_x = max(0, self.world_width - self.viewport_width)
        max_y = max(0, self.world_height - self.viewport_height)
        self.target_x = max(0, min(self.target_x, max_x))
        self.target_y = max(0, min(self.target_y, max_y))
        
        # Smooth lerp
        self.x += (self.target_x - self.x) * self.lerp_speed
        self.y += (self.target_y - self.y) * self.lerp_speed
    
    def get_offset(self):
        """Get render offset (negative camera position)."""
        return (-int(self.x), -int(self.y))
    
    def get_visible_rect(self):
        """Get the world-space rect currently visible on screen."""
        return pygame.Rect(int(self.x), int(self.y), self.viewport_width, self.viewport_height)
    
    def snap_to(self, player_x, player_y):
        """Instantly center camera on player (no lerp)."""
        self.x = player_x - self.viewport_width // 2
        self.y = player_y - self.viewport_height // 2
        # Clamp
        max_x = max(0, self.world_width - self.viewport_width)
        max_y = max(0, self.world_height - self.viewport_height)
        self.x = max(0, min(self.x, max_x))
        self.y = max(0, min(self.y, max_y))
        self.target_x = self.x
        self.target_y = self.y
