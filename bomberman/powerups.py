"""
Power-up system for Bomberman game
"""
import pygame
import random
from .constants import *

class PowerUp:
    def __init__(self, x, y, power_type, image):
        self.x = x
        self.y = y
        self.type = power_type
        self.image = image
        self.float_offset = 0
        self.float_direction = 1
        self.collected = False
        self.active_time = 0  # For temporary power-ups
    
    def update(self):
        """Update power-up animation"""
        # Make the power-up float up and down slightly
        self.float_offset += 0.2 * self.float_direction
        if self.float_offset > 3:
            self.float_direction = -1
        elif self.float_offset < -3:
            self.float_direction = 1
            
        # Update active time for temporary power-ups
        if self.active_time > 0:
            self.active_time -= 1
            return self.active_time > 0
        return True
    
    def draw(self, screen):
        """Draw the power-up with floating effect"""
        if not self.collected:
            screen.blit(self.image, (self.x * TILE_SIZE, self.y * TILE_SIZE + self.float_offset))
    
    def apply(self, player):
        """Apply power-up effect to player"""
        if self.type == PowerUpType.SPEED:
            player.speed_boost = 600  # 10 seconds at 60 FPS
        elif self.type == PowerUpType.EXTRA_BOMB:
            player.max_bombs += 1
        elif self.type == PowerUpType.BOMB_RANGE:
            player.bomb_range += 1
        elif self.type == PowerUpType.SHIELD:
            player.shield = True
            player.shield_time = 600  # 10 seconds at 60 FPS
        elif self.type == PowerUpType.EXTRA_LIFE:
            player.lives = min(player.lives + 1, 5)  # Max 5 lives
        elif self.type == PowerUpType.REMOTE_BOMB:
            player.has_remote_bomb = True
            player.remote_bombs = []
        elif self.type == PowerUpType.ARMOR:
            player.armor = min(player.armor + 1, 3)  # Max level 3 armor
            player.armor_time = 900  # 15 seconds at 60 FPS
        elif self.type == PowerUpType.HEALTH:
            player.health = min(player.health + 2, 5)  # Restore 2 health, max 5
        elif self.type == PowerUpType.ICE_IMMUNITY:
            player.slow_immune = 600  # 10 seconds at 60 FPS

class PowerUpType:
    SPEED = "speed"           # Increases movement speed
    EXTRA_BOMB = "extra_bomb" # Allows placing more bombs
    BOMB_RANGE = "bomb_range" # Increases bomb explosion range
    SHIELD = "shield"         # Protects from one hit
    EXTRA_LIFE = "extra_life" # Adds one life
    REMOTE_BOMB = "remote_bomb" # Allows remote detonation
    ARMOR = "armor"           # Reduces damage taken
    HEALTH = "health"         # Restores health points
    ICE_IMMUNITY = "ice_immunity" # Immunity to ice bomb slow effect

class PowerUpManager:
    def __init__(self, game_assets):
        self.assets = game_assets
        self.powerups = []
        
    def create_powerup(self, x, y):
        """Create a random power-up at the specified position"""
        # Determine power-up type with different probabilities
        power_types = [
            (PowerUpType.SPEED, 0.20),
            (PowerUpType.EXTRA_BOMB, 0.20),
            (PowerUpType.BOMB_RANGE, 0.15),
            (PowerUpType.SHIELD, 0.10),
            (PowerUpType.EXTRA_LIFE, 0.05),
            (PowerUpType.REMOTE_BOMB, 0.10),
            (PowerUpType.ARMOR, 0.10),
            (PowerUpType.HEALTH, 0.05),
            (PowerUpType.ICE_IMMUNITY, 0.05)
        ]
        
        # Select power-up type based on probability
        power_type = random.choices(
            [p[0] for p in power_types],
            weights=[p[1] for p in power_types],
            k=1
        )[0]
        
        # Get appropriate image based on type
        if power_type == PowerUpType.SPEED:
            image = self.assets.speed_powerup_img
        elif power_type == PowerUpType.EXTRA_BOMB:
            image = self.assets.bomb_powerup_img
        elif power_type == PowerUpType.BOMB_RANGE:
            image = self.assets.range_powerup_img
        elif power_type == PowerUpType.SHIELD:
            image = self.assets.shield_powerup_img
        elif power_type == PowerUpType.EXTRA_LIFE:
            image = self.assets.life_powerup_img
        elif power_type == PowerUpType.REMOTE_BOMB:
            image = self.assets.remote_powerup_img
        elif power_type == PowerUpType.ARMOR:
            image = self.assets.armor_powerup_img
        elif power_type == PowerUpType.HEALTH:
            image = self.assets.health_powerup_img
        elif power_type == PowerUpType.ICE_IMMUNITY:
            image = self.assets.ice_immunity_powerup_img
        
        # Create and return the power-up
        powerup = PowerUp(x, y, power_type, image)
        self.powerups.append(powerup)
        return powerup
    
    def update(self):
        """Update all power-ups"""
        for powerup in self.powerups[:]:
            if not powerup.update():
                self.powerups.remove(powerup)
    
    def draw(self, screen):
        """Draw all power-ups"""
        for powerup in self.powerups:
            powerup.draw(screen)
    
    def check_collision(self, player):
        """Check if player collides with any power-up"""
        for powerup in self.powerups[:]:
            if powerup.x == player.x and powerup.y == player.y and not powerup.collected:
                powerup.apply(player)
                powerup.collected = True
                self.powerups.remove(powerup)
                return True
        return False