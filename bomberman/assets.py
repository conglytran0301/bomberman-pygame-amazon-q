"""
Asset loading and management for Bomberman game
"""
import pygame
import random
import math
from .constants import *

class GameAssets:
    def __init__(self):
        # Create visually distinct images for game elements
        
        # Player - robot design with metallic blue color
        self.player_img = self.create_robot_image(TILE_SIZE, (70, 130, 180), is_player=True)
        
        # Enemy - robot design with red color
        self.enemy_img = self.create_robot_image(TILE_SIZE, (180, 60, 60), is_player=False)
        
        # Indestructible wall - metallic brick pattern
        self.wall_img = self.create_metallic_wall(TILE_SIZE, (80, 80, 90), (50, 50, 60))
        
        # Destructible wall - high-tech panel texture
        self.destructible_wall_img = self.create_tech_panel(TILE_SIZE, (100, 120, 140), (70, 90, 110))
        
        # Empty tile - futuristic floor grid
        self.empty_img = self.create_tech_floor(TILE_SIZE, (40, 40, 50), (60, 60, 80))
        
        # Bomb images - high-tech bombs with glowing effects
        self.fire_bomb_img = self.create_tech_bomb_image(TILE_SIZE, RED)
        self.ice_bomb_img = self.create_tech_bomb_image(TILE_SIZE, CYAN)
        self.mega_bomb_img = self.create_tech_bomb_image(TILE_SIZE, PURPLE)
        
        # Explosion image - energy blast effect
        self.explosion_img = self.create_energy_explosion(TILE_SIZE)
        self.fire_explosion_img = self.create_energy_explosion(TILE_SIZE, (255, 100, 0))
        self.ice_explosion_img = self.create_energy_explosion(TILE_SIZE, (0, 200, 255))
        self.mega_explosion_img = self.create_energy_explosion(TILE_SIZE, (200, 0, 255))
        
        # Heart image for lives - tech style energy cell
        self.heart_img = self.create_energy_cell(TILE_SIZE//2, RED)
        
        # Health bar segments
        self.health_segment_img = self.create_health_segment(TILE_SIZE//5, GREEN)
        
        # Power-up images
        self.speed_powerup_img = self.create_powerup_image(TILE_SIZE, NEON_BLUE, "S")
        self.bomb_powerup_img = self.create_powerup_image(TILE_SIZE, NEON_GREEN, "B")
        self.range_powerup_img = self.create_powerup_image(TILE_SIZE, ORANGE, "R")
        self.shield_powerup_img = self.create_powerup_image(TILE_SIZE, TECH_SILVER, "P")
        self.life_powerup_img = self.create_powerup_image(TILE_SIZE, RED, "L")
        self.remote_powerup_img = self.create_powerup_image(TILE_SIZE, PURPLE, "C")
        self.armor_powerup_img = self.create_powerup_image(TILE_SIZE, TECH_GOLD, "A")
        self.health_powerup_img = self.create_powerup_image(TILE_SIZE, GREEN, "H")
        self.ice_immunity_powerup_img = self.create_powerup_image(TILE_SIZE, (150, 220, 255), "I")
        
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
        
    def create_robot_image(self, size, color, is_player=True):
        """Create a robot-shaped character"""
        img = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Robot body - slightly rectangular
        body_height = int(size * 0.6)
        body_width = int(size * 0.7)
        body_x = (size - body_width) // 2
        body_y = (size - body_height) // 2 + int(size * 0.1)  # Slightly lower
        
        # Draw body with metallic gradient
        for i in range(body_height):
            # Create gradient effect
            shade = min(255, color[0] + i//2), min(255, color[1] + i//2), min(255, color[2] + i//2)
            pygame.draw.line(img, shade, (body_x, body_y + i), (body_x + body_width, body_y + i))
        
        # Draw head - circular for player, square for enemy
        head_size = int(size * 0.3)
        head_x = (size - head_size) // 2
        head_y = body_y - head_size + int(size * 0.05)
        
        if is_player:
            pygame.draw.circle(img, color, (size//2, head_y + head_size//2), head_size//2)
            # Add visor effect
            visor_width = int(head_size * 0.8)
            visor_height = int(head_size * 0.3)
            visor_x = (size - visor_width) // 2
            visor_y = head_y + int(head_size * 0.3)
            pygame.draw.rect(img, (100, 200, 255, 200), (visor_x, visor_y, visor_width, visor_height))
        else:
            pygame.draw.rect(img, color, (head_x, head_y, head_size, head_size))
            # Add evil-looking eyes
            eye_size = int(head_size * 0.2)
            pygame.draw.rect(img, (255, 0, 0), (head_x + eye_size, head_y + eye_size, eye_size, eye_size))
            pygame.draw.rect(img, (255, 0, 0), (head_x + head_size - eye_size*2, head_y + eye_size, eye_size, eye_size))
        
        # Draw arms
        arm_width = int(size * 0.15)
        arm_height = int(size * 0.4)
        # Left arm
        pygame.draw.rect(img, (min(255, color[0]-20), min(255, color[1]-20), min(255, color[2]-20)), 
                        (body_x - arm_width + 2, body_y + int(size * 0.1), arm_width, arm_height))
        # Right arm
        pygame.draw.rect(img, (min(255, color[0]-20), min(255, color[1]-20), min(255, color[2]-20)), 
                        (body_x + body_width - 2, body_y + int(size * 0.1), arm_width, arm_height))
        
        # Draw legs
        leg_width = int(size * 0.2)
        leg_height = int(size * 0.25)
        leg_gap = int(size * 0.1)
        # Left leg
        pygame.draw.rect(img, (min(255, color[0]-40), min(255, color[1]-40), min(255, color[2]-40)), 
                        (body_x + int(size * 0.1), body_y + body_height - 1, leg_width, leg_height))
        # Right leg
        pygame.draw.rect(img, (min(255, color[0]-40), min(255, color[1]-40), min(255, color[2]-40)), 
                        (body_x + body_width - leg_width - int(size * 0.1), body_y + body_height - 1, leg_width, leg_height))
        
        # Add highlights and details
        if is_player:
            # Antenna
            pygame.draw.line(img, (200, 200, 200), (size//2, head_y), (size//2, head_y - int(size * 0.15)), 2)
            pygame.draw.circle(img, (0, 200, 255), (size//2, head_y - int(size * 0.15)), 3)
            
            # Chest light
            pygame.draw.circle(img, (100, 200, 255), (size//2, body_y + int(body_height * 0.3)), int(size * 0.08))
            pygame.draw.circle(img, (200, 230, 255), (size//2, body_y + int(body_height * 0.3)), int(size * 0.04))
        else:
            # Enemy details
            pygame.draw.rect(img, (200, 50, 50), (size//2 - int(size * 0.15), body_y + int(body_height * 0.3), 
                                                int(size * 0.3), int(size * 0.1)))
        
        # Add metallic sheen
        for i in range(0, size, 4):
            pygame.draw.line(img, (255, 255, 255, 30), (0, i), (size, i))
            
        return img
        
    def create_metallic_wall(self, size, primary_color, secondary_color):
        """Create a metallic wall texture for indestructible walls"""
        img = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Base metallic gradient background
        for y in range(size):
            # Create vertical gradient
            shade = min(255, primary_color[0] + y//3), min(255, primary_color[1] + y//3), min(255, primary_color[2] + y//3)
            pygame.draw.line(img, shade, (0, y), (size, y))
        
        # Add metallic panel lines
        panel_size = size // 2
        for x in range(0, size, panel_size):
            for y in range(0, size, panel_size):
                pygame.draw.rect(img, secondary_color, (x, y, panel_size, panel_size), 2)
                
                # Add rivets at corners
                rivet_size = size // 16
                for rx, ry in [(x+2, y+2), (x+panel_size-2-rivet_size, y+2), 
                              (x+2, y+panel_size-2-rivet_size), (x+panel_size-2-rivet_size, y+panel_size-2-rivet_size)]:
                    pygame.draw.circle(img, (180, 180, 190), (rx + rivet_size//2, ry + rivet_size//2), rivet_size//2)
                    # Highlight on rivet
                    pygame.draw.circle(img, (220, 220, 230), (rx + rivet_size//3, ry + rivet_size//3), rivet_size//6)
        
        # Add some scratches for texture
        for _ in range(5):
            start_x, start_y = random.randint(0, size), random.randint(0, size)
            end_x, end_y = start_x + random.randint(-size//3, size//3), start_y + random.randint(-size//3, size//3)
            pygame.draw.line(img, (150, 150, 160), (start_x, start_y), (end_x, end_y), 1)
            
        # Add border
        pygame.draw.rect(img, (50, 50, 60), (0, 0, size, size), 2)
        
        return img
        
    def create_tech_panel(self, size, primary_color, secondary_color):
        """Create a high-tech panel texture for destructible walls"""
        img = pygame.Surface((size, size), pygame.SRCALPHA)
        img.fill(primary_color)
        
        # Add circuit-like pattern
        line_color = (min(255, secondary_color[0] + 30), min(255, secondary_color[1] + 30), min(255, secondary_color[2] + 30))
        
        # Horizontal and vertical lines
        for i in range(0, size, size//8):
            # Horizontal lines with random breaks
            for x in range(0, size, size//4):
                if random.random() > 0.3:  # 70% chance to draw line segment
                    end_x = min(x + random.randint(size//8, size//4), size)
                    pygame.draw.line(img, line_color, (x, i), (end_x, i), 1)
            
            # Vertical lines with random breaks
            for y in range(0, size, size//4):
                if random.random() > 0.3:  # 70% chance to draw line segment
                    end_y = min(y + random.randint(size//8, size//4), size)
                    pygame.draw.line(img, line_color, (i, y), (i, end_y), 1)
        
        # Add some "components"
        for _ in range(3):
            comp_x = random.randint(size//8, size-size//4)
            comp_y = random.randint(size//8, size-size//4)
            comp_size = random.randint(size//8, size//4)
            
            # Draw component
            pygame.draw.rect(img, secondary_color, (comp_x, comp_y, comp_size, comp_size))
            pygame.draw.rect(img, line_color, (comp_x, comp_y, comp_size, comp_size), 1)
            
            # Add details to component
            if random.random() > 0.5:
                # Circuit lines
                pygame.draw.line(img, line_color, (comp_x + comp_size//2, comp_y), 
                                (comp_x + comp_size//2, comp_y + comp_size), 1)
                pygame.draw.line(img, line_color, (comp_x, comp_y + comp_size//2), 
                                (comp_x + comp_size, comp_y + comp_size//2), 1)
            else:
                # LED-like dot
                led_color = (0, 255, 0) if random.random() > 0.5 else (255, 50, 50)
                pygame.draw.circle(img, led_color, (comp_x + comp_size//2, comp_y + comp_size//2), comp_size//6)
                # Glow effect
                pygame.draw.circle(img, (*led_color, 100), (comp_x + comp_size//2, comp_y + comp_size//2), comp_size//4)
        
        # Add border
        pygame.draw.rect(img, (min(255, secondary_color[0] + 50), min(255, secondary_color[1] + 50), min(255, secondary_color[2] + 50)), 
                        (0, 0, size, size), 2)
        
        return img
        
    def create_tech_floor(self, size, primary_color, secondary_color):
        """Create a futuristic floor grid"""
        img = pygame.Surface((size, size), pygame.SRCALPHA)
        img.fill(primary_color)
        
        # Draw grid lines
        grid_size = size // 4
        for i in range(0, size + 1, grid_size):
            pygame.draw.line(img, secondary_color, (i, 0), (i, size), 1)
            pygame.draw.line(img, secondary_color, (0, i), (size, i), 1)
        
        # Add some glowing dots at intersections
        for x in range(grid_size, size, grid_size):
            for y in range(grid_size, size, grid_size):
                if random.random() > 0.7:  # 30% chance for a glowing dot
                    glow_color = (100, 150, 255) if random.random() > 0.5 else (100, 255, 150)
                    pygame.draw.circle(img, glow_color, (x, y), 2)
                    # Add subtle glow
                    pygame.draw.circle(img, (*glow_color, 50), (x, y), 4)
        
        # Add subtle diagonal lines for texture
        for i in range(0, size, grid_size * 2):
            if random.random() > 0.5:
                pygame.draw.line(img, (*secondary_color, 100), (0, i), (i, 0), 1)
                pygame.draw.line(img, (*secondary_color, 100), (size-i, 0), (size, i), 1)
                pygame.draw.line(img, (*secondary_color, 100), (0, size-i), (i, size), 1)
                pygame.draw.line(img, (*secondary_color, 100), (size-i, size), (size, size-i), 1)
        
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
    
    def create_tech_bomb_image(self, size, color):
        """Create a high-tech bomb with glowing effects"""
        img = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Draw bomb body (hexagonal shape)
        bomb_radius = size // 2 - 4
        center = (size//2, size//2)
        
        # Create hexagon points
        points = []
        for i in range(6):
            angle = i * (360 / 6)
            angle_rad = angle * (3.14159 / 180)
            x = center[0] + int(bomb_radius * 0.9 * math.cos(angle_rad))
            y = center[1] + int(bomb_radius * 0.9 * math.sin(angle_rad))
            points.append((x, y))
        
        # Draw metallic body
        pygame.draw.polygon(img, (50, 50, 60), points)
        pygame.draw.polygon(img, (80, 80, 90), points, 2)
        
        # Add inner hexagon for detail
        inner_points = []
        for i in range(6):
            angle = i * (360 / 6)
            angle_rad = angle * (3.14159 / 180)
            x = center[0] + int(bomb_radius * 0.6 * math.cos(angle_rad))
            y = center[1] + int(bomb_radius * 0.6 * math.sin(angle_rad))
            inner_points.append((x, y))
        
        pygame.draw.polygon(img, (30, 30, 40), inner_points)
        
        # Add colored core based on bomb type
        pygame.draw.circle(img, color, center, bomb_radius // 2)
        
        # Add glow effect
        glow_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        for i in range(4):
            glow_radius = bomb_radius // 2 + i * 2
            glow_alpha = 150 - i * 40
            pygame.draw.circle(glow_surf, (*color, glow_alpha), center, glow_radius)
        img.blit(glow_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        
        # Add tech details - circuit lines
        for i in range(3):
            angle = random.randint(0, 359)
            angle_rad = angle * (3.14159 / 180)
            start_x = center[0] + int(bomb_radius * 0.5 * math.cos(angle_rad))
            start_y = center[1] + int(bomb_radius * 0.5 * math.sin(angle_rad))
            end_x = center[0] + int(bomb_radius * 0.85 * math.cos(angle_rad))
            end_y = center[1] + int(bomb_radius * 0.85 * math.sin(angle_rad))
            
            pygame.draw.line(img, (200, 200, 220), (start_x, start_y), (end_x, end_y), 1)
            
            # Add small dot at end of line
            pygame.draw.circle(img, (255, 255, 255), (end_x, end_y), 2)
        
        # Add small blinking lights
        for i in range(3):
            angle = i * (360 / 3)
            angle_rad = angle * (3.14159 / 180)
            x = center[0] + int(bomb_radius * 0.75 * math.cos(angle_rad))
            y = center[1] + int(bomb_radius * 0.75 * math.sin(angle_rad))
            
            light_color = (255, 255, 255) if random.random() > 0.5 else color
            pygame.draw.circle(img, light_color, (x, y), 2)
        
        return img
    
    def create_energy_explosion(self, size, base_color=None):
        """Create an energy blast explosion effect"""
        img = pygame.Surface((size, size), pygame.SRCALPHA)
        center = (size//2, size//2)
        
        # Create shockwave rings
        if base_color:
            # Use provided base color
            r, g, b = base_color
            colors = [
                (255, 255, 255, 200),  # White core
                (r, g, b, 180),        # Base color
                (r//2 + 128, g//2 + 128, b//2 + 128, 160),  # Lighter variant
                (r//2, g//2, b//2, 140)  # Darker variant
            ]
        else:
            # Use random colors
            colors = [
                (255, 255, 255, 200),  # White core
                (*self.get_random_energy_color(), 180),  # Random energy color
                (*self.get_random_energy_color(), 160),  # Random energy color
                (*self.get_random_energy_color(), 140)   # Random energy color
            ]
        
        radii = [size//8, size//4, size//3, size//2 - 2]
        
        # Draw gradient rings
        for i, (color, radius) in enumerate(zip(colors, radii)):
            pygame.draw.circle(img, color, center, radius)
        
        # Add energy particles
        particle_color = base_color if base_color else self.get_random_energy_color()
        for _ in range(20):
            angle = random.uniform(0, 2 * 3.14159)
            distance = random.uniform(0, size//2 - 5)
            x = center[0] + int(distance * math.cos(angle))
            y = center[1] + int(distance * math.sin(angle))
            
            particle_size = random.randint(1, 4)
            
            pygame.draw.circle(img, particle_color, (x, y), particle_size)
            # Add glow
            pygame.draw.circle(img, (*particle_color, 100), (x, y), particle_size * 2)
        
        # Add energy rays
        ray_color = base_color if base_color else self.get_random_energy_color()
        for _ in range(8):
            angle = random.uniform(0, 2 * 3.14159)
            inner_x = center[0] + int((size//8) * math.cos(angle))
            inner_y = center[1] + int((size//8) * math.sin(angle))
            outer_x = center[0] + int((size//2) * math.cos(angle))
            outer_y = center[1] + int((size//2) * math.sin(angle))
            
            pygame.draw.line(img, ray_color, (inner_x, inner_y), (outer_x, outer_y), random.randint(1, 3))
        
        return img
        
    def create_health_segment(self, size, color):
        """Create a health bar segment"""
        img = pygame.Surface((size, size//2), pygame.SRCALPHA)
        
        # Draw filled rectangle with border
        pygame.draw.rect(img, color, (0, 0, size, size//2))
        pygame.draw.rect(img, (255, 255, 255), (0, 0, size, size//2), 1)
        
        # Add highlight
        pygame.draw.line(img, (255, 255, 255, 128), (2, 2), (size-3, 2), 1)
        
        return img
        
    def get_random_energy_color(self):
        """Helper to get random energy colors"""
        colors = [
            (255, 200, 50),  # Golden
            (50, 200, 255),  # Blue
            (255, 50, 50),   # Red
            (50, 255, 100),  # Green
            (200, 50, 255)   # Purple
        ]
        return random.choice(colors)
        
    def create_powerup_image(self, size, color, letter):
        """Create a power-up image with the specified color and letter indicator"""
        img = pygame.Surface((size, size), pygame.SRCALPHA)
        center = (size//2, size//2)
        
        # Draw hexagonal base
        points = []
        for i in range(6):
            angle = i * (360 / 6)
            angle_rad = angle * (3.14159 / 180)
            x = center[0] + int((size//2 - 4) * math.cos(angle_rad))
            y = center[1] + int((size//2 - 4) * math.sin(angle_rad))
            points.append((x, y))
        
        # Draw base with gradient
        for i in range(size//2):
            alpha = 255 - i * 4
            if alpha < 50:
                alpha = 50
            pygame.draw.circle(img, (*color, alpha), center, size//2 - i)
        
        # Draw border
        pygame.draw.polygon(img, (255, 255, 255), points, 2)
        
        # Draw letter indicator
        font = pygame.font.SysFont('Arial', size//2)
        text = font.render(letter, True, (255, 255, 255))
        text_rect = text.get_rect(center=center)
        img.blit(text, text_rect)
        
        # Add glow effect
        glow_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        for i in range(3):
            glow_radius = size//2 - 2 + i * 2
            glow_alpha = 100 - i * 30
            pygame.draw.circle(glow_surf, (*color, glow_alpha), center, glow_radius)
        img.blit(glow_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        
        return img
        
    def create_energy_cell(self, size, color):
        """Create a tech style energy cell instead of heart"""
        img = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Draw hexagonal energy cell
        center = (size//2, size//2)
        radius = size//2 - 2
        
        # Create hexagon points
        points = []
        for i in range(6):
            angle = i * (360 / 6)
            angle_rad = angle * (3.14159 / 180)
            x = center[0] + int(radius * math.cos(angle_rad))
            y = center[1] + int(radius * math.sin(angle_rad))
            points.append((x, y))
        
        # Draw cell container
        pygame.draw.polygon(img, (60, 60, 70), points)
        pygame.draw.polygon(img, (100, 100, 110), points, 2)
        
        # Draw energy inside
        inner_radius = int(radius * 0.7)
        pygame.draw.circle(img, color, center, inner_radius)
        
        # Add glow effect
        glow_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        for i in range(3):
            glow_radius = inner_radius - i
            glow_alpha = 150 - i * 40
            pygame.draw.circle(glow_surf, (*color, glow_alpha), center, glow_radius)
        img.blit(glow_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        
        # Add energy level lines
        for i in range(1, 4):
            y_pos = center[1] - inner_radius//2 + i * (inner_radius//3)
            line_width = int(inner_radius * 1.2) - i * 2
            x_start = center[0] - line_width//2
            pygame.draw.line(img, (255, 255, 255, 150), (x_start, y_pos), (x_start + line_width, y_pos), 1)
        
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