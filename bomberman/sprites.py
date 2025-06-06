"""
Sprite classes for the Bomberman game
"""
import pygame
import random
from .constants import *

class Player:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
        self.lives = 3
        self.bomb_types = [BombType.FIRE]  # Start with fire bomb
        self.current_bomb_type = BombType.FIRE
        self.active_bomb = False
    
    def move(self, dx, dy, game):
        new_x, new_y = self.x + dx, self.y + dy
        
        # Check if the new position is valid
        if (0 <= new_x < game.grid_size and 
            0 <= new_y < game.grid_size and 
            game.grid[new_y][new_x] == EMPTY and
            not any(bomb.x == new_x and bomb.y == new_y for bomb in game.bombs)):
            self.x, self.y = new_x, new_y
    
    def place_bomb(self, game):
        # Check if player already has an active bomb
        if self.active_bomb:
            return False
            
        # Check if there's already a bomb at this position
        if any(bomb.x == self.x and bomb.y == self.y for bomb in game.bombs):
            return False
        
        # Create bomb based on current type
        if self.current_bomb_type == BombType.FIRE:
            bomb = Bomb(self.x, self.y, game.assets.fire_bomb_img, BombType.FIRE, self)
        elif self.current_bomb_type == BombType.ICE:
            bomb = Bomb(self.x, self.y, game.assets.ice_bomb_img, BombType.ICE, self)
        elif self.current_bomb_type == BombType.MEGA:
            bomb = Bomb(self.x, self.y, game.assets.mega_bomb_img, BombType.MEGA, self)
        
        game.bombs.append(bomb)
        self.active_bomb = True
        return True
    
    def switch_bomb_type(self):
        if len(self.bomb_types) > 1:
            current_index = self.bomb_types.index(self.current_bomb_type)
            next_index = (current_index + 1) % len(self.bomb_types)
            self.current_bomb_type = self.bomb_types[next_index]
    
    def hit(self):
        self.lives -= 1
        return self.lives <= 0
    
    def draw(self, screen):
        screen.blit(self.image, (self.x * TILE_SIZE, self.y * TILE_SIZE))

class Enemy:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
        self.frozen = 0  # Frames the enemy is frozen
        self.active_bomb = False
        self.bomb_cooldown = 0
    
    def move_random(self, game):
        if self.frozen > 0:
            self.frozen -= 1
            return
            
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            new_x, new_y = self.x + dx, self.y + dy
            
            # Check if the new position is valid
            if (0 <= new_x < game.grid_size and 
                0 <= new_y < game.grid_size and 
                game.grid[new_y][new_x] == EMPTY and
                not any(bomb.x == new_x and bomb.y == new_y for bomb in game.bombs)):
                
                # Basic bomb avoidance - don't move toward tiles that might explode soon
                if self.is_dangerous_tile(new_x, new_y, game):
                    continue
                    
                self.x, self.y = new_x, new_y
                break
    
    def is_dangerous_tile(self, x, y, game):
        # Check if any bomb might explode here soon
        for bomb in game.bombs:
            if bomb.timer < 30:  # About to explode
                # Check if this tile is in bomb's explosion range
                if (bomb.x == x or bomb.y == y) and abs(bomb.x - x) + abs(bomb.y - y) <= 2:
                    return True
        return False
    
    def try_place_bomb(self, game):
        # Check if enemy already has an active bomb or is on cooldown
        if self.active_bomb or self.bomb_cooldown > 0:
            if self.bomb_cooldown > 0:
                self.bomb_cooldown -= 1
            return False
            
        # Random chance to place bomb based on difficulty
        if random.random() > game.difficulty["npc_bomb_chance"]:
            return False
            
        # Check if there's already a bomb at this position
        if any(bomb.x == self.x and bomb.y == self.y for bomb in game.bombs):
            return False
        
        # Create bomb
        bomb = Bomb(self.x, self.y, game.assets.fire_bomb_img, BombType.FIRE, self)
        game.bombs.append(bomb)
        self.active_bomb = True
        return True
    
    def freeze(self):
        self.frozen = 180  # Freeze for 3 seconds (60 FPS * 3)
    
    def draw(self, screen):
        if self.frozen > 0 and self.frozen % 10 < 5:  # Blink when frozen
            # Draw with blue tint
            frozen_img = self.image.copy()
            frozen_img.fill((100, 100, 255, 128), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(frozen_img, (self.x * TILE_SIZE, self.y * TILE_SIZE))
        else:
            screen.blit(self.image, (self.x * TILE_SIZE, self.y * TILE_SIZE))

class Bomb:
    def __init__(self, x, y, image, bomb_type, owner):
        self.x = x
        self.y = y
        self.image = image
        self.bomb_type = bomb_type
        self.owner = owner  # Reference to player or enemy who placed the bomb
        self.timer = 120  # 2 seconds at 60 FPS
        self.exploded = False
        self.pulse_direction = 1  # For pulsing animation
        self.pulse_scale = 1.0
    
    def update(self):
        self.timer -= 1
        
        # Update pulse animation
        self.pulse_scale += 0.01 * self.pulse_direction
        if self.pulse_scale > 1.2:
            self.pulse_direction = -1
        elif self.pulse_scale < 0.8:
            self.pulse_direction = 1
        
        if self.timer <= 0:
            self.exploded = True
            # Reset owner's active bomb flag
            self.owner.active_bomb = False
            if isinstance(self.owner, Enemy):
                self.owner.bomb_cooldown = 120  # Cooldown before placing another bomb
    
    def draw(self, screen):
        # Make bomb pulse continuously
        scaled_size = int(TILE_SIZE * self.pulse_scale)
        offset = (TILE_SIZE - scaled_size) // 2
        
        # Make bomb flash red when about to explode
        if self.timer < 30 and self.timer % 10 < 5:
            flash_img = self.image.copy()
            flash_img.fill((255, 0, 0, 128), special_flags=pygame.BLEND_RGBA_ADD)
            scaled_img = pygame.transform.scale(flash_img, (scaled_size, scaled_size))
        else:
            scaled_img = pygame.transform.scale(self.image, (scaled_size, scaled_size))
            
        screen.blit(scaled_img, (self.x * TILE_SIZE + offset, self.y * TILE_SIZE + offset))

class Explosion:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
        self.timer = 30  # 0.5 seconds at 60 FPS
        self.finished = False
        self.scale = 0.5  # Start small and grow
    
    def update(self):
        self.timer -= 1
        
        # Grow explosion and then fade
        if self.timer > 15:
            self.scale = 0.5 + 0.5 * (1 - (self.timer - 15) / 15)
        
        if self.timer <= 0:
            self.finished = True
    
    def draw(self, screen):
        # Scale and fade the explosion
        alpha = int(255 * (self.timer / 30))
        scaled_size = int(TILE_SIZE * self.scale)
        offset = (TILE_SIZE - scaled_size) // 2
        
        img_copy = pygame.transform.scale(self.image, (scaled_size, scaled_size))
        img_copy.set_alpha(alpha)
        screen.blit(img_copy, (self.x * TILE_SIZE + offset, self.y * TILE_SIZE + offset))

class BombSkill:
    def __init__(self, x, y, bomb_type, image):
        self.x = x
        self.y = y
        self.bomb_type = bomb_type
        self.image = image
        self.float_offset = 0
        self.float_direction = 1
    
    def update(self):
        # Make the skill float up and down slightly
        self.float_offset += 0.2 * self.float_direction
        if self.float_offset > 3:
            self.float_direction = -1
        elif self.float_offset < -3:
            self.float_direction = 1
    
    def draw(self, screen):
        # Draw with floating effect
        screen.blit(self.image, (self.x * TILE_SIZE, self.y * TILE_SIZE + self.float_offset))