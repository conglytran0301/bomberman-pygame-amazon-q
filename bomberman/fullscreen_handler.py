"""
Fullscreen handling for Bomberman game
"""
import pygame
from .screen_utils import calculate_tile_size

class FullscreenHandler:
    def __init__(self, game):
        self.game = game
        self.is_fullscreen = False
        self.windowed_size = None
        
    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode"""
        if self.is_fullscreen:
            # Switch back to windowed mode
            self.is_fullscreen = False
            if self.windowed_size:
                width, height = self.windowed_size
                self.game.screen = pygame.display.set_mode((width, height))
        else:
            # Switch to fullscreen mode
            self.is_fullscreen = True
            # Save current window size
            self.windowed_size = (self.game.screen.get_width(), self.game.screen.get_height())
            # Set fullscreen mode
            self.game.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            
        # Recalculate tile size and update game elements
        self.update_game_scale()
        
        return self.is_fullscreen
    
    def update_game_scale(self):
        """Update game scale based on current screen size"""
        # Get current screen dimensions
        screen_width = self.game.screen.get_width()
        screen_height = self.game.screen.get_height()
        
        # UI height
        ui_height = 60
        
        # Calculate new tile size
        new_tile_size = calculate_tile_size(
            self.game.grid_size,
            screen_width,
            screen_height,
            ui_height
        )
        
        # Update global tile size
        globals()['TILE_SIZE'] = new_tile_size
        
        # Reload assets if needed
        # In a full implementation, you might want to regenerate assets based on new tile size
        # self.game.assets = GameAssets()