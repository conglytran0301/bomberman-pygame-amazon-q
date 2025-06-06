"""
Map generation and management for Bomberman game
"""
import random
import pygame
from .constants import *
from .sprites import BombSkill

class Map:
    def __init__(self, difficulty, game_assets):
        self.difficulty = difficulty
        self.grid_size = difficulty["size"]
        self.grid = [[EMPTY for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.assets = game_assets
        self.skills = []
        
        # Generate the map
        self.generate_map()
    
    def generate_map(self):
        # Reset grid
        self.grid = [[EMPTY for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.skills = []
        
        # Place indestructible walls (border and pattern)
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                # Border walls
                if x == 0 or y == 0 or x == self.grid_size - 1 or y == self.grid_size - 1:
                    self.grid[y][x] = WALL
                # Pattern walls (every other tile)
                elif x % 2 == 0 and y % 2 == 0:
                    self.grid[y][x] = WALL
        
        # Place destructible walls
        wall_count = int(self.grid_size * self.grid_size * self.difficulty["walls_percent"])
        placed = 0
        
        while placed < wall_count:
            x = random.randint(1, self.grid_size - 2)
            y = random.randint(1, self.grid_size - 2)
            
            # Skip if already a wall or too close to player start
            if self.grid[y][x] != EMPTY or (x <= 2 and y <= 2):
                continue
            
            self.grid[y][x] = DESTRUCTIBLE
            placed += 1
        
        # Place skill bombs under destructible walls
        for _ in range(self.difficulty["skills_count"]):
            attempts = 0
            while attempts < 100:  # Prevent infinite loop
                x = random.randint(1, self.grid_size - 2)
                y = random.randint(1, self.grid_size - 2)
                
                if self.grid[y][x] == DESTRUCTIBLE:
                    bomb_type = random.choice(list(BombType))
                    
                    # Select appropriate image based on bomb type
                    if bomb_type == BombType.FIRE:
                        image = self.assets.fire_bomb_img
                    elif bomb_type == BombType.ICE:
                        image = self.assets.ice_bomb_img
                    else:  # MEGA
                        image = self.assets.mega_bomb_img
                    
                    self.skills.append(BombSkill(x, y, bomb_type, image))
                    break
                
                attempts += 1
    
    def get_valid_spawn_position(self):
        """Get a valid position for spawning enemies"""
        while True:
            x = random.randint(3, self.grid_size - 2)
            y = random.randint(3, self.grid_size - 2)
            
            if self.grid[y][x] == EMPTY:
                return x, y
    
    def is_valid_move(self, x, y, bombs):
        """Check if a position is valid for movement"""
        if x < 0 or x >= self.grid_size or y < 0 or y >= self.grid_size:
            return False
            
        if self.grid[y][x] != EMPTY:
            return False
            
        # Check for bombs
        for bomb in bombs:
            if bomb.x == x and bomb.y == y:
                return False
                
        return True
    
    def draw(self, screen):
        """Draw the map"""
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                
                # Draw tile based on grid value
                if self.grid[y][x] == EMPTY:
                    screen.blit(self.assets.empty_img, rect)
                elif self.grid[y][x] == WALL:
                    screen.blit(self.assets.wall_img, rect)
                elif self.grid[y][x] == DESTRUCTIBLE:
                    screen.blit(self.assets.destructible_wall_img, rect)
        
        # Draw skill bombs (only if not hidden under walls)
        for skill in self.skills:
            if self.grid[skill.y][skill.x] == EMPTY:
                skill.update()  # Update floating animation
                skill.draw(screen)
    
    def draw_debug_overlay(self, screen, font):
        """Draw debug information on tiles"""
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                tile_type = self.grid[y][x]
                label = ""
                
                if tile_type == EMPTY:
                    label = "E"
                elif tile_type == WALL:
                    label = "W"
                elif tile_type == DESTRUCTIBLE:
                    label = "D"
                
                text = font.render(label, True, (255, 255, 255))
                screen.blit(text, (x * TILE_SIZE + 5, y * TILE_SIZE + 5))