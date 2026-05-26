# main.py - Entry point cho game Dungeon Escape
"""
Dungeon Escape
=================================
Cấu trúc đơn giản:
- config.py           : Constants, colors, settings
- levels.py           : Level data (all tile-based)
- level_validator.py  : Validate level data at load time
- camera.py           : Room-based camera system
- particles.py        : Particle system  
- collision.py        : Collision detection
- utils.py            : Utilities (ScreenShake, Background, Wall, Score)
- entities.py         : All game entities (Knight, Guard, Bullet, etc.)
- ui.py               : UI components (Button, HUD)
- screens.py          : Game screens (gameplay, menu, gameover)
"""

from config import TILE_SIZE
from levels import LEVELS
from level_validator import validate_all_levels
from collision import collision_grid
from utils import Background, Wall, Score
from entities import Knight, Guard, Obstacle, Key, PowerUp, Door
from screens import gameplay, gamestart, gameover


def load_level(level_index, knight):
    """Load level data và tạo game objects.
    All level coordinates are in tiles — converted to pixels here.
    """
    level = LEVELS[level_index]
    
    world_cols = level.get('world_cols', 18)
    world_rows = level.get('world_rows', 13)
    world_width = world_cols * TILE_SIZE
    world_height = world_rows * TILE_SIZE
    
    # Create obstacles (tile → pixel)
    obstacle_list = [Obstacle(pos[0] * TILE_SIZE, pos[1] * TILE_SIZE)
                     for pos in level['obstacles']]
    
    # Build collision grid từ obstacles để tối ưu collision detection
    collision_grid.build_from_list(obstacle_list)
    
    # Create keys (tile → pixel)
    keys = [Key(pos[0] * TILE_SIZE, pos[1] * TILE_SIZE)
            for pos in level['keys']]
    
    # Create guards (tile → pixel)
    guard_list = []
    for i, pos in enumerate(level['guards']):
        guard_type = ['normal', 'fast', 'heavy'][i % 3] if level_index >= 2 else 'normal'
        guard_list.append(Guard(
            pos[0] * TILE_SIZE,
            pos[1] * TILE_SIZE,
            knight,
            guard_type,
            level['guard_speed'],
            world_cols,
            world_rows,
            level['obstacles'],
        ))
    
    # Create power-ups (tile → pixel) — now stored in level data
    powerups = [PowerUp(pu[0] * TILE_SIZE, pu[1] * TILE_SIZE, pu[2])
                for pu in level.get('powerups', [])]
    
    # Knight start position (tile → pixel)
    knight_start = (level['knight_start'][0] * TILE_SIZE,
                    level['knight_start'][1] * TILE_SIZE)
    
    # Door position (tile → pixel)
    door_pos = (level['door'][0] * TILE_SIZE,
                level['door'][1] * TILE_SIZE)
    
    return (obstacle_list, keys, guard_list, powerups,
            knight_start, door_pos, world_width, world_height,
            world_cols, world_rows)


def main():
    """Main game loop"""
    # Validate all levels at startup
    validate_all_levels(LEVELS)
    
    # Initialize shared game objects (will be re-created per level for world size)
    door = Door()
    score = Score()
    
    while True:
        # Show main menu (use default 1-room bg/wall for menu)
        background = Background()
        wall = Wall()
        current_level = gamestart(wall, background)
        
        while True:
            # Setup level
            level_data = LEVELS[current_level]
            world_cols = level_data.get('world_cols', 18)
            world_rows = level_data.get('world_rows', 13)
            
            knight_start = (level_data['knight_start'][0] * TILE_SIZE,
                            level_data['knight_start'][1] * TILE_SIZE)
            knight = Knight(knight_start[0], knight_start[1])
            
            (obstacle_list, keys, guard_list, powerups,
             _, door_pos, world_width, world_height,
             w_cols, w_rows) = load_level(current_level, knight)
            
            bullets = []
            
            # Create world-sized background and wall
            background = Background(world_cols, world_rows)
            wall = Wall(world_cols, world_rows)
            
            # Reset door to level position
            door.reset(door_pos[0], door_pos[1])
            score.__init__()
            
            # Run gameplay
            result = gameplay(background, wall, knight, door, obstacle_list, guard_list,
                            bullets, keys, score, powerups, current_level,
                            world_width, world_height)
            
            # Show game over screen
            action = gameover(result, score, current_level)
            
            if action == 'menu':
                break
            elif action == 'next':
                current_level = min(current_level + 1, len(LEVELS) - 1)
            # 'retry' continues the loop with same level


if __name__ == "__main__":
    main()
