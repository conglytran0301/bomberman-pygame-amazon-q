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
        self.health = 5       # Health points (5 max)
        self.bomb_types = [BombType.FIRE]  # Start with fire bomb
        self.current_bomb_type = BombType.FIRE
        self.active_bomb = False
        
        # Power-up related attributes
        self.speed_boost = 0  # Timer for speed boost
        self.max_bombs = 1    # Maximum bombs player can place at once
        self.bomb_range = 2   # Range of bomb explosions
        self.shield = False   # Protection from one hit
        self.shield_time = 0  # Timer for shield
        self.armor = 0        # Damage reduction (0-3)
        self.armor_time = 0   # Timer for armor
        self.has_remote_bomb = False  # Remote detonation ability
        self.remote_bombs = []  # List of remote bombs
        self.slow_immune = 0  # Timer for ice bomb immunity
    
    def move(self, dx, dy, game):
        new_x, new_y = self.x + dx, self.y + dy
        
        # Check if the new position is valid
        if (0 <= new_x < game.grid_size and 
            0 <= new_y < game.grid_size and 
            game.grid[new_y][new_x] == EMPTY and
            not any(bomb.x == new_x and bomb.y == new_y for bomb in game.bombs)):
            self.x, self.y = new_x, new_y
            
            # Check for power-up collision
            if hasattr(game, 'powerup_manager'):
                game.powerup_manager.check_collision(self)
    
    def place_bomb(self, game):
        # Check if player already has max bombs placed
        active_bombs = sum(1 for bomb in game.bombs if bomb.owner == self)
        if active_bombs >= self.max_bombs:
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
        
        # Set bomb range based on player's bomb_range attribute
        bomb.range = self.bomb_range
        
        # Handle remote bombs
        if self.has_remote_bomb:
            bomb.is_remote = True
            bomb.timer = 9999  # Won't explode until detonated
            self.remote_bombs.append(bomb)
        
        game.bombs.append(bomb)
        return True
    
    def switch_bomb_type(self):
        if len(self.bomb_types) > 1:
            current_index = self.bomb_types.index(self.current_bomb_type)
            next_index = (current_index + 1) % len(self.bomb_types)
            self.current_bomb_type = self.bomb_types[next_index]
    
    def hit(self, damage=1, effect=None):
        # Check if player has shield
        if self.shield:
            self.shield = False
            self.shield_time = 0
            return False  # Shield absorbed the hit
        
        # Apply armor damage reduction
        if self.armor > 0:
            damage = max(1, damage - self.armor)  # Minimum 1 damage
        
        # Apply damage to health
        self.health -= damage
        
        # Apply effect
        if effect == "slow" and self.slow_immune <= 0:
            # Apply slow effect (reduce speed)
            self.speed_boost = -180  # Slow for 3 seconds
        
        # Check if health is depleted
        if self.health <= 0:
            self.lives -= 1
            if self.lives > 0:
                # Reset health if still has lives
                self.health = 5
                return False
            return True  # Game over
        
        return False
    
    def update(self):
        """Update player status effects"""
        # Update speed boost timer
        if self.speed_boost > 0:
            self.speed_boost -= 1
        elif self.speed_boost < 0:
            # Negative speed boost means slowed
            self.speed_boost += 1
        
        # Update shield timer
        if self.shield_time > 0:
            self.shield_time -= 1
            if self.shield_time <= 0:
                self.shield = False
        
        # Update armor timer
        if self.armor_time > 0:
            self.armor_time -= 1
            if self.armor_time <= 0:
                self.armor = 0
        
        # Update slow immunity timer
        if self.slow_immune > 0:
            self.slow_immune -= 1
    
    def detonate_remote_bombs(self, game):
        """Detonate all remote bombs"""
        if not self.has_remote_bomb or not self.remote_bombs:
            return False
        
        for bomb in self.remote_bombs[:]:
            bomb.timer = 1  # Set to explode on next update
        
        self.remote_bombs = []
        return True
    
    def draw(self, screen):
        # Draw player
        screen.blit(self.image, (self.x * TILE_SIZE, self.y * TILE_SIZE))
        
        # Draw shield effect if active
        if self.shield:
            shield_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(shield_surf, (100, 200, 255, 100), (TILE_SIZE//2, TILE_SIZE//2), TILE_SIZE//2)
            pygame.draw.circle(shield_surf, (150, 220, 255, 150), (TILE_SIZE//2, TILE_SIZE//2), TILE_SIZE//2, 2)
            screen.blit(shield_surf, (self.x * TILE_SIZE, self.y * TILE_SIZE))
        
        # Draw armor effect if active
        if self.armor > 0:
            armor_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            armor_color = (255, 215, 0, 50 + self.armor * 30)  # Gold color, opacity based on armor level
            pygame.draw.rect(armor_surf, armor_color, (2, 2, TILE_SIZE-4, TILE_SIZE-4), 2)
            # Add corner reinforcements
            for corner in [(4, 4), (TILE_SIZE-4, 4), (4, TILE_SIZE-4), (TILE_SIZE-4, TILE_SIZE-4)]:
                pygame.draw.circle(armor_surf, armor_color, corner, 3)
            screen.blit(armor_surf, (self.x * TILE_SIZE, self.y * TILE_SIZE))
        
        # Draw speed boost effect if active
        if self.speed_boost > 0:
            # Draw speed lines behind player
            for i in range(3):
                offset = random.randint(5, 15)
                pygame.draw.line(screen, (255, 255, 255, 150), 
                                ((self.x * TILE_SIZE) + TILE_SIZE//2, (self.y * TILE_SIZE) + TILE_SIZE//2),
                                ((self.x * TILE_SIZE) - offset + TILE_SIZE//2, (self.y * TILE_SIZE) + TILE_SIZE//2),
                                2)
        
        # Draw slow effect if active
        elif self.speed_boost < 0:
            # Draw slow indicators (ice particles)
            slow_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            for i in range(4):
                x = random.randint(4, TILE_SIZE-4)
                y = random.randint(4, TILE_SIZE-4)
                size = random.randint(2, 4)
                pygame.draw.circle(slow_surf, (150, 220, 255, 200), (x, y), size)
            screen.blit(slow_surf, (self.x * TILE_SIZE, self.y * TILE_SIZE))
        
        # Draw ice immunity indicator if active
        if self.slow_immune > 0:
            # Draw a blue outline
            immune_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(immune_surf, (0, 150, 255, 100), (TILE_SIZE//2, TILE_SIZE//2), TILE_SIZE//2, 1)
            screen.blit(immune_surf, (self.x * TILE_SIZE, self.y * TILE_SIZE))

class Enemy:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
        self.frozen = 0  # Frames the enemy is frozen
        self.active_bomb = False
        self.bomb_cooldown = 0
        self.ai = None  # Will be initialized in game controller
    
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
            
        # Check if there's already a bomb at this position
        if any(bomb.x == self.x and bomb.y == self.y for bomb in game.bombs):
            return False
        
        # Choose bomb type based on situation and difficulty
        bomb_type = BombType.FIRE  # Default bomb type
        bomb_img = game.assets.fire_bomb_img
        
        # On harder difficulties, enemies can use different bomb types
        if hasattr(game, 'difficulty'):
            if game.difficulty == Difficulty.HARD:
                # On hard difficulty, enemies can use all bomb types
                # Check if player is nearby
                player_distance = abs(self.x - game.player.x) + abs(self.y - game.player.y)
                
                if player_distance <= 3:
                    # Player is close, use ice bomb to slow them down
                    bomb_type = BombType.ICE
                    bomb_img = game.assets.ice_bomb_img
                elif random.random() < 0.3:
                    # Sometimes use mega bomb for larger explosions
                    bomb_type = BombType.MEGA
                    bomb_img = game.assets.mega_bomb_img
            elif game.difficulty == Difficulty.NORMAL:
                # On normal difficulty, enemies can sometimes use ice bombs
                if random.random() < 0.2:
                    bomb_type = BombType.ICE
                    bomb_img = game.assets.ice_bomb_img
        
        # Create bomb with selected type
        bomb = Bomb(self.x, self.y, bomb_img, bomb_type, self)
        
        # Set bomb range based on difficulty
        if hasattr(game, 'difficulty'):
            if game.difficulty == Difficulty.HARD:
                bomb.range = 3  # Longer range on hard difficulty
            elif game.difficulty == Difficulty.NORMAL:
                bomb.range = 2  # Default range on normal
            else:
                bomb.range = 2  # Default range on easy
        
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
        self.range = 2  # Default explosion range
        self.is_remote = False  # Whether this is a remote bomb
    
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
        
        # Make bomb flash red when about to explode or blue if remote
        if self.is_remote:
            # Remote bomb has blue indicator
            flash_img = self.image.copy()
            if self.timer % 30 < 15:  # Slow pulse for remote bombs
                flash_img.fill((0, 100, 255, 100), special_flags=pygame.BLEND_RGBA_ADD)
            scaled_img = pygame.transform.scale(flash_img, (scaled_size, scaled_size))
            
            # Draw "R" indicator for remote bomb
            font = pygame.font.SysFont('Arial', 12)
            r_text = font.render("R", True, (255, 255, 255))
            screen.blit(scaled_img, (self.x * TILE_SIZE + offset, self.y * TILE_SIZE + offset))
            screen.blit(r_text, (self.x * TILE_SIZE + TILE_SIZE//2 - r_text.get_width()//2, 
                                self.y * TILE_SIZE + TILE_SIZE//2 - r_text.get_height()//2))
        else:
            # Regular bomb with normal timer
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