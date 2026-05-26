# screens.py - Tất cả game screens (Menu, Gameplay, Game Over)
import pygame
import sys
import math
import random
from pygame.locals import *

from config import (DISPLAYSURF, WINDOWWIDTH, WINDOWHEIGHT, TILE_SIZE, 
                    COLORS, FPS, fpsClock)
from levels import LEVELS
from particles import particles
from collision import check_collision
from camera import Camera
from utils import screen_shake
from ui import Button, draw_hud
from entities import Bullet
from sounds import play_sound


# =============================================================================
# LEVEL SELECT SCREEN
# =============================================================================
def level_select():
    """Level selection screen"""
    font_big = pygame.font.SysFont("consolas", 48, bold=True)
    font_med = pygame.font.SysFont("consolas", 24)
    
    buttons = []
    for i, level in enumerate(LEVELS):
        x = 150 + (i % 2) * 350
        y = 200 + (i // 2) * 120
        btn = Button(x, y, text=f"Level {i + 1}", width=250, height=80)
        buttons.append(btn)
    
    back_btn = Button(350, 520, text="BACK", width=200, height=50)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        DISPLAYSURF.fill(COLORS['bg_dark'])
        
        title = font_big.render("SELECT LEVEL", True, COLORS['gold'])
        DISPLAYSURF.blit(title, (WINDOWWIDTH // 2 - title.get_width() // 2, 80))
        
        for i, btn in enumerate(buttons):
            btn.draw()
            if btn.is_click():
                return i
            
            name = font_med.render(LEVELS[i]['name'], True, (150, 150, 150))
            DISPLAYSURF.blit(name, (btn.rect.centerx - name.get_width() // 2, btn.rect.bottom + 5))
        
        back_btn.draw()
        if back_btn.is_click():
            return -1
        
        fpsClock.tick(FPS)
        pygame.display.update()


# =============================================================================
# MAIN MENU SCREEN
# =============================================================================
def gamestart(wall, background):
    """Main menu screen"""
    start_button = Button(350, 250, text="START GAME", width=200, height=60)
    level_button = Button(350, 330, text="SELECT LEVEL", width=200, height=60)
    exit_button = Button(350, 410, text="EXIT", width=200, height=60)
    
    font_big = pygame.font.SysFont("consolas", 56, bold=True)
    font_small = pygame.font.SysFont("consolas", 18)
    
    title_y = 100
    time_offset = 0
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        time_offset += 0.05
        
        DISPLAYSURF.fill(COLORS['bg_dark'])
        
        if random.random() < 0.1:
            particles.emit(random.randint(0, WINDOWWIDTH), random.randint(0, WINDOWHEIGHT), 
                          COLORS['particle_magic'], 1, 0.5, 60, 2)
        
        particles.update()
        particles.draw()
        
        title_text = "DUNGEON ESCAPE"
        glow_offset = math.sin(time_offset) * 3
        
        shadow = font_big.render(title_text, True, COLORS['text_shadow'])
        DISPLAYSURF.blit(shadow, (WINDOWWIDTH // 2 - shadow.get_width() // 2 + 4, title_y + 4 + glow_offset))
        
        title = font_big.render(title_text, True, COLORS['gold'])
        DISPLAYSURF.blit(title, (WINDOWWIDTH // 2 - title.get_width() // 2, title_y + glow_offset))
        
        subtitle = font_small.render(" V1", True, (150, 150, 180))
        DISPLAYSURF.blit(subtitle, (WINDOWWIDTH // 2 - subtitle.get_width() // 2, title_y + 65))
        
        start_button.draw()
        level_button.draw()
        exit_button.draw()
        
        hint = font_small.render("Arrow Keys/WASD: Move | SHIFT: Sprint | SPACE: Dash", True, (100, 100, 120))
        DISPLAYSURF.blit(hint, (WINDOWWIDTH // 2 - hint.get_width() // 2, WINDOWHEIGHT - 40))
        
        if start_button.is_click():
            pygame.time.wait(100)
            return 0
        elif level_button.is_click():
            pygame.time.wait(100)
            selected = level_select()
            if selected >= 0:
                return selected
        elif exit_button.is_click():
            pygame.quit()
            sys.exit()
        
        pygame.display.update()
        fpsClock.tick(FPS)


# =============================================================================
# GAMEPLAY SCREEN
# =============================================================================
def gameplay(background, wall, knight, door, obstacle_list, guard_list, bullets, keys,
             score, powerups, current_level, world_width=None, world_height=None):
    """Main gameplay loop with camera support."""
    score.__init__()
    count = 0
    move_left = False
    move_right = False
    move_top = False
    move_down = False
    sprint = False
    shoot_interval = LEVELS[current_level]['shoot_interval']
    start_time = pygame.time.get_ticks()
    key_count = len(keys)
    dying = False  # Death animation state
    last_shot_times = {id(guard): 0 for guard in guard_list}
    
    # World dimensions (default to viewport if not supplied)
    w_width = world_width or WINDOWWIDTH
    w_height = world_height or WINDOWHEIGHT
    
    # Camera setup
    camera = Camera(w_width, w_height)
    camera.snap_to(knight.x, knight.y)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key in (K_LEFT, K_a):
                    move_left = True
                if event.key in (K_RIGHT, K_d):
                    move_right = True
                if event.key in (K_UP, K_w):
                    move_top = True
                if event.key in (K_DOWN, K_s):
                    move_down = True
                if event.key in (K_LSHIFT, K_RSHIFT):
                    sprint = True
                if event.key == K_SPACE:
                    dx = (1 if move_right else 0) - (1 if move_left else 0)
                    dy = (1 if move_down else 0) - (1 if move_top else 0)
                    if dx != 0 or dy != 0:
                        length = math.hypot(dx, dy)
                        knight.dash((dx / length, dy / length))
            if event.type == KEYUP:
                if event.key in (K_LEFT, K_a):
                    move_left = False
                if event.key in (K_RIGHT, K_d):
                    move_right = False
                if event.key in (K_UP, K_w):
                    move_top = False
                if event.key in (K_DOWN, K_s):
                    move_down = False
                if event.key in (K_LSHIFT, K_RSHIFT):
                    sprint = False
        
        # Update camera to follow player
        camera.update(knight.x, knight.y)
        cam_offset = camera.get_offset()
        
        # Screen shake is layered on top of camera offset
        screen_shake.update()
        shake = screen_shake.get_offset()
        render_offset = (cam_offset[0] + shake[0], cam_offset[1] + shake[1])
        
        DISPLAYSURF.fill(COLORS['bg_dark'])
        
        background.draw(render_offset)
        wall.draw(render_offset)
        door.draw(render_offset)
        
        for key in keys:
            key.update()
            key.draw(render_offset)
        
        for powerup in powerups:
            powerup.update()
            powerup.draw(render_offset)
        
        for guard in guard_list:
            guard.draw(render_offset)
            guard.update(obstacle_list)
        
        for obstacle in obstacle_list:
            obstacle.draw(render_offset)
        
        # Shooting
        current_time = pygame.time.get_ticks()
        fired_bullet = False
        for guard in guard_list:
            guard_id = id(guard)
            if current_time - last_shot_times[guard_id] > shoot_interval:
                bullets.append(Bullet(guard, knight.x, knight.y))
                last_shot_times[guard_id] = current_time
                fired_bullet = True
        if fired_bullet:
            play_sound('bullet_fire')
        
        for bullet in bullets[:]:
            bullet.update()
            bullet.draw(render_offset)
        
        particles.update()
        particles.draw()
        
        knight.draw(render_offset)
        
        # If dying, update death animation and skip normal gameplay
        if dying:
            if knight.update_dying():
                return 'lose'
            draw_hud(knight, score, count, key_count, current_level)
            fpsClock.tick(FPS)
            pygame.display.update()
            continue
        
        knight.update(move_left, move_right, move_top, move_down, obstacle_list, sprint,
                      world_width=w_width, world_height=w_height)
        score.update(start_time)
        
        # Check door — collision-based instead of hardcoded coords
        if count == key_count:
            door.open()
            if check_collision(knight, door):
                particles.emit(knight.x + TILE_SIZE // 2, knight.y + TILE_SIZE // 2, 
                              COLORS['door_glow'], 15, 5, 40, 6)
                return 'win'
        
        # Key collection
        for key in keys[:]:
            if check_collision(knight, key):
                keys.remove(key)
                count += 1
                screen_shake.add_trauma(0.1)
                particles.emit(key.x + TILE_SIZE // 2, key.y + TILE_SIZE // 2, 
                              COLORS['gold'], 10, 3, 30, 4)
                play_sound('key_collect')
        
        # Power-up collection
        for powerup in powerups[:]:
            if not powerup.collected and check_collision(knight, powerup):
                powerup.collected = True
                powerups.remove(powerup)
                screen_shake.add_trauma(0.15)
                particles.emit(powerup.x + TILE_SIZE // 2, powerup.y + TILE_SIZE // 2, 
                              powerup.colors[powerup.power_type], 12, 4, 35, 5)
                play_sound('powerup_collect')
                
                if powerup.power_type == 'speed':
                    knight.speed_boost_time = 300
                    play_sound('speed_boost')
                elif powerup.power_type == 'shield':
                    knight.shield_time = 300
                    play_sound('shield_activate')
                elif powerup.power_type == 'slow_time':
                    for guard in guard_list:
                        guard.slow_timer = 300
                    play_sound('slow_time')
        
        # Bullet collision
        for bullet in bullets[:]:
            if knight.shield_time <= 0 and check_collision(knight, bullet):
                screen_shake.add_trauma(0.5)
                particles.emit(knight.x + TILE_SIZE // 2, knight.y + TILE_SIZE // 2, 
                              COLORS['health_red'], 15, 5, 40, 5)
                play_sound('player_hit')
                knight.start_dying()
                dying = True
                break
            
            # Bullet out-of-bounds uses WORLD bounds, not viewport
            if (bullet.x < TILE_SIZE or bullet.x > w_width - TILE_SIZE or
                bullet.y < TILE_SIZE or bullet.y > w_height - TILE_SIZE):
                bullets.remove(bullet)
                continue
            
            for obstacle in obstacle_list:
                if check_collision(bullet, obstacle):
                    bullets.remove(bullet)
                    particles.emit(bullet.x, bullet.y, COLORS['particle_fire'], 5, 2, 15, 3)
                    play_sound('bullet_hit')
                    break
        
        # Guard collision
        for guard in guard_list:
            if knight.shield_time <= 0 and check_collision(knight, guard):
                screen_shake.add_trauma(0.5)
                particles.emit(knight.x + TILE_SIZE // 2, knight.y + TILE_SIZE // 2, 
                              COLORS['health_red'], 15, 5, 40, 5)
                play_sound('player_hit')
                knight.start_dying()
                dying = True
                break
        
        # HUD is always drawn in screen-space (no camera offset)
        draw_hud(knight, score, count, key_count, current_level)
        
        fpsClock.tick(FPS)
        pygame.display.update()


# =============================================================================
# GAME OVER SCREEN
# =============================================================================
def gameover(result, score, current_level):
    """Game over screen - hiển thị kết quả và options.
    Supports SPACE key for quick retry.
    """
    if result == 'win':
        play_sound('level_complete')
    else:
        play_sound('game_over')
    
    button_back = Button(250, 400, text="MENU", width=180, height=50)
    replay_button = Button(470, 400, text="RETRY", width=180, height=50)
    next_level_button = Button(360, 480, text="NEXT LEVEL", width=180, height=50)
    
    font_big = pygame.font.SysFont("consolas", 60, bold=True)
    font_med = pygame.font.SysFont("consolas", 30)
    font_hint = pygame.font.SysFont("consolas", 20)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # SPACE to retry quickly
            if event.type == KEYDOWN and event.key == K_SPACE:
                if result == 'lose':
                    return 'retry'
                elif result == 'win' and current_level < len(LEVELS) - 1:
                    return 'next'
        
        DISPLAYSURF.fill(COLORS['bg_dark'])
        
        overlay = pygame.Surface((WINDOWWIDTH, WINDOWHEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        DISPLAYSURF.blit(overlay, (0, 0))
        
        if result == 'win':
            title_text = font_big.render("VICTORY!", True, COLORS['gold'])
            title_shadow = font_big.render("VICTORY!", True, COLORS['text_shadow'])
            DISPLAYSURF.blit(title_shadow, (WINDOWWIDTH // 2 - title_text.get_width() // 2 + 3, 153))
            DISPLAYSURF.blit(title_text, (WINDOWWIDTH // 2 - title_text.get_width() // 2, 150))
            
            level_text = font_med.render(f"Level {current_level + 1} Complete!", True, COLORS['white'])
            DISPLAYSURF.blit(level_text, (WINDOWWIDTH // 2 - level_text.get_width() // 2, 230))
            
            time_text = font_med.render(f"Time: {score.time}s", True, COLORS['stamina_blue'])
            DISPLAYSURF.blit(time_text, (WINDOWWIDTH // 2 - time_text.get_width() // 2, 280))
            
            if current_level < len(LEVELS) - 1:
                next_level_button.draw()
                if next_level_button.is_click():
                    return 'next'
                # Hint for SPACE
                hint = font_hint.render("Press SPACE for next level", True, (120, 120, 140))
                DISPLAYSURF.blit(hint, (WINDOWWIDTH // 2 - hint.get_width() // 2, 540))
            else:
                complete_text = font_med.render("All Levels Complete!", True, COLORS['gold'])
                DISPLAYSURF.blit(complete_text, (WINDOWWIDTH // 2 - complete_text.get_width() // 2, 330))
        else:
            title_text = font_big.render("DEFEATED", True, COLORS['health_red'])
            title_shadow = font_big.render("DEFEATED", True, COLORS['text_shadow'])
            DISPLAYSURF.blit(title_shadow, (WINDOWWIDTH // 2 - title_text.get_width() // 2 + 3, 153))
            DISPLAYSURF.blit(title_text, (WINDOWWIDTH // 2 - title_text.get_width() // 2, 150))
            
            hint_text = font_med.render("Use SPACE to dash through danger!", True, (180, 180, 180))
            DISPLAYSURF.blit(hint_text, (WINDOWWIDTH // 2 - hint_text.get_width() // 2, 280))
            
            # Hint for quick retry
            retry_hint = font_hint.render("Press SPACE to retry", True, (120, 200, 120))
            DISPLAYSURF.blit(retry_hint, (WINDOWWIDTH // 2 - retry_hint.get_width() // 2, 340))
        
        button_back.draw()
        replay_button.draw()
        
        if button_back.is_click():
            pygame.time.wait(100)
            return 'menu'
        elif replay_button.is_click():
            pygame.time.wait(100)
            return 'retry'
        
        fpsClock.tick(FPS)
        pygame.display.update()
