# main.py - Entry point cho game Dungeon Escape
"""
Dungeon Escape - Enhanced Edition
=================================
Cấu trúc đơn giản:
- config.py     : Constants, colors, settings
- levels.py     : Level data
- particles.py  : Particle system  
- collision.py  : Collision detection
- utils.py      : Utilities (ScreenShake, Background, Wall, Score)
- entities.py   : All game entities (Knight, Guard, Bullet, etc.)
- ui.py         : UI components (Button, HUD)
- screens.py    : Game screens (gameplay, menu, gameover)
"""

from config import TILE_SIZE
from levels import LEVELS
from collision import collision_grid
from utils import Background, Wall, Score
from entities import Knight, Guard, Obstacle, Key, PowerUp, Door
from screens import gameplay, gamestart, gameover


def load_level(level_index, knight):
    """Load level data và tạo game objects"""
    level = LEVELS[level_index]
    
    # Create obstacles
    obstacle_list = []
    for pos in level['obstacles']:
        obstacle_list.append(Obstacle(TILE_SIZE * pos[0], TILE_SIZE * pos[1]))
    
    # Build collision grid từ obstacles để tối ưu collision detection
    collision_grid.build_from_list(obstacle_list)
    
    # Create keys
    keys = [Key(pos[0], pos[1]) for pos in level['keys']]
    
    # Create guards
    guard_list = []
    for i, pos in enumerate(level['guards']):
        guard_type = ['normal', 'fast', 'heavy'][i % 3] if level_index >= 2 else 'normal'
        guard_list.append(Guard(pos[0], pos[1], knight, guard_type, level['guard_speed']))
    
    # Add power-ups based on level
    powerups = []
    if level_index >= 1:
        powerups.append(PowerUp(400, 300, 'speed'))
    if level_index >= 2:
        powerups.append(PowerUp(200, 200, 'shield'))
    if level_index >= 3:
        powerups.append(PowerUp(600, 250, 'slow_time'))
    
    return obstacle_list, keys, guard_list, powerups, level['knight_start']


def main():
    """Main game loop"""
    # Initialize shared game objects
    background = Background()
    wall = Wall()
    door = Door()
    score = Score()
    
    while True:
        # Show main menu and get selected level
        current_level = gamestart(wall, background)
        
        while True:
            # Setup level
            level_data = LEVELS[current_level]
            knight = Knight(level_data['knight_start'][0], level_data['knight_start'][1])
            
            obstacle_list, keys, guard_list, powerups, _ = load_level(current_level, knight)
            bullets = []
            
            # Run gameplay
            result = gameplay(background, wall, knight, door, obstacle_list, guard_list, 
                            bullets, keys, score, powerups, current_level)
            
            # Show game over screen
            action = gameover(result, score, current_level)
            
            if action == 'menu':
                break
            elif action == 'next':
                current_level = min(current_level + 1, len(LEVELS) - 1)
            # 'retry' continues the loop with same level


if __name__ == "__main__":
    main()
