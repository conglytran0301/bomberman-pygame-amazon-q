"""
Constants for the Bomberman game
"""
import enum

# Game settings
TILE_SIZE = 48  # Base tile size, will be dynamically adjusted based on screen size
FPS = 60

# Graphics quality settings
GRAPHICS_QUALITY = {
    "LOW": {"particles": 5, "glow_effects": False, "animation_frames": 3},
    "MEDIUM": {"particles": 15, "glow_effects": True, "animation_frames": 5},
    "HIGH": {"particles": 30, "glow_effects": True, "animation_frames": 8}
}

# Default to medium quality
CURRENT_QUALITY = "MEDIUM"

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

# Enhanced colors for tech theme
TECH_BLUE = (70, 130, 180)
TECH_RED = (180, 60, 60)
TECH_GREEN = (60, 180, 100)
TECH_GOLD = (218, 165, 32)
TECH_SILVER = (192, 192, 192)
NEON_BLUE = (30, 144, 255)
NEON_GREEN = (57, 255, 20)
NEON_PINK = (255, 20, 147)

# Bomb types
class BombType(enum.Enum):
    FIRE = 1    # Fire bomb - deals 2 damage
    ICE = 2     # Ice bomb - deals 1 damage and slows
    MEGA = 3    # Mega bomb - deals 3 damage with larger radius

# Bomb damage values
BOMB_DAMAGE = {
    BombType.FIRE: 2,
    BombType.ICE: 1,
    BombType.MEGA: 3
}

# Bomb effects
BOMB_EFFECTS = {
    BombType.FIRE: "damage",
    BombType.ICE: "slow",
    BombType.MEGA: "damage"
}

# Difficulty settings
class Difficulty:
    EASY = {"size": 13, "enemies": 3, "walls_percent": 0.15, "skills_count": 3, "npc_bomb_chance": 0.01}
    NORMAL = {"size": 15, "enemies": 5, "walls_percent": 0.2, "skills_count": 5, "npc_bomb_chance": 0.02}
    HARD = {"size": 17, "enemies": 8, "walls_percent": 0.25, "skills_count": 8, "npc_bomb_chance": 0.03}

# Tile types for grid
EMPTY = 0
WALL = 1
DESTRUCTIBLE = 2