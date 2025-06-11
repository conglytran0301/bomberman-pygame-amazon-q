"""
Main game controller for Bomberman
"""
import pygame
import sys
import os
import random
from .constants import *
from .sprites import Player, Enemy, Bomb, Explosion
from .map import Map
from .assets import GameAssets
from .config import GameConfig
from .settings_menu import SettingsMenu
from .powerups import PowerUpManager, PowerUpType
from .screen_utils import get_optimal_screen_size, center_window, calculate_tile_size, create_screen
from .fullscreen_handler import FullscreenHandler
from .enemy_ai import EnemyAI

class GameController:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Robot Bomberman")
        
        # Get optimal screen size for laptop displays
        optimal_size = get_optimal_screen_size()
        self.screen_width = optimal_size[0]
        self.screen_height = optimal_size[1]
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False
        self.paused = False
        self.debug_mode = False  # Toggle for debug overlay
        self.changing_difficulty = False  # Flag for difficulty change menu
        self.show_settings = False  # Flag for settings menu
        
        # Initialize fullscreen handler
        from .fullscreen_handler import FullscreenHandler
        self.fullscreen_handler = FullscreenHandler(self)
        
        # Load configuration
        self.config = GameConfig()
        
        # Initialize settings menu
        self.settings_menu = SettingsMenu(self)
        
        # Load assets
        self.assets = GameAssets()
        
        # Initialize power-up manager
        from .powerups import PowerUpManager
        self.powerup_manager = PowerUpManager(self.assets)
        
        # Initialize fonts - use more modern fonts if available
        font_size_factor = min(1.0, self.screen_width / 1366)  # Scale font based on screen width
        try:
            self.font = pygame.font.SysFont('Segoe UI', int(24 * font_size_factor))
            self.small_font = pygame.font.SysFont('Segoe UI', int(12 * font_size_factor))
            self.big_font = pygame.font.SysFont('Segoe UI', int(48 * font_size_factor))
        except:
            # Fallback to Arial if Segoe UI not available
            self.font = pygame.font.SysFont('Arial', int(24 * font_size_factor))
            self.small_font = pygame.font.SysFont('Arial', int(12 * font_size_factor))
            self.big_font = pygame.font.SysFont('Arial', int(48 * font_size_factor))
        
        # Start with difficulty selection
        self.show_difficulty_selection()
    
    def show_difficulty_selection(self, in_game=False):
        """Show difficulty selection screen"""
        # Create a screen for difficulty selection
        if in_game:
            # Use existing screen if changing difficulty during gameplay
            temp_screen = self.screen
            self.changing_difficulty = True
        else:
            # Use optimal size for laptop screens
            width = min(800, int(self.screen_width * 0.8))
            height = min(600, int(self.screen_height * 0.8))
            
            # Create centered screen
            temp_screen = create_screen(width, height)
        
        selection_active = True
        while selection_active:
            temp_screen.fill(BLACK)
            
            # Draw title
            title = self.big_font.render("Bomberman", True, WHITE)
            subtitle = self.font.render("Select Difficulty", True, WHITE)
            
            # Center horizontally
            center_x = temp_screen.get_width() // 2
            temp_screen.blit(title, (center_x - title.get_width()//2, 100))
            temp_screen.blit(subtitle, (center_x - subtitle.get_width()//2, 160))
            
            # Draw buttons - scale based on screen size
            button_width = min(200, int(temp_screen.get_width() * 0.3))
            button_height = 50
            button_x = center_x - button_width // 2
            
            easy_btn = pygame.Rect(button_x, 250, button_width, button_height)
            normal_btn = pygame.Rect(button_x, 320, button_width, button_height)
            hard_btn = pygame.Rect(button_x, 390, button_width, button_height)
            
            pygame.draw.rect(temp_screen, GREEN, easy_btn)
            pygame.draw.rect(temp_screen, YELLOW, normal_btn)
            pygame.draw.rect(temp_screen, RED, hard_btn)
            
            easy_text = self.font.render("Easy", True, BLACK)
            normal_text = self.font.render("Normal", True, BLACK)
            hard_text = self.font.render("Hard", True, BLACK)
            
            temp_screen.blit(easy_text, (center_x - easy_text.get_width()//2, 265))
            temp_screen.blit(normal_text, (center_x - normal_text.get_width()//2, 335))
            temp_screen.blit(hard_text, (center_x - hard_text.get_width()//2, 405))
            
            # Draw difficulty details
            easy_details = self.small_font.render("15x15 grid, 3 enemies", True, WHITE)
            normal_details = self.small_font.render("20x20 grid, 5 enemies", True, WHITE)
            hard_details = self.small_font.render("25x25 grid, 8 enemies", True, WHITE)
            
            temp_screen.blit(easy_details, (center_x - easy_details.get_width()//2, 300))
            temp_screen.blit(normal_details, (center_x - normal_details.get_width()//2, 370))
            temp_screen.blit(hard_details, (center_x - hard_details.get_width()//2, 440))
            
            # Add back button if changing difficulty during gameplay
            if in_game:
                back_btn = pygame.Rect(button_x, 460, button_width, button_height)
                pygame.draw.rect(temp_screen, GRAY, back_btn)
                back_text = self.font.render("Back to Game", True, BLACK)
                temp_screen.blit(back_text, (center_x - back_text.get_width()//2, 475))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and in_game:
                        self.changing_difficulty = False
                        selection_active = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    if easy_btn.collidepoint(mouse_pos):
                        if in_game:
                            self.changing_difficulty = False
                            self.start_game(Difficulty.EASY)
                        else:
                            self.start_game(Difficulty.EASY)
                        selection_active = False
                    elif normal_btn.collidepoint(mouse_pos):
                        if in_game:
                            self.changing_difficulty = False
                            self.start_game(Difficulty.NORMAL)
                        else:
                            self.start_game(Difficulty.NORMAL)
                        selection_active = False
                    elif hard_btn.collidepoint(mouse_pos):
                        if in_game:
                            self.changing_difficulty = False
                            self.start_game(Difficulty.HARD)
                        else:
                            self.start_game(Difficulty.HARD)
                        selection_active = False
                    elif in_game and back_btn.collidepoint(mouse_pos):
                        self.changing_difficulty = False
                        selection_active = False
    
    def start_game(self, difficulty):
        """Initialize the game with the selected difficulty"""
        self.difficulty = difficulty
        self.grid_size = difficulty["size"]
        
        # UI height
        ui_height = 60
        
        # Calculate optimal tile size for the grid
        TILE_SIZE = calculate_tile_size(
            self.grid_size, 
            self.screen_width, 
            self.screen_height, 
            ui_height
        )
        
        # Update the global tile size
        globals()['TILE_SIZE'] = TILE_SIZE
        
        # Calculate actual screen dimensions
        screen_width = self.grid_size * TILE_SIZE
        screen_height = self.grid_size * TILE_SIZE + ui_height
        
        # Create centered screen with the calculated dimensions
        self.screen = create_screen(screen_width, screen_height)
        
        # Initialize game objects
        self.map = Map(difficulty, self.assets)
        self.grid = self.map.grid
        
        # Create player at starting position
        self.player = Player(1, 1, self.assets.player_img)
        
        # Create enemies
        self.enemies = []
        self.create_enemies()
        
        # Initialize other game objects
        self.bombs = []
        self.explosions = []
        self.score = 0
        self.game_over = False  # Reset game over state
        self.changing_difficulty = False
        
        # Start game loop
        self.game_loop()
    
    def create_enemies(self):
        """Create enemies based on difficulty"""
        self.enemies = []
        
        # Determine difficulty level for AI
        if self.difficulty == Difficulty.EASY:
            ai_difficulty = "EASY"
        elif self.difficulty == Difficulty.NORMAL:
            ai_difficulty = "NORMAL"
        else:
            ai_difficulty = "HARD"
        
        for _ in range(self.difficulty["enemies"]):
            x, y = self.map.get_valid_spawn_position()
            enemy = Enemy(x, y, self.assets.enemy_img)
            
            # Initialize AI for this enemy
            enemy.ai = EnemyAI(enemy, ai_difficulty)
            
            self.enemies.append(enemy)
    
    def game_loop(self):
        """Main game loop"""
        while self.running:
            self.clock.tick(FPS)
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.changing_difficulty:
                            self.changing_difficulty = False
                        else:
                            self.paused = not self.paused
                    elif event.key == pygame.K_F1:
                        self.debug_mode = not self.debug_mode
                    elif event.key == pygame.K_F11:
                        # Toggle fullscreen mode
                        self.fullscreen_handler.toggle_fullscreen()
                    elif event.key == pygame.K_d:
                        # Change difficulty when paused or game over
                        if self.paused or self.game_over:
                            self.show_difficulty_selection(in_game=True)
                    elif event.key == pygame.K_s:
                        # Show settings menu when paused or game over
                        if self.paused or self.game_over:
                            self.settings_menu.show()
                    elif event.key == pygame.K_r:
                        if self.game_over:
                            # Reset the game with the same difficulty
                            self.start_game(self.difficulty)
                            return
                    
                    # Handle Ctrl+D for difficulty change during gameplay
                    if event.key == pygame.K_d and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        self.show_difficulty_selection(in_game=True)
                    
                    if not self.paused and not self.game_over and not self.changing_difficulty:
                        if event.key == pygame.K_UP:
                            self.player.move(0, -1, self)
                        elif event.key == pygame.K_DOWN:
                            self.player.move(0, 1, self)
                        elif event.key == pygame.K_LEFT:
                            self.player.move(-1, 0, self)
                        elif event.key == pygame.K_RIGHT:
                            self.player.move(1, 0, self)
                        elif event.key == pygame.K_SPACE:
                            if self.player.place_bomb(self):
                                self.assets.play_sound("pickup")  # Use as bomb placement sound
                        elif event.key == pygame.K_TAB:
                            self.player.switch_bomb_type()
                        elif event.key == pygame.K_e:
                            # Detonate remote bombs if player has them
                            if self.player.detonate_remote_bombs(self):
                                self.assets.play_sound("pickup")
            
            # Skip updates if paused, game over, or changing difficulty
            if not self.paused and not self.game_over and not self.changing_difficulty:
                self.update()
            
            # Render
            self.render()
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()
    
    def update(self):
        """Update game state"""
        # Update player status effects
        self.player.update()
        
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
        
        # Update power-ups
        self.powerup_manager.update()
        
        # Update enemies
        for enemy in self.enemies[:]:
            # Use advanced AI instead of random movement
            if enemy.ai:
                enemy.ai.update(self)
            else:
                # Fallback to old behavior if AI not initialized
                if random.random() < 0.05:  # 5% chance to move each frame
                    enemy.move_random(self)
                enemy.try_place_bomb(self)
            
            # No collision with player - they can pass through each other
        
        # Check for skill pickups
        for skill in self.map.skills[:]:
            if skill.x == self.player.x and skill.y == self.player.y and self.grid[skill.y][skill.x] == EMPTY:
                if skill.bomb_type not in self.player.bomb_types:
                    self.player.bomb_types.append(skill.bomb_type)
                self.player.current_bomb_type = skill.bomb_type
                self.map.skills.remove(skill)
                self.score += 50
                self.assets.play_sound("pickup")
        
        # Check if player is on an explosion
        for explosion in self.explosions:
            if explosion.x == self.player.x and explosion.y == self.player.y:
                if self.player.hit():
                    self.game_over = True
    
    def explode_bomb(self, bomb):
        """Handle bomb explosion"""
        # Create explosion at bomb position with appropriate image based on bomb type
        if bomb.bomb_type == BombType.FIRE:
            explosion_img = self.assets.fire_explosion_img
        elif bomb.bomb_type == BombType.ICE:
            explosion_img = self.assets.ice_explosion_img
        elif bomb.bomb_type == BombType.MEGA:
            explosion_img = self.assets.mega_explosion_img
        else:
            explosion_img = self.assets.explosion_img
            
        self.explosions.append(Explosion(bomb.x, bomb.y, explosion_img))
        
        # Get explosion range based on bomb type and bomb range
        base_range = 4 if bomb.bomb_type == BombType.MEGA else 2
        explosion_range = bomb.range if hasattr(bomb, 'range') else base_range
        
        # Create explosions in four directions
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        
        # Track if this bomb hit the player (for AI tracking)
        hit_player = False
        
        for dx, dy in directions:
            for i in range(1, explosion_range + 1):
                x, y = bomb.x + (dx * i), bomb.y + (dy * i)
                
                # Stop at grid boundaries
                if x < 0 or x >= self.grid_size or y < 0 or y >= self.grid_size:
                    break
                
                # Stop at indestructible walls
                if self.grid[y][x] == WALL:
                    break
                
                # Destroy destructible walls
                if self.grid[y][x] == DESTRUCTIBLE:
                    self.grid[y][x] = EMPTY
                    self.score += 10
                    
                    # Create explosion here with appropriate image based on bomb type
                    if bomb.bomb_type == BombType.FIRE:
                        explosion_img = self.assets.fire_explosion_img
                    elif bomb.bomb_type == BombType.ICE:
                        explosion_img = self.assets.ice_explosion_img
                    elif bomb.bomb_type == BombType.MEGA:
                        explosion_img = self.assets.mega_explosion_img
                    else:
                        explosion_img = self.assets.explosion_img
                        
                    self.explosions.append(Explosion(x, y, explosion_img))
                    
                    # Chance to spawn power-up (20%)
                    if random.random() < 0.2:
                        self.powerup_manager.create_powerup(x, y)
                    
                    break
                
                # Create explosion in empty space with appropriate image based on bomb type
                if bomb.bomb_type == BombType.FIRE:
                    explosion_img = self.assets.fire_explosion_img
                elif bomb.bomb_type == BombType.ICE:
                    explosion_img = self.assets.ice_explosion_img
                elif bomb.bomb_type == BombType.MEGA:
                    explosion_img = self.assets.mega_explosion_img
                else:
                    explosion_img = self.assets.explosion_img
                    
                self.explosions.append(Explosion(x, y, explosion_img))
                
                # Check if explosion hits player
                if x == self.player.x and y == self.player.y:
                    # Get damage and effect based on bomb type
                    damage = BOMB_DAMAGE.get(bomb.bomb_type, 1)
                    effect = BOMB_EFFECTS.get(bomb.bomb_type, None)
                    
                    # Track if this bomb hit the player (for AI tracking)
                    hit_player = True
                    
                    if self.player.hit(damage, effect):
                        self.game_over = True
                
                # Check if explosion hits enemies
                for enemy in self.enemies[:]:
                    if x == enemy.x and y == enemy.y:
                        if bomb.bomb_type == BombType.ICE:
                            enemy.freeze()
                        else:
                            self.enemies.remove(enemy)
                            self.score += 100
        
        # Update AI tracking for enemy bombs
        if isinstance(bomb.owner, Enemy) and hasattr(bomb.owner, 'ai'):
            bomb.owner.ai.bombs_placed += 1
            if hit_player:
                bomb.owner.ai.successful_hits += 1
        
        # Play explosion sound
        self.assets.play_sound("explosion")
        
        # Check if all enemies are defeated
        if len(self.enemies) == 0:
            self.score += 500  # Bonus for clearing the level
            self.map.generate_map()
            self.grid = self.map.grid
            self.create_enemies()
    
    def render(self):
        """Render the game"""
        self.screen.fill(BLACK)
        
        # Draw map
        self.map.draw(self.screen)
        
        # Draw power-ups
        self.powerup_manager.draw(self.screen)
        
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
        
        # Draw debug overlay if enabled
        if self.debug_mode:
            self.map.draw_debug_overlay(self.screen, self.small_font)
        
        # Draw UI
        self.render_ui()
        
        # Draw pause or game over overlay if needed
        if self.paused:
            self.render_pause_overlay()
        elif self.game_over:
            self.render_game_over_overlay()
        elif self.changing_difficulty:
            # This is handled in show_difficulty_selection with in_game=True
            pass
    
    def render_ui(self):
        """Render the game UI"""
        ui_rect = pygame.Rect(0, self.grid_size * TILE_SIZE, self.grid_size * TILE_SIZE, 60)
        pygame.draw.rect(self.screen, GRAY, ui_rect)
        
        # Draw lives
        for i in range(self.player.lives):
            self.screen.blit(self.assets.heart_img, (10 + i * 30, self.grid_size * TILE_SIZE + 15))
            
        # Draw health bar
        health_x = 10 + self.player.lives * 30 + 10
        health_y = self.grid_size * TILE_SIZE + 15
        health_segment_width = self.assets.health_segment_img.get_width()
        
        # Draw health segments
        for i in range(5):  # Max 5 health
            if i < self.player.health:
                # Full health segment
                self.screen.blit(self.assets.health_segment_img, (health_x + i * health_segment_width, health_y))
            else:
                # Empty health segment (gray)
                empty_segment = self.assets.health_segment_img.copy()
                empty_segment.fill((100, 100, 100, 255), special_flags=pygame.BLEND_RGBA_MULT)
                self.screen.blit(empty_segment, (health_x + i * health_segment_width, health_y))
        
        # Calculate UI positions based on screen width
        ui_width = self.grid_size * TILE_SIZE
        
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, self.grid_size * TILE_SIZE + 15))
        
        # Draw current bomb type with colored indicator
        bomb_type = self.player.current_bomb_type
        bomb_color = RED if bomb_type == BombType.FIRE else CYAN if bomb_type == BombType.ICE else PURPLE
        bomb_type_text = self.font.render(f"Bomb: {bomb_type.name}", True, bomb_color)
        bomb_x = ui_width // 4
        self.screen.blit(bomb_type_text, (bomb_x, self.grid_size * TILE_SIZE + 15))
        
        # Draw power-up indicators
        power_y = self.grid_size * TILE_SIZE + 40
        
        # Calculate positions for power-up indicators
        col1_x = 10
        col2_x = ui_width // 4
        col3_x = ui_width // 2
        col4_x = (ui_width * 3) // 4
        
        # Speed boost indicator
        if self.player.speed_boost > 0:
            speed_text = self.small_font.render(f"Speed: {self.player.speed_boost//60}s", True, NEON_BLUE)
            self.screen.blit(speed_text, (col1_x, power_y))
        elif self.player.speed_boost < 0:
            # Slow effect
            slow_text = self.small_font.render(f"Slowed: {abs(self.player.speed_boost)//60}s", True, (150, 220, 255))
            self.screen.blit(slow_text, (col1_x, power_y))
        
        # Shield indicator
        if self.player.shield:
            shield_text = self.small_font.render(f"Shield: {self.player.shield_time//60}s", True, TECH_SILVER)
            self.screen.blit(shield_text, (col2_x, power_y))
        
        # Armor indicator
        if self.player.armor > 0:
            armor_text = self.small_font.render(f"Armor: {self.player.armor} ({self.player.armor_time//60}s)", True, TECH_GOLD)
            self.screen.blit(armor_text, (col2_x + 120, power_y))
        
        # Ice immunity indicator
        if self.player.slow_immune > 0:
            immune_text = self.small_font.render(f"Ice Immune: {self.player.slow_immune//60}s", True, (0, 200, 255))
            self.screen.blit(immune_text, (col1_x + 120, power_y))
        
        # Remote bomb indicator
        if self.player.has_remote_bomb:
            remote_text = self.small_font.render(f"Remote Bombs: {len(self.player.remote_bombs)}", True, PURPLE)
            self.screen.blit(remote_text, (col3_x, power_y))
            
        # Bomb range indicator
        range_text = self.small_font.render(f"Range: {self.player.bomb_range}", True, ORANGE)
        self.screen.blit(range_text, (col3_x, self.grid_size * TILE_SIZE + 15))
        
        # Max bombs indicator
        bombs_text = self.small_font.render(f"Max Bombs: {self.player.max_bombs}", True, NEON_GREEN)
        self.screen.blit(bombs_text, (col4_x, self.grid_size * TILE_SIZE + 15))
        
        # Calculate UI positions based on screen width
        ui_width = self.grid_size * TILE_SIZE
        
        # Draw enemies left
        enemies_text = self.font.render(f"Enemies: {len(self.enemies)}", True, WHITE)
        self.screen.blit(enemies_text, ((ui_width * 3) // 4, self.grid_size * TILE_SIZE + 40))
        
        # Draw current difficulty
        diff_name = "Easy" if self.difficulty == Difficulty.EASY else "Normal" if self.difficulty == Difficulty.NORMAL else "Hard"
        diff_text = self.small_font.render(f"Diff: {diff_name}", True, WHITE)
        self.screen.blit(diff_text, (ui_width - 100, self.grid_size * TILE_SIZE + 15))
        
        # Draw settings button
        settings_text = self.small_font.render("Settings (S)", True, WHITE)
        self.screen.blit(settings_text, (ui_width - 100, self.grid_size * TILE_SIZE + 40))
        
        # Draw debug mode indicator
        if self.debug_mode:
            debug_text = self.small_font.render("DEBUG MODE (F1)", True, YELLOW)
            self.screen.blit(debug_text, (10, self.grid_size * TILE_SIZE + 40))
    
    def render_pause_overlay(self):
        """Render pause screen overlay"""
        overlay = pygame.Surface((self.grid_size * TILE_SIZE, self.grid_size * TILE_SIZE))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        pause_text = self.big_font.render("PAUSED", True, WHITE)
        resume_text = self.font.render("Press ESC to resume", True, WHITE)
        diff_text = self.font.render("Press D to change difficulty", True, WHITE)
        settings_text = self.font.render("Press S for settings", True, WHITE)
        
        center_x = self.grid_size * TILE_SIZE // 2
        self.screen.blit(pause_text, 
                        (center_x - pause_text.get_width() // 2, 
                         self.grid_size * TILE_SIZE // 2 - 100))
        self.screen.blit(resume_text, 
                        (center_x - resume_text.get_width() // 2, 
                         self.grid_size * TILE_SIZE // 2 - 40))
        self.screen.blit(diff_text, 
                        (center_x - diff_text.get_width() // 2, 
                         self.grid_size * TILE_SIZE // 2))
        self.screen.blit(settings_text, 
                        (center_x - settings_text.get_width() // 2, 
                         self.grid_size * TILE_SIZE // 2 + 40))
    
    def render_game_over_overlay(self):
        """Render game over screen overlay"""
        overlay = pygame.Surface((self.grid_size * TILE_SIZE, self.grid_size * TILE_SIZE))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.big_font.render("GAME OVER", True, RED)
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        restart_text = self.font.render("Press R to restart", True, WHITE)
        diff_text = self.font.render("Press D to change difficulty", True, WHITE)
        settings_text = self.font.render("Press S for settings", True, WHITE)
        
        center_x = self.grid_size * TILE_SIZE // 2
        self.screen.blit(game_over_text, 
                        (center_x - game_over_text.get_width() // 2, 
                         self.grid_size * TILE_SIZE // 2 - 120))
        self.screen.blit(score_text, 
                        (center_x - score_text.get_width() // 2, 
                         self.grid_size * TILE_SIZE // 2 - 60))
        self.screen.blit(restart_text, 
                        (center_x - restart_text.get_width() // 2, 
                         self.grid_size * TILE_SIZE // 2 - 20))
        self.screen.blit(diff_text, 
                        (center_x - diff_text.get_width() // 2, 
                         self.grid_size * TILE_SIZE // 2 + 20))
        self.screen.blit(settings_text, 
                        (center_x - settings_text.get_width() // 2, 
                         self.grid_size * TILE_SIZE // 2 + 60))