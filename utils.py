# utils.py - Utility classes (ScreenShake, Background, Wall, Score)
import pygame
import random
from config import (DISPLAYSURF, WINDOWWIDTH, WINDOWHEIGHT, TILE_SIZE, 
                    NUM_TILES_WIDTH, NUM_TILES_HEIGHT, COLORS)


class ScreenShake:
    """Hiệu ứng rung màn hình"""
    def __init__(self):
        self.offset_x = 0
        self.offset_y = 0
        self.trauma = 0
    
    def add_trauma(self, amount):
        self.trauma = min(1.0, self.trauma + amount)
    
    def update(self):
        if self.trauma > 0:
            shake = self.trauma ** 2
            self.offset_x = random.uniform(-10, 10) * shake
            self.offset_y = random.uniform(-10, 10) * shake
            self.trauma = max(0, self.trauma - 0.05)
        else:
            self.offset_x = 0
            self.offset_y = 0
    
    def get_offset(self):
        return (int(self.offset_x), int(self.offset_y))


class Background:
    """Background với cached rendering"""
    def __init__(self):
        self.image = pygame.transform.scale(pygame.image.load("images\\background.png"), (TILE_SIZE, TILE_SIZE))
        # Render background 1 lần duy nhất khi khởi tạo - không cần re-render
        self.cached_bg = pygame.Surface((WINDOWWIDTH, WINDOWHEIGHT))
        self.cached_bg.fill(COLORS['bg_dark'])  # Fill background color trước
        for i in range(1, NUM_TILES_WIDTH - 1):
            for j in range(1, NUM_TILES_HEIGHT - 1):
                x = i * TILE_SIZE
                y = j * TILE_SIZE
                self.cached_bg.blit(self.image, (x, y))
    
    def draw(self, offset=(0, 0)):
        # Chỉ 1 blit thay vì 234 blits!
        DISPLAYSURF.blit(self.cached_bg, offset)


class Wall:
    """Tường viền game"""
    def __init__(self):
        self.image = pygame.transform.scale(pygame.image.load("images\\wall.png"), (TILE_SIZE, TILE_SIZE))
    
    def draw(self, offset=(0, 0)):
        # Draw top and bottom walls
        for i in range(NUM_TILES_WIDTH):
            x_top = i * TILE_SIZE + offset[0]
            y_top = offset[1]
            DISPLAYSURF.blit(self.image, (x_top, y_top))
            
            x_bot = i * TILE_SIZE + offset[0]
            y_bot = WINDOWHEIGHT - TILE_SIZE + offset[1]
            DISPLAYSURF.blit(self.image, (x_bot, y_bot))
        
        # Draw left and right walls
        for i in range(1, NUM_TILES_HEIGHT - 1):
            x_left = offset[0]
            y_left = i * TILE_SIZE + offset[1]
            DISPLAYSURF.blit(self.image, (x_left, y_left))
            
            x_right = WINDOWWIDTH - TILE_SIZE + offset[0]
            y_right = i * TILE_SIZE + offset[1]
            DISPLAYSURF.blit(self.image, (x_right, y_right))


class Score:
    """Quản lý điểm số và thời gian"""
    def __init__(self):
        self.time = 0
        self.keys_collected = 0
        self.level = 1
    
    def update(self, start_time):
        time = pygame.time.get_ticks() - start_time
        self.time = round(time / 1000, 2)


# Global instances
screen_shake = ScreenShake()
