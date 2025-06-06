"""
Constants for the Bomberman game
"""
import enum

# Game settings
TILE_SIZE = 40  # This will be dynamically adjusted based on screen size
FPS = 60

# Screen dimensions will be calculated based on grid size and tile size

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
PURPLE = (128, 0, 128)

# Bomb types
class BombType(enum.Enum):
    FIRE = 1
    ICE = 2
    MEGA = 3

# Difficulty settings
class Difficulty:
    EASY = {"size": 15, "enemies": 3, "walls_percent": 0.15, "skills_count": 3, "npc_bomb_chance": 0.01}
    NORMAL = {"size": 20, "enemies": 5, "walls_percent": 0.2, "skills_count": 5, "npc_bomb_chance": 0.02}
    HARD = {"size": 25, "enemies": 8, "walls_percent": 0.25, "skills_count": 8, "npc_bomb_chance": 0.03}

# Tile types for grid
EMPTY = 0
WALL = 1
DESTRUCTIBLE = 2