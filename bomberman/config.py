"""
Configuration settings for the Bomberman game
"""
from .constants import GRAPHICS_QUALITY

class GameConfig:
    def __init__(self):
        # Graphics settings
        self.graphics_quality = "MEDIUM"  # LOW, MEDIUM, HIGH
        self.fullscreen = False
        self.show_fps = False
        self.vsync = True
        
        # Sound settings
        self.sound_enabled = True
        self.music_volume = 0.7
        self.sfx_volume = 0.8
        
        # Game settings
        self.robot_theme = True  # Enable robot theme
        self.particle_effects = True
        self.screen_shake = True
        
    def set_graphics_quality(self, quality):
        """Set graphics quality level"""
        if quality in GRAPHICS_QUALITY:
            self.graphics_quality = quality
            return True
        return False
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        self.fullscreen = not self.fullscreen
        # In a real implementation, this would actually toggle fullscreen
        # But we're using the FullscreenHandler class for that
        return self.fullscreen
    
    def toggle_robot_theme(self):
        """Toggle robot theme"""
        self.robot_theme = not self.robot_theme
        return self.robot_theme
    
    def toggle_particle_effects(self):
        """Toggle particle effects"""
        self.particle_effects = not self.particle_effects
        return self.particle_effects
    
    def get_current_quality_settings(self):
        """Get current quality settings"""
        return GRAPHICS_QUALITY[self.graphics_quality]
    
    def save_config(self):
        """Save configuration to file (placeholder)"""
        # In a real implementation, this would save to a file
        print("Configuration saved")
        
    def load_config(self):
        """Load configuration from file (placeholder)"""
        # In a real implementation, this would load from a file
        print("Configuration loaded")