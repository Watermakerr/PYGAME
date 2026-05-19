# level_validator.py - Validate level data integrity
from config import TILE_SIZE


def validate_level(level, level_index):
    """Validate a level's data, raising ValueError on critical issues.
    All coordinates in the level dict are in TILE coords.
    """
    name = level.get('name', f'Level {level_index}')
    world_cols = level.get('world_cols', 18)
    world_rows = level.get('world_rows', 13)
    errors = []
    warnings = []

    def _in_bounds(col, row, label):
        """Check if a tile coordinate is inside the playable area (inside walls)."""
        if not (1 <= col <= world_cols - 2 and 1 <= row <= world_rows - 2):
            errors.append(f"  {label} at ({col},{row}) is outside playable area "
                          f"[1..{world_cols-2}, 1..{world_rows-2}]")
            return False
        return True

    obstacle_set = set(level.get('obstacles', []))

    def _not_in_obstacle(col, row, label):
        if (col, row) in obstacle_set:
            errors.append(f"  {label} at ({col},{row}) overlaps an obstacle")
            return False
        return True

    # --- Validate obstacles ---
    for pos in level.get('obstacles', []):
        _in_bounds(pos[0], pos[1], "Obstacle")

    # --- Validate knight_start ---
    ks = level.get('knight_start')
    if ks:
        _in_bounds(ks[0], ks[1], "knight_start")
        _not_in_obstacle(ks[0], ks[1], "knight_start")

    # --- Validate keys ---
    for pos in level.get('keys', []):
        _in_bounds(pos[0], pos[1], "Key")
        _not_in_obstacle(pos[0], pos[1], "Key")

    # --- Validate guards ---
    for pos in level.get('guards', []):
        _in_bounds(pos[0], pos[1], "Guard")
        _not_in_obstacle(pos[0], pos[1], "Guard")

    # --- Validate powerups ---
    for pu in level.get('powerups', []):
        _in_bounds(pu[0], pu[1], f"PowerUp({pu[2]})")
        _not_in_obstacle(pu[0], pu[1], f"PowerUp({pu[2]})")

    # --- Validate door ---
    door = level.get('door')
    if door:
        _in_bounds(door[0], door[1], "Door")
        _not_in_obstacle(door[0], door[1], "Door")

    # --- Report ---
    if errors:
        msg = f"Level '{name}' (index {level_index}) validation FAILED:\n" + "\n".join(errors)
        if warnings:
            msg += "\nWarnings:\n" + "\n".join(warnings)
        print(msg)
        raise ValueError(msg)
    elif warnings:
        print(f"Level '{name}' warnings:\n" + "\n".join(warnings))
    else:
        print(f"Level '{name}' validated OK.")


def validate_all_levels(levels):
    """Validate every level in the list."""
    for i, level in enumerate(levels):
        validate_level(level, i)
