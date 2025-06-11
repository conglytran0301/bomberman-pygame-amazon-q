"""
Screen utilities for Bomberman game
"""
import pygame
import os

def get_optimal_screen_size():
    """
    Get optimal screen size for the current display
    Returns a tuple (width, height) that fits well on most laptops
    """
    # Get screen info
    screen_info = pygame.display.Info()
    screen_width = screen_info.current_w
    screen_height = screen_info.current_h
    
    # Default size for laptops (fits well on most 1366x768 screens)
    default_width = 1024
    default_height = 700
    
    # If screen is smaller than default, adjust accordingly
    if screen_width < default_width + 100:  # Add margin
        default_width = int(screen_width * 0.9)
    
    if screen_height < default_height + 100:  # Add margin
        default_height = int(screen_height * 0.85)
    
    return (default_width, default_height)

def center_window():
    """Center the pygame window on screen"""
    os.environ['SDL_VIDEO_CENTERED'] = '1'

def calculate_tile_size(grid_size, screen_width, screen_height, ui_height=60):
    """
    Calculate optimal tile size based on grid size and screen dimensions
    
    Args:
        grid_size: Number of tiles in each dimension
        screen_width: Available screen width
        screen_height: Available screen height
        ui_height: Height reserved for UI elements
        
    Returns:
        Optimal tile size
    """
    available_height = screen_height - ui_height
    
    # Calculate tile size that fits the grid
    tile_size_width = screen_width // grid_size
    tile_size_height = available_height // grid_size
    
    # Use the smaller dimension to ensure everything fits
    return min(tile_size_width, tile_size_height)

def create_screen(width, height):
    """Create a centered pygame screen with the specified dimensions"""
    center_window()
    return pygame.display.set_mode((width, height))