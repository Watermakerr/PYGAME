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
    """Background with cached rendering for arbitrary world sizes"""
    def __init__(self, world_cols=None, world_rows=None):
        from config import NUM_TILES_WIDTH, NUM_TILES_HEIGHT
        self.image = pygame.transform.scale(pygame.image.load("images\\background.png"), (TILE_SIZE, TILE_SIZE))
        cols = world_cols or NUM_TILES_WIDTH
        rows = world_rows or NUM_TILES_HEIGHT
        self.world_width = cols * TILE_SIZE
        self.world_height = rows * TILE_SIZE
        # Render background once — tiles inside the wall border
        self.cached_bg = pygame.Surface((self.world_width, self.world_height))
        self.cached_bg.fill(COLORS['bg_dark'])
        for i in range(1, cols - 1):
            for j in range(1, rows - 1):
                self.cached_bg.blit(self.image, (i * TILE_SIZE, j * TILE_SIZE))
    
    def draw(self, offset=(0, 0)):
        DISPLAYSURF.blit(self.cached_bg, offset)


class Wall:
    """Tường viền game — draws along world boundaries"""
    def __init__(self, world_cols=None, world_rows=None):
        from config import NUM_TILES_WIDTH, NUM_TILES_HEIGHT
        self.image = pygame.transform.scale(pygame.image.load("images\\wall.png"), (TILE_SIZE, TILE_SIZE))
        self.cols = world_cols or NUM_TILES_WIDTH
        self.rows = world_rows or NUM_TILES_HEIGHT
    
    def draw(self, offset=(0, 0)):
        # Top and bottom walls
        for i in range(self.cols):
            DISPLAYSURF.blit(self.image, (i * TILE_SIZE + offset[0], offset[1]))
            DISPLAYSURF.blit(self.image, (i * TILE_SIZE + offset[0],
                                          (self.rows - 1) * TILE_SIZE + offset[1]))
        # Left and right walls
        for j in range(1, self.rows - 1):
            DISPLAYSURF.blit(self.image, (offset[0], j * TILE_SIZE + offset[1]))
            DISPLAYSURF.blit(self.image, ((self.cols - 1) * TILE_SIZE + offset[0],
                                          j * TILE_SIZE + offset[1]))


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
