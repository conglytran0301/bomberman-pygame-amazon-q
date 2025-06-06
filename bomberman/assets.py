"""
Asset loading and management for Bomberman game
"""
import pygame
import random
from .constants import *

class GameAssets:
    def __init__(self):
        # Create visually distinct images for game elements
        
        # Player - blue circle with white border
        self.player_img = self.create_placeholder_image(TILE_SIZE, BLUE, border_color=WHITE, shape="circle")
        
        # Enemy - red circle with black border
        self.enemy_img = self.create_placeholder_image(TILE_SIZE, RED, border_color=BLACK, shape="circle")
        
        # Indestructible wall - dark gray brick pattern
        self.wall_img = self.create_brick_pattern(TILE_SIZE, (50, 50, 50), (30, 30, 30))
        
        # Destructible wall - brown wooden texture
        self.destructible_wall_img = self.create_wood_pattern(TILE_SIZE, (139, 69, 19), (160, 82, 45))
        
        # Empty tile - light green/gray floor
        self.empty_img = self.create_floor_pattern(TILE_SIZE, (200, 200, 200), (180, 180, 180))
        
        # Bomb images - distinct for each type
        self.fire_bomb_img = self.create_bomb_image(TILE_SIZE, RED)
        self.ice_bomb_img = self.create_bomb_image(TILE_SIZE, CYAN)
        self.mega_bomb_img = self.create_bomb_image(TILE_SIZE, PURPLE)
        
        # Explosion image - bright orange/yellow with animation effect
        self.explosion_img = self.create_explosion_image(TILE_SIZE)
        
        # Heart image for lives
        self.heart_img = self.create_placeholder_image(TILE_SIZE//2, RED, shape="heart")
        
        # Load sounds
        self.load_sounds()
    
    def create_placeholder_image(self, size, color, alpha=255, shape="square", border_color=None):
        img = pygame.Surface((size, size), pygame.SRCALPHA)
        
        if shape == "square":
            pygame.draw.rect(img, (*color, alpha), (0, 0, size, size))
            if border_color:
                pygame.draw.rect(img, border_color, (0, 0, size, size), 2)
        elif shape == "circle":
            pygame.draw.circle(img, (*color, alpha), (size//2, size//2), size//2 - 2)
            if border_color:
                pygame.draw.circle(img, border_color, (size//2, size//2), size//2, 2)
        elif shape == "heart":
            # Simple heart shape
            pygame.draw.circle(img, (*color, alpha), (size//4, size//4), size//4)
            pygame.draw.circle(img, (*color, alpha), (3*size//4, size//4), size//4)
            points = [(size//2, size), (0, size//2), (size//2, size//4), (size, size//2)]
            pygame.draw.polygon(img, (*color, alpha), points)
            if border_color:
                pygame.draw.polygon(img, border_color, points, 2)
        
        return img
    
    def create_brick_pattern(self, size, primary_color, secondary_color):
        """Create a brick pattern for indestructible walls"""
        img = pygame.Surface((size, size), pygame.SRCALPHA)
        img.fill(primary_color)
        
        # Draw brick pattern
        brick_height = size // 4
        for y in range(0, size, brick_height):
            offset = brick_height // 2 if (y // brick_height) % 2 else 0
            for x in range(-offset, size, brick_height * 2):
                pygame.draw.rect(img, secondary_color, (x, y, brick_height, 1))
                pygame.draw.rect(img, secondary_color, (x, y + brick_height - 1, brick_height, 1))
                pygame.draw.rect(img, secondary_color, (x, y, 1, brick_height))
                pygame.draw.rect(img, secondary_color, (x + brick_height - 1, y, 1, brick_height))
        
        # Add border for clarity
        pygame.draw.rect(img, BLACK, (0, 0, size, size), 2)
        return img
    
    def create_wood_pattern(self, size, primary_color, secondary_color):
        """Create a wood pattern for destructible walls"""
        img = pygame.Surface((size, size), pygame.SRCALPHA)
        img.fill(primary_color)
        
        # Draw wood grain
        for i in range(0, size, 4):
            line_width = 1 if i % 8 == 0 else 1
            pygame.draw.line(img, secondary_color, (0, i), (size, i), line_width)
        
        # Add some knots
        for _ in range(2):
            x, y = random.randint(5, size-5), random.randint(5, size-5)
            radius = random.randint(2, 4)
            pygame.draw.circle(img, secondary_color, (x, y), radius)
            pygame.draw.circle(img, primary_color, (x, y), radius-1)
        
        # Add border for clarity
        pygame.draw.rect(img, (100, 50, 0), (0, 0, size, size), 2)
        return img
    
    def create_floor_pattern(self, size, primary_color, secondary_color):
        """Create a floor pattern for empty tiles"""
        img = pygame.Surface((size, size), pygame.SRCALPHA)
        img.fill(primary_color)
        
        # Draw subtle grid pattern
        for i in range(0, size, size//4):
            pygame.draw.line(img, secondary_color, (i, 0), (i, size), 1)
            pygame.draw.line(img, secondary_color, (0, i), (size, i), 1)
        
        return img
    
    def create_bomb_image(self, size, color):
        """Create a bomb image with fuse"""
        img = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Draw bomb body (circle)
        bomb_radius = size // 2 - 4
        pygame.draw.circle(img, BLACK, (size//2, size//2 + 2), bomb_radius)
        
        # Add highlight
        highlight_pos = (size//2 - bomb_radius//2, size//2 - bomb_radius//2)
        highlight_radius = bomb_radius // 3
        pygame.draw.circle(img, (80, 80, 80), highlight_pos, highlight_radius)
        
        # Draw fuse
        fuse_start = (size//2, size//2 - bomb_radius + 2)
        fuse_end = (size//2, size//2 - bomb_radius - 6)
        pygame.draw.line(img, (139, 69, 19), fuse_start, fuse_end, 2)
        
        # Draw colored cap on fuse to indicate bomb type
        pygame.draw.circle(img, color, fuse_end, 3)
        
        return img
    
    def create_explosion_image(self, size):
        """Create an explosion image"""
        img = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Draw explosion (concentric circles with gradient)
        colors = [
            (255, 255, 0, 200),  # Yellow (inner)
            (255, 165, 0, 180),  # Orange (middle)
            (255, 0, 0, 160)     # Red (outer)
        ]
        
        radii = [size//6, size//3, size//2 - 2]
        center = (size//2, size//2)
        
        for i, (color, radius) in enumerate(zip(colors, radii)):
            pygame.draw.circle(img, color, center, radius)
        
        return img
    
    def load_sounds(self):
        # Initialize sound dictionary
        self.sounds = {}
        
        # We'll use placeholder sounds for now
        # In a real game, you would load actual sound files
        try:
            self.sounds["explosion"] = pygame.mixer.Sound("explosion.wav")
            self.sounds["pickup"] = pygame.mixer.Sound("pickup.wav")
        except:
            # If sound files don't exist, create dummy sound objects
            class DummySound:
                def play(self): pass
            
            self.sounds["explosion"] = DummySound()
            self.sounds["pickup"] = DummySound()
    
    def play_sound(self, sound_name):
        """Play a sound by name"""
        if sound_name in self.sounds:
            self.sounds[sound_name].play()