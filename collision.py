# collision.py - Collision detection system
import pygame
from config import TILE_SIZE


class CollisionGrid:
    """Grid-based spatial partitioning để tối ưu collision detection"""
    def __init__(self, cell_size=100):
        self.cell_size = cell_size
        self.grid = {}
    
    def clear(self):
        """Xóa grid - gọi khi load level mới"""
        self.grid.clear()
    
    def _get_cell(self, x, y):
        """Lấy cell key từ tọa độ"""
        return (int(x) // self.cell_size, int(y) // self.cell_size)
    
    def _get_cells_for_rect(self, rect):
        """Lấy tất cả cells mà rect có thể chạm vào"""
        min_cell_x = int(rect.x) // self.cell_size
        max_cell_x = int(rect.x + rect.width) // self.cell_size
        min_cell_y = int(rect.y) // self.cell_size
        max_cell_y = int(rect.y + rect.height) // self.cell_size
        
        cells = []
        for cx in range(min_cell_x, max_cell_x + 1):
            for cy in range(min_cell_y, max_cell_y + 1):
                cells.append((cx, cy))
        return cells
    
    def add_obstacle(self, obstacle):
        """Thêm obstacle vào grid"""
        rect = pygame.Rect(obstacle.x, obstacle.y, obstacle.width, obstacle.height)
        for cell in self._get_cells_for_rect(rect):
            if cell not in self.grid:
                self.grid[cell] = []
            if obstacle not in self.grid[cell]:
                self.grid[cell].append(obstacle)
    
    def build_from_list(self, obstacles):
        """Build grid từ danh sách obstacles"""
        self.clear()
        for obs in obstacles:
            self.add_obstacle(obs)
    
    def get_nearby_obstacles(self, rect):
        """Lấy các obstacles gần rect (chỉ trong các cells liên quan)"""
        nearby = set()
        for cell in self._get_cells_for_rect(rect):
            if cell in self.grid:
                for obs in self.grid[cell]:
                    nearby.add(obs)
        return list(nearby)


# Global collision grid instance
collision_grid = CollisionGrid(cell_size=TILE_SIZE * 2)


def check_collision(rect_1, rect_2, shrink=0):
    """Kiểm tra va chạm với tùy chọn thu nhỏ hitbox để dễ đi qua khe hẹp"""
    rect1_rect = pygame.Rect(rect_1.x + shrink, rect_1.y + shrink, 
                              rect_1.width - shrink * 2, rect_1.height - shrink * 2)
    rect2_rect = pygame.Rect(rect_2.x, rect_2.y, rect_2.width, rect_2.height)
    return rect1_rect.colliderect(rect2_rect)


def check_collision_with_grid(rect, shrink=0):
    """Kiểm tra va chạm sử dụng spatial grid - tối ưu hơn check tất cả obstacles"""
    nearby = collision_grid.get_nearby_obstacles(rect)
    for obs in nearby:
        if check_collision(rect, obs, shrink):
            return True
    return False
