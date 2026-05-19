# entities.py - Tất cả game entities (Knight, Guard, Bullet, Obstacle, Key, Door, PowerUp)
import pygame
import math
import os
from config import DISPLAYSURF, TILE_SIZE, WINDOWWIDTH, WINDOWHEIGHT, COLORS
from collision import check_collision_with_grid
from particles import particles
from utils import screen_shake
from sounds import play_sound

# Sprite display size (larger than hitbox for visual appeal)
SPRITE_SIZE = TILE_SIZE * 2
SPRITE_OFFSET = (SPRITE_SIZE - TILE_SIZE) // 2  # center sprite over hitbox


# =============================================================================
# Helper: Load animation frames from a folder
# =============================================================================
def load_animation_frames(folder_path, size=(TILE_SIZE, TILE_SIZE)):
    """Load all PNG frames from a folder, sorted by name, scaled to size."""
    import os
    frames = []
    for filename in sorted(os.listdir(folder_path)):
        if filename.endswith('.png'):
            img = pygame.image.load(os.path.join(folder_path, filename)).convert_alpha()
            img = pygame.transform.scale(img, size)
            frames.append(img)
    return frames


# =============================================================================
# KNIGHT - Player character
# =============================================================================
class Knight:
    """Player character với dash và stamina system"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.base_speed = 5
        self.move_speed = self.base_speed
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        
        # Sprite animations (Wraith_01)
        sprite_base = os.path.join("images", "Wraith_01", "PNG Sequences")
        self.frames_idle = load_animation_frames(os.path.join(sprite_base, "Idle"), (SPRITE_SIZE, SPRITE_SIZE))
        self.frames_walk = load_animation_frames(os.path.join(sprite_base, "Walking"), (SPRITE_SIZE, SPRITE_SIZE))
        self.frames_dying = load_animation_frames(os.path.join(sprite_base, "Dying"), (SPRITE_SIZE, SPRITE_SIZE))
        self.current_frames = self.frames_idle
        self.frame_index = 0
        self.anim_speed = 0.15
        self.image = self.frames_idle[0]
        
        # Death animation state
        self.is_dying = False
        self.death_timer = 0
        self.death_duration = len(self.frames_dying)  # frames to play
        
        # Stamina system
        self.stamina = 100
        self.max_stamina = 100
        self.stamina_regen = 0.5
        
        # Dash ability
        self.dash_speed = 20
        self.dash_cooldown = 0
        self.dash_duration = 0
        self.dash_direction = (0, 0)
        self.is_dashing = False
        
        # Sprint
        self.is_sprinting = False
        self.sprint_speed = 8
        
        # Power-up effects
        self.shield_time = 0
        self.speed_boost_time = 0
        
        # Animation
        self.trail_timer = 0
        self.facing_right = True
        self.is_moving = False
    
    def dash(self, direction):
        if self.dash_cooldown <= 0 and self.stamina >= 30 and not self.is_dashing:
            self.is_dashing = True
            self.dash_duration = 8
            self.dash_direction = direction
            self.stamina -= 30
            self.dash_cooldown = 45
            screen_shake.add_trauma(0.2)
            particles.emit(self.x + TILE_SIZE // 2, self.y + TILE_SIZE // 2, 
                          COLORS['particle_magic'], 8, 4, 20, 5)
            play_sound('dash')
    
    def update(self, move_left, move_right, move_top, move_down, obstacles, sprint=False,
               world_width=None, world_height=None):
        # Handle dash
        if self.is_dashing and self.dash_duration > 0:
            self.dash_duration -= 1
            dx, dy = self.dash_direction
            new_x = self.x + dx * self.dash_speed
            new_y = self.y + dy * self.dash_speed
            
            test_rect_x = pygame.Rect(new_x, self.y, TILE_SIZE, TILE_SIZE)
            if not check_collision_with_grid(test_rect_x):
                self.x = new_x
            test_rect_y = pygame.Rect(self.x, new_y, TILE_SIZE, TILE_SIZE)
            if not check_collision_with_grid(test_rect_y):
                self.y = new_y
            
            particles.emit_trail(self.x + TILE_SIZE // 2, self.y + TILE_SIZE // 2, 
                               COLORS['particle_magic'], self.dash_direction)
        else:
            self.is_dashing = False
            self.is_sprinting = sprint and self.stamina > 0
            if self.is_sprinting:
                self.move_speed = self.sprint_speed
                self.stamina -= 0.8
            else:
                self.move_speed = self.base_speed
        
        # Speed boost from power-up
        if self.speed_boost_time > 0:
            self.move_speed *= 1.5
            self.speed_boost_time -= 1
        
        # Stamina regeneration
        if not self.is_sprinting and not self.is_dashing:
            self.stamina = min(self.max_stamina, self.stamina + self.stamina_regen)
        
        # Cooldowns
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1
        if self.shield_time > 0:
            self.shield_time -= 1
        
        # Normal movement
        if not self.is_dashing:
            hitbox_shrink = 5
            if move_left:
                new_x = self.x - self.move_speed
                test_rect = pygame.Rect(new_x, self.y, TILE_SIZE, TILE_SIZE)
                if not check_collision_with_grid(test_rect, hitbox_shrink):
                    self.x = new_x
                self.facing_right = False
            if move_right:
                new_x = self.x + self.move_speed
                test_rect = pygame.Rect(new_x, self.y, TILE_SIZE, TILE_SIZE)
                if not check_collision_with_grid(test_rect, hitbox_shrink):
                    self.x = new_x
                self.facing_right = True
            if move_top:
                new_y = self.y - self.move_speed
                test_rect = pygame.Rect(self.x, new_y, TILE_SIZE, TILE_SIZE)
                if not check_collision_with_grid(test_rect, hitbox_shrink):
                    self.y = new_y
            if move_down:
                new_y = self.y + self.move_speed
                test_rect = pygame.Rect(self.x, new_y, TILE_SIZE, TILE_SIZE)
                if not check_collision_with_grid(test_rect, hitbox_shrink):
                    self.y = new_y
        
        # Boundary check (clamp to world bounds, not viewport)
        w_bound = (world_width or WINDOWWIDTH) - 2 * TILE_SIZE
        h_bound = (world_height or WINDOWHEIGHT) - 2 * TILE_SIZE
        self.x = max(TILE_SIZE, min(w_bound, self.x))
        self.y = max(TILE_SIZE, min(h_bound, self.y))
        
        # Track movement for animation
        self.is_moving = move_left or move_right or move_top or move_down
        
        # Update animation frames
        if self.is_dying:
            self.current_frames = self.frames_dying
            self.anim_speed = 0.12
        elif self.is_moving or self.is_dashing:
            self.current_frames = self.frames_walk
            self.anim_speed = 0.2
        else:
            self.current_frames = self.frames_idle
            self.anim_speed = 0.1
        
        self.frame_index += self.anim_speed
        if self.is_dying:
            if self.frame_index >= len(self.current_frames):
                self.frame_index = len(self.current_frames) - 1
        else:
            if self.frame_index >= len(self.current_frames):
                self.frame_index = 0
        self.image = self.current_frames[int(self.frame_index)]
        
        # Movement particles
        self.trail_timer += 1
        if (move_left or move_right or move_top or move_down) and self.trail_timer % 8 == 0:
            particles.emit(self.x + TILE_SIZE // 2, self.y + TILE_SIZE, 
                          (150, 150, 150), 1, 1, 15, 2, 0.1)
    
    def start_dying(self):
        """Start the death animation"""
        self.is_dying = True
        self.frame_index = 0
        self.death_timer = 0
        self.current_frames = self.frames_dying
        # 15 frames in 0.5s at 60 FPS = 30 ticks -> anim_speed = 15/30 = 0.5
        self.anim_speed = len(self.frames_dying) / 50.0
    
    def update_dying(self):
        """Update death animation, returns True when animation is complete"""
        if not self.is_dying:
            return False
        self.frame_index += self.anim_speed
        if self.frame_index >= len(self.frames_dying):
            self.frame_index = len(self.frames_dying) - 1
            return True
        self.image = self.current_frames[int(self.frame_index)]
        return False
    
    def draw(self, offset=(0, 0)):
        draw_x = self.x + offset[0]
        draw_y = self.y + offset[1]
        
        # Draw shield effect
        if self.shield_time > 0:
            shield_surf = pygame.Surface((TILE_SIZE + 20, TILE_SIZE + 20), pygame.SRCALPHA)
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.01)) * 50 + 100
            pygame.draw.circle(shield_surf, (100, 200, 255, int(pulse)), 
                             (TILE_SIZE // 2 + 10, TILE_SIZE // 2 + 10), TILE_SIZE // 2 + 10, 3)
            DISPLAYSURF.blit(shield_surf, (draw_x - 10, draw_y - 10))
        
        # Draw speed boost effect
        if self.speed_boost_time > 0 and self.speed_boost_time % 3 == 0:
            particles.emit(self.x + TILE_SIZE // 2, self.y + TILE_SIZE // 2, 
                          COLORS['gold'], 1, 2, 10, 3)
        
        # Draw knight (animated sprite) - centered over hitbox
        img = self.image if self.facing_right else pygame.transform.flip(self.image, True, False)
        DISPLAYSURF.blit(img, (draw_x - SPRITE_OFFSET, draw_y - SPRITE_OFFSET))
        
        # Dash ready indicator
        if not self.is_dying and self.dash_cooldown <= 0 and self.stamina >= 30:
            pygame.draw.circle(DISPLAYSURF, COLORS['particle_magic'], 
                             (int(draw_x + TILE_SIZE // 2), int(draw_y - 5)), 4)


# =============================================================================
# GUARD - Enemy character
# =============================================================================
class Guard:
    """Enemy guard với các types khác nhau"""
    def __init__(self, x, y, knight, guard_type='normal', speed=3):
        self.x = x
        self.y = y
        self.base_speed = speed
        self.speed = speed
        self.knight = knight
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.guard_type = guard_type
        
        # Sprite animations (Wraith_02)
        sprite_base = os.path.join("images", "Wraith_02", "PNG Sequences")
        self.frames_idle = load_animation_frames(os.path.join(sprite_base, "Idle"), (SPRITE_SIZE, SPRITE_SIZE))
        self.frames_walk = load_animation_frames(os.path.join(sprite_base, "Walking"), (SPRITE_SIZE, SPRITE_SIZE))
        self.current_frames = self.frames_idle
        self.frame_index = 0
        self.anim_speed = 0.15
        self.image = self.frames_idle[0]
        self.facing_right = True
        self.was_moving = False
        
        if guard_type == 'fast':
            self.speed = speed * 1.5
            self.color_tint = (255, 200, 100)
        elif guard_type == 'heavy':
            self.speed = speed * 0.7
            self.color_tint = (150, 100, 100)
        else:
            self.color_tint = None
        
        self.slowed = False
        self.slow_timer = 0
    
    def update(self, obstacles):
        if self.slow_timer > 0:
            self.slow_timer -= 1
            current_speed = self.speed * 0.3
        else:
            self.slowed = False
            current_speed = self.speed
        
        if self.knight.x > self.x:
            new_x = self.x + current_speed
            test_rect = pygame.Rect(new_x, self.y, TILE_SIZE, TILE_SIZE)
            if not check_collision_with_grid(test_rect):
                self.x = new_x
        
        if self.knight.x < self.x:
            new_x = self.x - current_speed
            test_rect = pygame.Rect(new_x, self.y, TILE_SIZE, TILE_SIZE)
            if not check_collision_with_grid(test_rect):
                self.x = new_x
        
        if self.knight.y < self.y:
            new_y = self.y - current_speed
            test_rect = pygame.Rect(self.x, new_y, TILE_SIZE, TILE_SIZE)
            if not check_collision_with_grid(test_rect):
                self.y = new_y
        
        if self.knight.y > self.y:
            new_y = self.y + current_speed
            test_rect = pygame.Rect(self.x, new_y, TILE_SIZE, TILE_SIZE)
            if not check_collision_with_grid(test_rect):
                self.y = new_y
        
        # Update facing direction
        if self.knight.x > self.x:
            self.facing_right = True
        elif self.knight.x < self.x:
            self.facing_right = False
        
        # Update animation
        is_moving = abs(self.knight.x - self.x) > 2 or abs(self.knight.y - self.y) > 2
        if is_moving:
            self.current_frames = self.frames_walk
            self.anim_speed = 0.18
        else:
            self.current_frames = self.frames_idle
            self.anim_speed = 0.1
        
        self.frame_index += self.anim_speed
        if self.frame_index >= len(self.current_frames):
            self.frame_index = 0
        self.image = self.current_frames[int(self.frame_index)]
    
    def draw(self, offset=(0, 0)):
        draw_x = self.x + offset[0]
        draw_y = self.y + offset[1]
        
        dist = math.hypot(self.knight.x - self.x, self.knight.y - self.y)
        if dist < 150:
            warning_alpha = int((1 - dist / 150) * 100)
            warning_surf = pygame.Surface((TILE_SIZE + 10, TILE_SIZE + 10), pygame.SRCALPHA)
            pygame.draw.circle(warning_surf, (*COLORS['warning'][:3], warning_alpha), 
                              (TILE_SIZE // 2 + 5, TILE_SIZE // 2 + 5), TILE_SIZE // 2 + 5, 2)
            DISPLAYSURF.blit(warning_surf, (draw_x - 5, draw_y - 5))
        
        if self.slow_timer > 0:
            slow_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            slow_surf.fill((100, 100, 255, 80))
            DISPLAYSURF.blit(slow_surf, (draw_x, draw_y))
        
        img = self.image if self.facing_right else pygame.transform.flip(self.image, True, False)
        DISPLAYSURF.blit(img, (draw_x - SPRITE_OFFSET, draw_y - SPRITE_OFFSET))


# =============================================================================
# BULLET - Projectile from guards
# =============================================================================
class Bullet:
    """Đạn bắn từ guard"""
    def __init__(self, guard, dest_x, dest_y):
        self.x = guard.x + TILE_SIZE // 2
        self.y = guard.y + TILE_SIZE // 2
        self.dest_x = dest_x
        self.dest_y = dest_y
        self.speed = 10
        self.color = COLORS['particle_fire']
        self.radius = 8
        self.dx = 0
        self.dy = 0
        self.width = self.radius * 2
        self.height = self.radius * 2
        self.trail_timer = 0
    
    def update(self):
        if self.dx == 0 and self.dy == 0:
            dx = self.dest_x - self.x
            dy = self.dest_y - self.y
            dist = math.hypot(dx, dy)
            if dist > 0:
                self.dx = dx / dist
                self.dy = dy / dist
        else:
            self.x += self.dx * self.speed
            self.y += self.dy * self.speed
        
        self.trail_timer += 1
        if self.trail_timer % 4 == 0:
            particles.emit(self.x, self.y, self.color, 1, 1, 10, 3)
    
    def draw(self, offset=(0, 0)):
        draw_x = int(self.x) + offset[0]
        draw_y = int(self.y) + offset[1]
        
        glow_surf = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*self.color[:3], 100), (self.radius * 2, self.radius * 2), self.radius * 2)
        DISPLAYSURF.blit(glow_surf, (draw_x - self.radius * 2, draw_y - self.radius * 2))
        
        pygame.draw.circle(DISPLAYSURF, self.color, (draw_x, draw_y), self.radius)
        pygame.draw.circle(DISPLAYSURF, (255, 255, 200), (draw_x, draw_y), self.radius // 2)


# =============================================================================
# OBSTACLE - Walls/blocks in level
# =============================================================================
class Obstacle:
    """Vật cản trong game"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.image = pygame.transform.scale(pygame.image.load("images\\obstacle.png"), (TILE_SIZE, TILE_SIZE))
        self.width = TILE_SIZE
        self.height = TILE_SIZE
    
    def draw(self, offset=(0, 0)):
        DISPLAYSURF.blit(self.image, (self.x + offset[0], self.y + offset[1]))


# =============================================================================
# KEY - Collectible to open door
# =============================================================================
class Key:
    """Chìa khóa để mở cửa"""
    def __init__(self, x, y):
        self.image = pygame.transform.scale(pygame.image.load("images\\key.png"), (TILE_SIZE, TILE_SIZE))
        self.x = x
        self.y = y
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.float_offset = 0
        self.float_dir = 1
        self.glow_time = 0
    
    def update(self):
        self.float_offset += 0.15 * self.float_dir
        if abs(self.float_offset) > 5:
            self.float_dir *= -1
        self.glow_time += 1
    
    def draw(self, offset=(0, 0)):
        draw_x = self.x + offset[0]
        draw_y = self.y + offset[1] + self.float_offset
        
        glow_intensity = abs(math.sin(self.glow_time * 0.05)) * 100 + 50
        glow_surf = pygame.Surface((TILE_SIZE + 20, TILE_SIZE + 20), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*COLORS['gold'][:3], int(glow_intensity)), 
                          (TILE_SIZE // 2 + 10, TILE_SIZE // 2 + 10), TILE_SIZE // 2 + 5)
        DISPLAYSURF.blit(glow_surf, (draw_x - 10, draw_y - 10))
        DISPLAYSURF.blit(self.image, (draw_x, draw_y))


# =============================================================================
# DOOR - Exit door for level
# =============================================================================
class Door:
    """Cửa thoát level"""
    def __init__(self, x=None, y=None):
        self.closed_image = pygame.transform.scale(pygame.image.load("images\\door_close.png"), (TILE_SIZE, TILE_SIZE))
        self.open_image = pygame.transform.scale(pygame.image.load("images\\door_open.png"), (TILE_SIZE, TILE_SIZE))
        self.image = self.closed_image
        self.x = x if x is not None else (WINDOWWIDTH - TILE_SIZE)
        self.y = y if y is not None else (WINDOWHEIGHT - 2 * TILE_SIZE)
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.is_open = False
        self.glow_time = 0
    
    def reset(self, x=None, y=None):
        """Reset door state for a new level attempt."""
        self.image = self.closed_image
        self.is_open = False
        self.glow_time = 0
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
    
    def draw(self, offset=(0, 0)):
        draw_x = self.x + offset[0]
        draw_y = self.y + offset[1]
        
        if self.is_open:
            self.glow_time += 1
            glow_intensity = abs(math.sin(self.glow_time * 0.05)) * 80 + 80
            glow_surf = pygame.Surface((TILE_SIZE + 30, TILE_SIZE + 30), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*COLORS['door_glow'][:3], int(glow_intensity)), 
                              (TILE_SIZE // 2 + 15, TILE_SIZE // 2 + 15), TILE_SIZE // 2 + 15)
            DISPLAYSURF.blit(glow_surf, (draw_x - 15, draw_y - 15))
        
        DISPLAYSURF.blit(self.image, (draw_x, draw_y))
    
    def open(self):
        if self.is_open:
            return
        self.image = self.open_image
        self.is_open = True
        play_sound('door_open')


# =============================================================================
# POWERUP - Speed, Shield, Slow time
# =============================================================================
class PowerUp:
    """Power-up items (speed, shield, slow_time)"""
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.power_type = power_type
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.collected = False
        self.float_offset = 0
        self.float_dir = 1
        
        self.colors = {
            'speed': (255, 200, 50),
            'shield': (100, 200, 255),
            'slow_time': (200, 100, 255),
        }
    
    def update(self):
        self.float_offset += 0.1 * self.float_dir
        if abs(self.float_offset) > 3:
            self.float_dir *= -1
    
    def draw(self, offset=(0, 0)):
        if self.collected:
            return
        draw_x = self.x + offset[0]
        draw_y = self.y + offset[1]
        color = self.colors.get(self.power_type, (255, 255, 255))
        
        glow_surf = pygame.Surface((TILE_SIZE + 20, TILE_SIZE + 20), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*color, 50), (TILE_SIZE // 2 + 10, TILE_SIZE // 2 + 10), TILE_SIZE // 2 + 10)
        DISPLAYSURF.blit(glow_surf, (draw_x - 10, draw_y - 10 + self.float_offset))
        
        pygame.draw.circle(DISPLAYSURF, color, 
                          (int(draw_x + TILE_SIZE // 2), int(draw_y + TILE_SIZE // 2 + self.float_offset)), 
                          TILE_SIZE // 3)
        pygame.draw.circle(DISPLAYSURF, (255, 255, 255), 
                          (int(draw_x + TILE_SIZE // 2), int(draw_y + TILE_SIZE // 2 + self.float_offset)), 
                          TILE_SIZE // 3, 2)
        
        font = pygame.font.SysFont("arial", 16, bold=True)
        icons = {'speed': 'S', 'shield': 'D', 'slow_time': 'T'}
        text = font.render(icons.get(self.power_type, '?'), True, (255, 255, 255))
        text_rect = text.get_rect(center=(draw_x + TILE_SIZE // 2, draw_y + TILE_SIZE // 2 + self.float_offset))
        DISPLAYSURF.blit(text, text_rect)
