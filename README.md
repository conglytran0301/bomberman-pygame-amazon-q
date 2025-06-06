# Bomberman Game with Pygame

A Bomberman-style game implemented in Python using Pygame with multiple difficulty levels, bomb types, and enemy AI.

## Features

### Core Gameplay
- Grid-based movement (1 tile per key press)
- Bomb placement with space bar
- Cross-pattern explosions that stop at walls
- Destructible and indestructible blocks
- 3 lives system

### Bomb System
- Multiple bomb types:
  - 🔥 Fire Bomb: Standard explosion with 2-tile range
  - ❄️ Ice Bomb: Freezes enemies temporarily
  - 💥 Mega Bomb: Extended explosion with 4-tile range
- Collectible bomb types
- Switch between bomb types with Tab key

### Enemy AI
- Enemies move randomly on valid tiles
- Enemies can place bombs
- Basic bomb avoidance AI
- Enemies die when hit by explosions

### Difficulty Levels
- Easy: 15x15 grid, 3 enemies
- Normal: 20x20 grid, 5 enemies
- Hard: 25x25 grid, 8 enemies
- **NEW**: Change difficulty during gameplay with Ctrl+D or when paused

### Visual Elements
- Distinct visuals for all game elements:
  - Indestructible walls: Dark gray brick pattern
  - Destructible blocks: Brown wooden texture
  - Empty tiles: Light gray floor pattern
  - Bombs: Black spheres with colored fuses
  - Explosions: Bright yellow/orange animation
  - Player: Blue circle with white border
  - Enemies: Red circles with black border
- Animated effects for bombs, explosions, and items
- Debug mode (press F1) to show tile types
- **NEW**: Responsive design that adapts to your screen size

## Requirements

- Python 3.x
- Pygame

## Installation

1. Install Python from [python.org](https://www.python.org/downloads/)
2. Install Pygame:
```
pip install pygame
```
3. Run the game:
```
python main.py
```

## Controls

- Arrow keys: Move player
- Space: Place bomb
- Tab: Switch bomb type
- Esc: Pause game
- F1: Toggle debug mode
- R: Restart game (when game over)
- Ctrl+D: Change difficulty during gameplay
- D: Change difficulty when paused

## Game Mechanics

- Player moves one tile at a time
- Bombs explode after 2 seconds
- Explosions spread in four directions
- Explosions stop at indestructible walls
- Destructible walls can be destroyed to reveal power-ups
- Colliding with enemies or explosions costs one life
- Game ends when all lives are lost

## Code Structure

The game is organized into several modules:
- `main.py`: Entry point
- `bomberman/game.py`: Main game controller
- `bomberman/sprites.py`: Player, enemy, bomb, and explosion classes
- `bomberman/map.py`: Map generation and management
- `bomberman/assets.py`: Asset loading and management
- `bomberman/constants.py`: Game constants and settings