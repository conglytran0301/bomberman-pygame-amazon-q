import pygame
import random
import sys
import os
from enum import Enum

# Initialize pygame
pygame.init()

# Game constants
TILE_SIZE = 40
FPS = 60

# Bomb types
class BombType(Enum):
    FIRE = 1
    ICE = 2
    MEGA = 3

# Difficulty settings
class Difficulty:
    EASY = {"size": 15, "enemies": 3, "walls_percent": 0.15, "skills_count": 3}
    NORMAL = {"size": 20, "enemies": 5, "walls_percent": 0.2, "skills_count": 5}
    HARD = {"size": 25, "enemies": 8, "walls_percent": 0.25, "skills_count": 8}

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

# Game class
class BombermanGame:
    def __init__(self):
        self.running = True
        self.clock = pygame.time.Clock()
        self.difficulty = None
        self.grid_size = 0
        self.screen = None
        self.font = pygame.font.SysFont('Arial', 24)
        self.big_font = pygame.font.SysFont('Arial', 48)
        
        # Game objects
        self.player = None
        self.enemies = []
        self.bombs = []
        self.explosions = []
        self.walls = []
        self.destructible_walls = []
        self.skills = []
        
        # Game state
        self.score = 0
        self.game_over = False
        self.grid = []
        
        # Load assets
        self.load_assets()
        
        # Start with difficulty selection
        self.show_difficulty_selection()
    
    def load_assets(self):
        # Create placeholder images for sprites
        self.player_img = self.create_placeholder_image(TILE_SIZE, BLUE)
        self.enemy_img = self.create_placeholder_image(TILE_SIZE, RED)
        self.wall_img = self.create_placeholder_image(TILE_SIZE, GRAY)
        self.destructible_wall_img = self.create_placeholder_image(TILE_SIZE, ORANGE)
        self.empty_img = self.create_placeholder_image(TILE_SIZE, GREEN, alpha=100)
        
        # Bomb images
        self.fire_bomb_img = self.create_placeholder_image(TILE_SIZE, RED, shape="circle")
        self.ice_bomb_img = self.create_placeholder_image(TILE_SIZE, CYAN, shape="circle")
        self.mega_bomb_img = self.create_placeholder_image(TILE_SIZE, PURPLE, shape="circle")
        
        # Explosion images
        self.explosion_img = self.create_placeholder_image(TILE_SIZE, YELLOW)
        
        # Heart image for lives
        self.heart_img = self.create_placeholder_image(TILE_SIZE//2, RED, shape="heart")
    
    def create_placeholder_image(self, size, color, alpha=255, shape="square"):
        img = pygame.Surface((size, size), pygame.SRCALPHA)
        
        if shape == "square":
            pygame.draw.rect(img, (*color, alpha), (0, 0, size, size))
            pygame.draw.rect(img, BLACK, (0, 0, size, size), 2)
        elif shape == "circle":
            pygame.draw.circle(img, (*color, alpha), (size//2, size//2), size//2)
            pygame.draw.circle(img, BLACK, (size//2, size//2), size//2, 2)
        elif shape == "heart":
            # Simple heart shape
            pygame.draw.circle(img, (*color, alpha), (size//4, size//4), size//4)
            pygame.draw.circle(img, (*color, alpha), (3*size//4, size//4), size//4)
            points = [(size//2, size), (0, size//2), (size//2, size//4), (size, size//2)]
            pygame.draw.polygon(img, (*color, alpha), points)
            pygame.draw.polygon(img, BLACK, points, 2)
        
        return img
    
    def show_difficulty_selection(self):
        # Create a temporary screen for difficulty selection
        temp_screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Bomberman - Select Difficulty")
        
        while True:
            temp_screen.fill(BLACK)
            
            # Draw title
            title = self.big_font.render("Select Difficulty", True, WHITE)
            temp_screen.blit(title, (400 - title.get_width()//2, 100))
            
            # Draw buttons
            easy_btn = pygame.Rect(300, 200, 200, 50)
            normal_btn = pygame.Rect(300, 300, 200, 50)
            hard_btn = pygame.Rect(300, 400, 200, 50)
            
            pygame.draw.rect(temp_screen, GREEN, easy_btn)
            pygame.draw.rect(temp_screen, YELLOW, normal_btn)
            pygame.draw.rect(temp_screen, RED, hard_btn)
            
            easy_text = self.font.render("Easy", True, BLACK)
            normal_text = self.font.render("Normal", True, BLACK)
            hard_text = self.font.render("Hard", True, BLACK)
            
            temp_screen.blit(easy_text, (400 - easy_text.get_width()//2, 215))
            temp_screen.blit(normal_text, (400 - normal_text.get_width()//2, 315))
            temp_screen.blit(hard_text, (400 - hard_text.get_width()//2, 415))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    if easy_btn.collidepoint(mouse_pos):
                        self.difficulty = Difficulty.EASY
                        self.start_game()
                        return
                    elif normal_btn.collidepoint(mouse_pos):
                        self.difficulty = Difficulty.NORMAL
                        self.start_game()
                        return
                    elif hard_btn.collidepoint(mouse_pos):
                        self.difficulty = Difficulty.HARD
                        self.start_game()
                        return
    
    def start_game(self):
        # Set up game based on difficulty
        self.grid_size = self.difficulty["size"]
        screen_size = self.grid_size * TILE_SIZE
        self.screen = pygame.display.set_mode((screen_size, screen_size + 60))  # Extra space for UI
        pygame.display.set_caption("Bomberman")
        
        # Initialize grid
        self.init_grid()
        
        # Create player
        self.player = Player(1, 1, self.player_img)
        
        # Create enemies
        self.create_enemies()
        
        # Start game loop
        self.game_loop()
    
    def init_grid(self):
        self.grid = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.walls = []
        self.destructible_walls = []
        self.skills = []
        
        # Place indestructible walls (border and pattern)
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                # Border walls
                if x == 0 or y == 0 or x == self.grid_size - 1 or y == self.grid_size - 1:
                    self.grid[y][x] = 1
                    self.walls.append((x, y))
                # Pattern walls (every other tile)
                elif x % 2 == 0 and y % 2 == 0:
                    self.grid[y][x] = 1
                    self.walls.append((x, y))
        
        # Place destructible walls
        wall_count = int(self.grid_size * self.grid_size * self.difficulty["walls_percent"])
        placed = 0
        
        while placed < wall_count:
            x = random.randint(1, self.grid_size - 2)
            y = random.randint(1, self.grid_size - 2)
            
            # Skip if already a wall or too close to player start
            if self.grid[y][x] != 0 or (x <= 2 and y <= 2):
                continue
            
            self.grid[y][x] = 2  # 2 = destructible wall
            self.destructible_walls.append((x, y))
            placed += 1
        
        # Place skill bombs
        for _ in range(self.difficulty["skills_count"]):
            while True:
                x = random.randint(1, self.grid_size - 2)
                y = random.randint(1, self.grid_size - 2)
                
                if self.grid[y][x] == 2:  # Only place under destructible walls
                    bomb_type = random.choice(list(BombType))
                    self.skills.append({"pos": (x, y), "type": bomb_type})
                    break
    
    def create_enemies(self):
        self.enemies = []
        
        for _ in range(self.difficulty["enemies"]):
            while True:
                x = random.randint(3, self.grid_size - 2)
                y = random.randint(3, self.grid_size - 2)
                
                if self.grid[y][x] == 0:  # Empty space
                    self.enemies.append(Enemy(x, y, self.enemy_img))
                    break
    
    def game_loop(self):
        while self.running:
            self.clock.tick(FPS)
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if not self.game_over:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            self.player.move(0, -1, self)
                        elif event.key == pygame.K_DOWN:
                            self.player.move(0, 1, self)
                        elif event.key == pygame.K_LEFT:
                            self.player.move(-1, 0, self)
                        elif event.key == pygame.K_RIGHT:
                            self.player.move(1, 0, self)
                        elif event.key == pygame.K_SPACE:
                            self.player.place_bomb(self)
                        elif event.key == pygame.K_TAB:
                            self.player.switch_bomb_type()
                else:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                        self.show_difficulty_selection()
            
            # Update game state
            self.update()
            
            # Render
            self.render()
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()
    
    def update(self):
        if self.game_over:
            return
        
        # Update bombs
        for bomb in self.bombs[:]:
            bomb.update()
            if bomb.exploded:
                self.explode_bomb(bomb)
                self.bombs.remove(bomb)
        
        # Update explosions
        for explosion in self.explosions[:]:
            explosion.update()
            if explosion.finished:
                self.explosions.remove(explosion)
        
        # Update enemies
        for enemy in self.enemies[:]:
            if random.random() < 0.1:  # 10% chance to move each frame
                enemy.move_random(self)
            
            # Check collision with player
            if enemy.x == self.player.x and enemy.y == self.player.y:
                self.player.hit()
                if self.player.lives <= 0:
                    self.game_over = True
        
        # Check for skill pickups
        for skill in self.skills[:]:
            if skill["pos"] == (self.player.x, self.player.y):
                self.player.bomb_types.append(skill["type"])
                self.player.current_bomb_type = skill["type"]
                self.skills.remove(skill)
                self.score += 50
    
    def explode_bomb(self, bomb):
        # Create explosion at bomb position
        self.explosions.append(Explosion(bomb.x, bomb.y, self.explosion_img))
        
        # Get explosion range based on bomb type
        explosion_range = 4 if bomb.bomb_type == BombType.MEGA else 2
        
        # Create explosions in four directions
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        
        for dx, dy in directions:
            for i in range(1, explosion_range + 1):
                x, y = bomb.x + (dx * i), bomb.y + (dy * i)
                
                # Stop at grid boundaries
                if x < 0 or x >= self.grid_size or y < 0 or y >= self.grid_size:
                    break
                
                # Stop at indestructible walls
                if self.grid[y][x] == 1:
                    break
                
                # Destroy destructible walls
                if self.grid[y][x] == 2:
                    self.grid[y][x] = 0
                    if (x, y) in self.destructible_walls:
                        self.destructible_walls.remove((x, y))
                        self.score += 10
                        
                        # Check if there's a skill bomb here
                        for skill in self.skills[:]:
                            if skill["pos"] == (x, y):
                                # Skill is now visible
                                pass
                    
                    # Create explosion here and stop in this direction
                    self.explosions.append(Explosion(x, y, self.explosion_img))
                    break
                
                # Create explosion in empty space
                self.explosions.append(Explosion(x, y, self.explosion_img))
                
                # Check if explosion hits player
                if x == self.player.x and y == self.player.y:
                    self.player.hit()
                    if self.player.lives <= 0:
                        self.game_over = True
                
                # Check if explosion hits enemies
                for enemy in self.enemies[:]:
                    if x == enemy.x and y == enemy.y:
                        if bomb.bomb_type == BombType.ICE:
                            enemy.freeze()
                        else:
                            self.enemies.remove(enemy)
                            self.score += 100
        
        # Check if all enemies are defeated
        if len(self.enemies) == 0:
            self.score += 500  # Bonus for clearing the level
            self.init_grid()
            self.create_enemies()
    
    def render(self):
        self.screen.fill(BLACK)
        
        # Draw grid
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                
                # Draw tile based on grid value
                if self.grid[y][x] == 0:  # Empty
                    self.screen.blit(self.empty_img, rect)
                elif self.grid[y][x] == 1:  # Wall
                    self.screen.blit(self.wall_img, rect)
                elif self.grid[y][x] == 2:  # Destructible wall
                    self.screen.blit(self.destructible_wall_img, rect)
        
        # Draw skill bombs
        for skill in self.skills:
            x, y = skill["pos"]
            if self.grid[y][x] == 0:  # Only draw if not hidden under a wall
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if skill["type"] == BombType.FIRE:
                    self.screen.blit(self.fire_bomb_img, rect)
                elif skill["type"] == BombType.ICE:
                    self.screen.blit(self.ice_bomb_img, rect)
                elif skill["type"] == BombType.MEGA:
                    self.screen.blit(self.mega_bomb_img, rect)
        
        # Draw bombs
        for bomb in self.bombs:
            bomb.draw(self.screen)
        
        # Draw explosions
        for explosion in self.explosions:
            explosion.draw(self.screen)
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw UI
        ui_rect = pygame.Rect(0, self.grid_size * TILE_SIZE, self.grid_size * TILE_SIZE, 60)
        pygame.draw.rect(self.screen, GRAY, ui_rect)
        
        # Draw lives
        for i in range(self.player.lives):
            self.screen.blit(self.heart_img, (10 + i * 30, self.grid_size * TILE_SIZE + 15))
        
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (150, self.grid_size * TILE_SIZE + 15))
        
        # Draw current bomb type
        bomb_type_text = self.font.render(f"Bomb: {self.player.current_bomb_type.name}", True, WHITE)
        self.screen.blit(bomb_type_text, (300, self.grid_size * TILE_SIZE + 15))
        
        # Draw game over message if needed
        if self.game_over:
            overlay = pygame.Surface((self.grid_size * TILE_SIZE, self.grid_size * TILE_SIZE))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.big_font.render("GAME OVER", True, RED)
            restart_text = self.font.render("Press R to restart", True, WHITE)
            
            self.screen.blit(game_over_text, 
                            (self.grid_size * TILE_SIZE // 2 - game_over_text.get_width() // 2, 
                             self.grid_size * TILE_SIZE // 2 - 50))
            self.screen.blit(restart_text, 
                            (self.grid_size * TILE_SIZE // 2 - restart_text.get_width() // 2, 
                             self.grid_size * TILE_SIZE // 2 + 20))

# Player class
class Player:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
        self.lives = 3
        self.bomb_types = [BombType.FIRE]  # Start with fire bomb
        self.current_bomb_type = BombType.FIRE
    
    def move(self, dx, dy, game):
        new_x, new_y = self.x + dx, self.y + dy
        
        # Check if the new position is valid
        if (0 <= new_x < game.grid_size and 
            0 <= new_y < game.grid_size and 
            game.grid[new_y][new_x] == 0 and
            not any(bomb.x == new_x and bomb.y == new_y for bomb in game.bombs)):
            self.x, self.y = new_x, new_y
    
    def place_bomb(self, game):
        # Check if there's already a bomb at this position
        if any(bomb.x == self.x and bomb.y == self.y for bomb in game.bombs):
            return
        
        # Create bomb based on current type
        if self.current_bomb_type == BombType.FIRE:
            bomb = Bomb(self.x, self.y, game.fire_bomb_img, BombType.FIRE)
        elif self.current_bomb_type == BombType.ICE:
            bomb = Bomb(self.x, self.y, game.ice_bomb_img, BombType.ICE)
        elif self.current_bomb_type == BombType.MEGA:
            bomb = Bomb(self.x, self.y, game.mega_bomb_img, BombType.MEGA)
        
        game.bombs.append(bomb)
    
    def switch_bomb_type(self):
        if len(self.bomb_types) > 1:
            current_index = self.bomb_types.index(self.current_bomb_type)
            next_index = (current_index + 1) % len(self.bomb_types)
            self.current_bomb_type = self.bomb_types[next_index]
    
    def hit(self):
        self.lives -= 1
    
    def draw(self, screen):
        screen.blit(self.image, (self.x * TILE_SIZE, self.y * TILE_SIZE))

# Enemy class
class Enemy:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
        self.frozen = 0  # Frames the enemy is frozen
    
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
                game.grid[new_y][new_x] == 0 and
                not any(bomb.x == new_x and bomb.y == new_y for bomb in game.bombs)):
                self.x, self.y = new_x, new_y
                break
    
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

# Bomb class
class Bomb:
    def __init__(self, x, y, image, bomb_type):
        self.x = x
        self.y = y
        self.image = image
        self.bomb_type = bomb_type
        self.timer = 120  # 2 seconds at 60 FPS
        self.exploded = False
    
    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.exploded = True
    
    def draw(self, screen):
        # Make bomb pulse as timer gets low
        scale = 1.0
        if self.timer < 60:
            scale = 0.8 + 0.4 * (1 - (self.timer / 60))
        
        scaled_size = int(TILE_SIZE * scale)
        offset = (TILE_SIZE - scaled_size) // 2
        
        scaled_img = pygame.transform.scale(self.image, (scaled_size, scaled_size))
        screen.blit(scaled_img, (self.x * TILE_SIZE + offset, self.y * TILE_SIZE + offset))

# Explosion class
class Explosion:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
        self.timer = 30  # 0.5 seconds at 60 FPS
        self.finished = False
    
    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.finished = True
    
    def draw(self, screen):
        # Make explosion fade out
        alpha = int(255 * (self.timer / 30))
        img_copy = self.image.copy()
        img_copy.set_alpha(alpha)
        screen.blit(img_copy, (self.x * TILE_SIZE, self.y * TILE_SIZE))

# Run the game
if __name__ == "__main__":
    game = BombermanGame()