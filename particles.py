# particles.py - Particle system
import pygame
import random
from config import DISPLAYSURF


class Particle:
    """Single particle với glow effect"""
    # Pre-rendered glow cache để tránh tạo surface mỗi frame
    glow_cache = {}
    
    @classmethod
    def get_glow_surface(cls, size, color, alpha):
        """Lấy hoặc tạo glow surface từ cache"""
        # Quantize alpha để giảm số lượng cache entries (chia thành 16 mức)
        alpha_key = (alpha // 16) * 16
        key = (size, color[:3], alpha_key)
        if key not in cls.glow_cache:
            surf = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*color[:3], alpha_key // 3), (size * 2, size * 2), size * 2)
            pygame.draw.circle(surf, (*color[:3], alpha_key), (size * 2, size * 2), size)
            cls.glow_cache[key] = surf
            # Giới hạn cache size để tránh memory leak
            if len(cls.glow_cache) > 500:
                cls.glow_cache.clear()
        return cls.glow_cache[key]
    
    def __init__(self, x, y, color, velocity=None, lifetime=30, size=4, gravity=0):
        self.x = x
        self.y = y
        self.color = color
        self.vx = velocity[0] if velocity else random.uniform(-2, 2)
        self.vy = velocity[1] if velocity else random.uniform(-2, 2)
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.gravity = gravity
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.lifetime -= 1
        return self.lifetime > 0
    
    def draw(self):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        size = max(1, int(self.size * (self.lifetime / self.max_lifetime)))
        # Sử dụng cached glow surface thay vì tạo mới mỗi frame
        glow_surf = Particle.get_glow_surface(size, self.color, alpha)
        DISPLAYSURF.blit(glow_surf, (int(self.x) - size * 2, int(self.y) - size * 2))


class ParticleSystem:
    """Quản lý tất cả particles trong game"""
    def __init__(self):
        self.particles = []
        self.max_particles = 50  # Giảm từ 150 để tối ưu hiệu năng
        self.emit_cooldown = {}  # Cooldown cho từng vị trí emit
        self.trail_cooldown = 0  # Cooldown cho trail particles
    
    def emit(self, x, y, color, count=3, spread=2, lifetime=30, size=4, gravity=0):
        # Thêm cooldown check theo vị trí để tránh emit quá nhiều
        key = (int(x) // 20, int(y) // 20)  # Grid 20x20 để group các vị trí gần nhau
        current_time = pygame.time.get_ticks()
        if key in self.emit_cooldown and current_time - self.emit_cooldown[key] < 50:
            return
        self.emit_cooldown[key] = current_time
        
        # Không emit nếu đã đầy
        if len(self.particles) >= self.max_particles:
            return
        
        # Giới hạn số particle thực sự tạo
        actual_count = min(count, self.max_particles - len(self.particles))
        for _ in range(actual_count):
            vel = (random.uniform(-spread, spread), random.uniform(-spread, spread))
            self.particles.append(Particle(x, y, color, vel, lifetime, size, gravity))
        
        # Dọn dẹp cooldown cũ định kỳ
        if len(self.emit_cooldown) > 100:
            old_time = current_time - 1000
            self.emit_cooldown = {k: v for k, v in self.emit_cooldown.items() if v > old_time}
    
    def emit_trail(self, x, y, color, direction):
        # Tăng cooldown cho trail từ mỗi frame lên mỗi 3 frame
        self.trail_cooldown += 1
        if self.trail_cooldown < 3:
            return
        self.trail_cooldown = 0
        
        if len(self.particles) < self.max_particles:
            self.particles.append(Particle(x, y, color, 
                                           (-direction[0] * 0.5 + random.uniform(-0.5, 0.5), 
                                            -direction[1] * 0.5 + random.uniform(-0.5, 0.5)), 
                                           20, 3))
    
    def update(self):
        self.particles = [p for p in self.particles if p.update()]
    
    def draw(self):
        for p in self.particles:
            p.draw()


# Global particle system instance
particles = ParticleSystem()
