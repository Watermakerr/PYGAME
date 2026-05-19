# config.py - Constants và settings cho game
import pygame

pygame.init()

# Window settings
WINDOWWIDTH = 900
WINDOWHEIGHT = 650
DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

# Tile settings
TILE_SIZE = 50
NUM_TILES_WIDTH = WINDOWWIDTH // TILE_SIZE
NUM_TILES_HEIGHT = WINDOWHEIGHT // TILE_SIZE

# Room dimensions (each room = one viewport)
ROOM_COLS = NUM_TILES_WIDTH    # 18 tiles
ROOM_ROWS = NUM_TILES_HEIGHT   # 13 tiles
ROOM_WIDTH = ROOM_COLS * TILE_SIZE   # 900 px
ROOM_HEIGHT = ROOM_ROWS * TILE_SIZE  # 650 px

# Game settings
FPS = 60
fpsClock = pygame.time.Clock()

# Color Palette (Dark Fantasy Theme)
COLORS = {
    'bg_dark': (25, 25, 35),
    'bg_medium': (40, 40, 55),
    'wall_dark': (60, 50, 70),
    'wall_light': (80, 70, 95),
    'gold': (255, 215, 0),
    'gold_dark': (180, 150, 0),
    'health_green': (50, 205, 50),
    'health_red': (220, 50, 50),
    'stamina_blue': (65, 105, 225),
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'text_shadow': (20, 20, 30),
    'particle_fire': (255, 100, 50),
    'particle_magic': (150, 100, 255),
    'door_glow': (100, 255, 150),
    'warning': (255, 100, 100),
    'ui_bg': (30, 30, 45, 200),
    'button_normal': (70, 60, 90),
    'button_hover': (100, 85, 130),
    'button_pressed': (50, 40, 65),
}

# Load images
icon = pygame.image.load("images\\guard.png")
pygame.display.set_icon(icon)
pygame.display.set_caption("Dungeon Escape - Enhanced Edition")

key_image = pygame.transform.scale(pygame.image.load("images\\key.png"), (TILE_SIZE, TILE_SIZE))
start_button_image = pygame.image.load("images\\start_button.png")
exit_button_image = pygame.image.load("images\\exit_button.png")
back_button_image = pygame.image.load("images\\back_button.png")
replay_button_image = pygame.image.load("images\\replay_button.png")
