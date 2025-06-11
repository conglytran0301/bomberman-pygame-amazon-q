"""
Settings menu for the Bomberman game
"""
import pygame
from .constants import *

class SettingsMenu:
    def __init__(self, game):
        self.game = game
        self.active = False
        self.current_tab = "Graphics"  # Graphics, Sound, Game
        
    def show(self):
        """Display the settings menu"""
        self.active = True
        
        # Create a surface for the settings menu
        menu_width = int(self.game.screen.get_width() * 0.8)
        menu_height = int(self.game.screen.get_height() * 0.8)
        menu_x = (self.game.screen.get_width() - menu_width) // 2
        menu_y = (self.game.screen.get_height() - menu_height) // 2
        
        menu_surface = pygame.Surface((menu_width, menu_height))
        menu_surface.fill((40, 40, 50))
        
        # Draw border
        pygame.draw.rect(menu_surface, TECH_SILVER, (0, 0, menu_width, menu_height), 2)
        
        # Draw title
        title = self.game.big_font.render("Settings", True, WHITE)
        menu_surface.blit(title, (menu_width//2 - title.get_width()//2, 20))
        
        # Draw tabs
        tab_width = menu_width // 3
        tab_height = 40
        tab_y = 80
        
        tabs = ["Graphics", "Sound", "Game"]
        for i, tab in enumerate(tabs):
            tab_x = i * tab_width
            tab_rect = pygame.Rect(tab_x, tab_y, tab_width, tab_height)
            
            # Highlight current tab
            if tab == self.current_tab:
                pygame.draw.rect(menu_surface, TECH_BLUE, tab_rect)
            else:
                pygame.draw.rect(menu_surface, GRAY, tab_rect)
            
            pygame.draw.rect(menu_surface, WHITE, tab_rect, 1)
            tab_text = self.game.font.render(tab, True, WHITE)
            menu_surface.blit(tab_text, (tab_x + tab_width//2 - tab_text.get_width()//2, 
                                         tab_y + tab_height//2 - tab_text.get_height()//2))
        
        # Draw settings based on current tab
        content_y = tab_y + tab_height + 20
        if self.current_tab == "Graphics":
            self.draw_graphics_settings(menu_surface, content_y)
        elif self.current_tab == "Sound":
            self.draw_sound_settings(menu_surface, content_y)
        elif self.current_tab == "Game":
            self.draw_game_settings(menu_surface, content_y)
        
        # Draw back button
        back_rect = pygame.Rect(menu_width//2 - 100, menu_height - 60, 200, 40)
        pygame.draw.rect(menu_surface, TECH_RED, back_rect)
        pygame.draw.rect(menu_surface, WHITE, back_rect, 1)
        back_text = self.game.font.render("Back", True, WHITE)
        menu_surface.blit(back_text, (menu_width//2 - back_text.get_width()//2, 
                                     menu_height - 60 + 20 - back_text.get_height()//2))
        
        # Blit menu to screen
        self.game.screen.blit(menu_surface, (menu_x, menu_y))
        pygame.display.flip()
        
        # Handle events
        waiting = True
        while waiting and self.active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.active = False
                        waiting = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    # Adjust mouse position relative to menu
                    rel_x = mouse_pos[0] - menu_x
                    rel_y = mouse_pos[1] - menu_y
                    
                    # Check if clicked on tabs
                    if tab_y <= rel_y <= tab_y + tab_height:
                        for i, tab in enumerate(tabs):
                            tab_x = i * tab_width
                            if tab_x <= rel_x <= tab_x + tab_width:
                                self.current_tab = tab
                                self.show()  # Refresh menu
                                return
                    
                    # Check if clicked on back button
                    if back_rect.collidepoint(rel_x, rel_y):
                        self.active = False
                        waiting = False
                    
                    # Handle settings interactions
                    if self.current_tab == "Graphics":
                        self.handle_graphics_click(rel_x, rel_y, content_y)
                    elif self.current_tab == "Sound":
                        self.handle_sound_click(rel_x, rel_y, content_y)
                    elif self.current_tab == "Game":
                        self.handle_game_click(rel_x, rel_y, content_y)
    
    def draw_graphics_settings(self, surface, start_y):
        """Draw graphics settings options"""
        width = surface.get_width()
        padding = 40
        option_height = 50
        
        # Quality setting
        y = start_y
        text = self.game.font.render("Graphics Quality:", True, WHITE)
        surface.blit(text, (padding, y))
        
        # Draw quality buttons
        button_width = 100
        button_spacing = 20
        button_x = width - padding - 3 * button_width - 2 * button_spacing
        
        qualities = ["LOW", "MEDIUM", "HIGH"]
        for i, quality in enumerate(qualities):
            btn_x = button_x + i * (button_width + button_spacing)
            btn_rect = pygame.Rect(btn_x, y, button_width, 30)
            
            # Highlight current setting
            if self.game.config.graphics_quality == quality:
                pygame.draw.rect(surface, TECH_BLUE, btn_rect)
            else:
                pygame.draw.rect(surface, GRAY, btn_rect)
            
            pygame.draw.rect(surface, WHITE, btn_rect, 1)
            q_text = self.game.font.render(quality, True, WHITE)
            surface.blit(q_text, (btn_x + button_width//2 - q_text.get_width()//2, 
                                 y + 15 - q_text.get_height()//2))
        
        # Fullscreen toggle
        y += option_height
        text = self.game.font.render("Fullscreen:", True, WHITE)
        surface.blit(text, (padding, y))
        
        toggle_rect = pygame.Rect(width - padding - 60, y, 60, 30)
        if self.game.config.fullscreen:
            pygame.draw.rect(surface, GREEN, toggle_rect)
            toggle_text = "ON"
        else:
            pygame.draw.rect(surface, RED, toggle_rect)
            toggle_text = "OFF"
        
        pygame.draw.rect(surface, WHITE, toggle_rect, 1)
        t_text = self.game.font.render(toggle_text, True, WHITE)
        surface.blit(t_text, (toggle_rect.centerx - t_text.get_width()//2, 
                             toggle_rect.centery - t_text.get_height()//2))
        
        # Show FPS toggle
        y += option_height
        text = self.game.font.render("Show FPS:", True, WHITE)
        surface.blit(text, (padding, y))
        
        toggle_rect = pygame.Rect(width - padding - 60, y, 60, 30)
        if self.game.config.show_fps:
            pygame.draw.rect(surface, GREEN, toggle_rect)
            toggle_text = "ON"
        else:
            pygame.draw.rect(surface, RED, toggle_rect)
            toggle_text = "OFF"
        
        pygame.draw.rect(surface, WHITE, toggle_rect, 1)
        t_text = self.game.font.render(toggle_text, True, WHITE)
        surface.blit(t_text, (toggle_rect.centerx - t_text.get_width()//2, 
                             toggle_rect.centery - t_text.get_height()//2))
        
        # VSync toggle
        y += option_height
        text = self.game.font.render("VSync:", True, WHITE)
        surface.blit(text, (padding, y))
        
        toggle_rect = pygame.Rect(width - padding - 60, y, 60, 30)
        if self.game.config.vsync:
            pygame.draw.rect(surface, GREEN, toggle_rect)
            toggle_text = "ON"
        else:
            pygame.draw.rect(surface, RED, toggle_rect)
            toggle_text = "OFF"
        
        pygame.draw.rect(surface, WHITE, toggle_rect, 1)
        t_text = self.game.font.render(toggle_text, True, WHITE)
        surface.blit(t_text, (toggle_rect.centerx - t_text.get_width()//2, 
                             toggle_rect.centery - t_text.get_height()//2))
    
    def draw_sound_settings(self, surface, start_y):
        """Draw sound settings options"""
        width = surface.get_width()
        padding = 40
        option_height = 50
        
        # Sound enabled toggle
        y = start_y
        text = self.game.font.render("Sound Enabled:", True, WHITE)
        surface.blit(text, (padding, y))
        
        toggle_rect = pygame.Rect(width - padding - 60, y, 60, 30)
        if self.game.config.sound_enabled:
            pygame.draw.rect(surface, GREEN, toggle_rect)
            toggle_text = "ON"
        else:
            pygame.draw.rect(surface, RED, toggle_rect)
            toggle_text = "OFF"
        
        pygame.draw.rect(surface, WHITE, toggle_rect, 1)
        t_text = self.game.font.render(toggle_text, True, WHITE)
        surface.blit(t_text, (toggle_rect.centerx - t_text.get_width()//2, 
                             toggle_rect.centery - t_text.get_height()//2))
        
        # Music volume slider
        y += option_height
        text = self.game.font.render("Music Volume:", True, WHITE)
        surface.blit(text, (padding, y))
        
        slider_width = 200
        slider_rect = pygame.Rect(width - padding - slider_width, y + 10, slider_width, 10)
        pygame.draw.rect(surface, GRAY, slider_rect)
        pygame.draw.rect(surface, WHITE, slider_rect, 1)
        
        # Draw slider position
        pos_x = slider_rect.x + int(slider_width * self.game.config.music_volume)
        pygame.draw.rect(surface, TECH_BLUE, (slider_rect.x, slider_rect.y, pos_x - slider_rect.x, slider_rect.height))
        pygame.draw.circle(surface, WHITE, (pos_x, slider_rect.y + slider_rect.height // 2), 8)
        
        # SFX volume slider
        y += option_height
        text = self.game.font.render("SFX Volume:", True, WHITE)
        surface.blit(text, (padding, y))
        
        slider_rect = pygame.Rect(width - padding - slider_width, y + 10, slider_width, 10)
        pygame.draw.rect(surface, GRAY, slider_rect)
        pygame.draw.rect(surface, WHITE, slider_rect, 1)
        
        # Draw slider position
        pos_x = slider_rect.x + int(slider_width * self.game.config.sfx_volume)
        pygame.draw.rect(surface, TECH_BLUE, (slider_rect.x, slider_rect.y, pos_x - slider_rect.x, slider_rect.height))
        pygame.draw.circle(surface, WHITE, (pos_x, slider_rect.y + slider_rect.height // 2), 8)
    
    def draw_game_settings(self, surface, start_y):
        """Draw game settings options"""
        width = surface.get_width()
        padding = 40
        option_height = 50
        
        # Robot theme toggle
        y = start_y
        text = self.game.font.render("Robot Theme:", True, WHITE)
        surface.blit(text, (padding, y))
        
        toggle_rect = pygame.Rect(width - padding - 60, y, 60, 30)
        if self.game.config.robot_theme:
            pygame.draw.rect(surface, GREEN, toggle_rect)
            toggle_text = "ON"
        else:
            pygame.draw.rect(surface, RED, toggle_rect)
            toggle_text = "OFF"
        
        pygame.draw.rect(surface, WHITE, toggle_rect, 1)
        t_text = self.game.font.render(toggle_text, True, WHITE)
        surface.blit(t_text, (toggle_rect.centerx - t_text.get_width()//2, 
                             toggle_rect.centery - t_text.get_height()//2))
        
        # Particle effects toggle
        y += option_height
        text = self.game.font.render("Particle Effects:", True, WHITE)
        surface.blit(text, (padding, y))
        
        toggle_rect = pygame.Rect(width - padding - 60, y, 60, 30)
        if self.game.config.particle_effects:
            pygame.draw.rect(surface, GREEN, toggle_rect)
            toggle_text = "ON"
        else:
            pygame.draw.rect(surface, RED, toggle_rect)
            toggle_text = "OFF"
        
        pygame.draw.rect(surface, WHITE, toggle_rect, 1)
        t_text = self.game.font.render(toggle_text, True, WHITE)
        surface.blit(t_text, (toggle_rect.centerx - t_text.get_width()//2, 
                             toggle_rect.centery - t_text.get_height()//2))
        
        # Screen shake toggle
        y += option_height
        text = self.game.font.render("Screen Shake:", True, WHITE)
        surface.blit(text, (padding, y))
        
        toggle_rect = pygame.Rect(width - padding - 60, y, 60, 30)
        if self.game.config.screen_shake:
            pygame.draw.rect(surface, GREEN, toggle_rect)
            toggle_text = "ON"
        else:
            pygame.draw.rect(surface, RED, toggle_rect)
            toggle_text = "OFF"
        
        pygame.draw.rect(surface, WHITE, toggle_rect, 1)
        t_text = self.game.font.render(toggle_text, True, WHITE)
        surface.blit(t_text, (toggle_rect.centerx - t_text.get_width()//2, 
                             toggle_rect.centery - t_text.get_height()//2))
        
        # Apply button
        y += option_height * 1.5
        apply_rect = pygame.Rect(width//2 - 100, y, 200, 40)
        pygame.draw.rect(surface, TECH_GREEN, apply_rect)
        pygame.draw.rect(surface, WHITE, apply_rect, 1)
        apply_text = self.game.font.render("Apply Changes", True, WHITE)
        surface.blit(apply_text, (width//2 - apply_text.get_width()//2, 
                                 y + 20 - apply_text.get_height()//2))
    
    def handle_graphics_click(self, x, y, start_y):
        """Handle clicks on graphics settings"""
        width = self.game.screen.get_width() * 0.8
        padding = 40
        option_height = 50
        
        # Quality buttons
        button_y = start_y
        button_width = 100
        button_spacing = 20
        button_x = width - padding - 3 * button_width - 2 * button_spacing
        
        if button_y <= y <= button_y + 30:
            qualities = ["LOW", "MEDIUM", "HIGH"]
            for i, quality in enumerate(qualities):
                btn_x = button_x + i * (button_width + button_spacing)
                if btn_x <= x <= btn_x + button_width:
                    self.game.config.set_graphics_quality(quality)
                    self.show()  # Refresh menu
                    return
        
        # Fullscreen toggle
        toggle_y = start_y + option_height
        toggle_rect = pygame.Rect(width - padding - 60, toggle_y, 60, 30)
        if toggle_rect.collidepoint(x, y):
            self.game.config.toggle_fullscreen()
            self.show()  # Refresh menu
            return
        
        # Show FPS toggle
        toggle_y += option_height
        toggle_rect = pygame.Rect(width - padding - 60, toggle_y, 60, 30)
        if toggle_rect.collidepoint(x, y):
            self.game.config.show_fps = not self.game.config.show_fps
            self.show()  # Refresh menu
            return
        
        # VSync toggle
        toggle_y += option_height
        toggle_rect = pygame.Rect(width - padding - 60, toggle_y, 60, 30)
        if toggle_rect.collidepoint(x, y):
            self.game.config.vsync = not self.game.config.vsync
            self.show()  # Refresh menu
            return
    
    def handle_sound_click(self, x, y, start_y):
        """Handle clicks on sound settings"""
        width = self.game.screen.get_width() * 0.8
        padding = 40
        option_height = 50
        
        # Sound enabled toggle
        toggle_y = start_y
        toggle_rect = pygame.Rect(width - padding - 60, toggle_y, 60, 30)
        if toggle_rect.collidepoint(x, y):
            self.game.config.sound_enabled = not self.game.config.sound_enabled
            self.show()  # Refresh menu
            return
        
        # Music volume slider
        slider_y = start_y + option_height
        slider_width = 200
        slider_rect = pygame.Rect(width - padding - slider_width, slider_y + 10, slider_width, 10)
        if slider_rect.y - 10 <= y <= slider_rect.y + slider_rect.height + 10:
            if slider_rect.x <= x <= slider_rect.x + slider_width:
                # Calculate volume based on x position
                self.game.config.music_volume = (x - slider_rect.x) / slider_width
                self.game.config.music_volume = max(0, min(1, self.game.config.music_volume))
                self.show()  # Refresh menu
                return
        
        # SFX volume slider
        slider_y += option_height
        slider_rect = pygame.Rect(width - padding - slider_width, slider_y + 10, slider_width, 10)
        if slider_rect.y - 10 <= y <= slider_rect.y + slider_rect.height + 10:
            if slider_rect.x <= x <= slider_rect.x + slider_width:
                # Calculate volume based on x position
                self.game.config.sfx_volume = (x - slider_rect.x) / slider_width
                self.game.config.sfx_volume = max(0, min(1, self.game.config.sfx_volume))
                self.show()  # Refresh menu
                return
    
    def handle_game_click(self, x, y, start_y):
        """Handle clicks on game settings"""
        width = self.game.screen.get_width() * 0.8
        padding = 40
        option_height = 50
        
        # Robot theme toggle
        toggle_y = start_y
        toggle_rect = pygame.Rect(width - padding - 60, toggle_y, 60, 30)
        if toggle_rect.collidepoint(x, y):
            self.game.config.toggle_robot_theme()
            self.show()  # Refresh menu
            return
        
        # Particle effects toggle
        toggle_y += option_height
        toggle_rect = pygame.Rect(width - padding - 60, toggle_y, 60, 30)
        if toggle_rect.collidepoint(x, y):
            self.game.config.toggle_particle_effects()
            self.show()  # Refresh menu
            return
        
        # Screen shake toggle
        toggle_y += option_height
        toggle_rect = pygame.Rect(width - padding - 60, toggle_y, 60, 30)
        if toggle_rect.collidepoint(x, y):
            self.game.config.screen_shake = not self.game.config.screen_shake
            self.show()  # Refresh menu
            return
        
        # Apply button
        apply_y = start_y + option_height * 4.5
        apply_rect = pygame.Rect(width//2 - 100, apply_y, 200, 40)
        if apply_rect.collidepoint(x, y):
            self.game.config.save_config()
            # Reload assets if robot theme changed
            if self.game.config.robot_theme:
                self.game.assets = GameAssets()
            self.show()  # Refresh menu
            return