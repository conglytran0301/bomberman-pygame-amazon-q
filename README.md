# Robot Bomberman

<div style="display: flex; align-items: center; justify-content: center">
  <img src="./assets/fcj_logo.png" alt="FCJ Logo" style="height: 200px; margin-right: 20px;">
  <img src="./assets/q_logo.png" alt="Q Logo" style="height: 200px;">
</div>

## Introduction

Robot Bomberman is a modern take on the classic Bomberman game, featuring upgraded graphics and robot characters. Developed using Python and the Pygame library, it delivers an engaging gaming experience with numerous new features.

## Short demo

![Watch Demo Video](./assets/Bomberman-Demo.gif)

## Key Features

### Characters and Graphics

- **Robot Characters**: Control a blue robot battling against red robot enemies
- **Enhanced Graphics**: High-tech visual style with metallic walls, technical panels, and energy effects
- **Particle Effects**: Beautiful explosion, smoke, and light effects

### Combat System

- **Health System**: 5 health points with visual health bar
- **Bomb Types with Unique Effects**:
  - **Fire Bombs**: Deal 2 damage with orange explosions
  - **Ice Bombs**: Deal 1 damage and slow movement with blue explosions
  - **Mega Bombs**: Deal 3 damage with larger purple explosions
- **Armor System**: Reduces damage taken from explosions

### Power-up System

Power-ups appear randomly when destroying walls:

- **Speed Boost**: Move faster for a limited time
- **Extra Bomb**: Increase the maximum number of bombs you can place at once
- **Bomb Range**: Increase the explosion range of your bombs
- **Shield**: Protect yourself from one hit completely
- **Armor**: Reduces damage taken from explosions (stacks up to level 3)
- **Health**: Restores 2 health points
- **Extra Life**: Gain an additional life (up to 5)
- **Remote Bomb**: Place bombs that you can detonate at will
- **Ice Immunity**: Temporary immunity to ice bomb slow effects

### Advanced Enemy AI

Enemies use pathfinding algorithms to hunt the player and avoid danger:

- **Wander**: Intelligently explore the map, targeting destructible walls
- **Hunt**: Chase the player when nearby and try to place strategic bombs
- **Escape**: Flee from danger when bombs are about to explode

## Controls

| Key            | Function                               |
| -------------- | -------------------------------------- |
| **Arrow Keys** | Move character                         |
| **Space**      | Place bomb                             |
| **Tab**        | Switch bomb type                       |
| **E**          | Detonate remote bombs (when available) |
| **ESC**        | Pause game                             |
| **S**          | Open settings menu (when paused)       |
| **D**          | Change difficulty (when paused)        |
| **F1**         | Toggle debug mode                      |
| **F11**        | Toggle fullscreen mode                 |

## Display Settings

The game automatically adjusts to fit laptop screens:

- Optimized for common laptop resolutions (1366x768 and higher)
- Fullscreen mode available with F11 key
- Responsive UI that scales with different screen sizes

## Settings

Access the settings menu by pressing **S** when the game is paused:

- **Graphics Quality**: Choose between Low, Medium, and High quality settings
- **Robot Theme**: Toggle the robot character theme
- **Particle Effects**: Enable/disable particle effects for better performance
- **Sound Settings**: Adjust music and sound effect volumes

## Difficulty Levels

| Level      | Grid Size | Number of Enemies | AI Characteristics                             |
| ---------- | --------- | ----------------- | ---------------------------------------------- |
| **Easy**   | 13x13     | 3                 | Limited detection range, less aggressive       |
| **Normal** | 15x15     | 5                 | Balanced behavior with moderate aggression     |
| **Hard**   | 17x17     | 8                 | Wider detection range, more aggressive hunting |

## How to Play

1. Navigate through the maze using the arrow keys
2. Place bombs with the space bar to destroy walls and defeat enemies
3. Collect power-ups to enhance your abilities
4. Defeat all enemies to advance to the next level
5. Try to achieve the highest score possible!

## System Requirements

- Python 3.6 or higher
- Pygame library (2.0.0 or higher)
- Operating System: Windows, macOS, or Linux
- RAM: 2GB or higher
- Processor: 1.5GHz or higher
- Graphics: OpenGL 2.0 support or higher

## Installation

1. Install Python from [python.org](https://www.python.org/downloads/)
2. Install Pygame using pip:
   ```
   pip install pygame
   ```
3. Download or clone this repository:
   ```
   git clone https://github.com/conglytran0301/bomberman-pygame-amazon-q.git
   ```
4. Navigate to the game directory:
   ```
   cd bomberman
   ```

## Running the Game

```
python main.py
```

## Development

The project is organized with the following structure:

```
AmazonQ-Game/
├── assets/                # Graphics and sound resources
├── bomberman/            # Main source code
│   ├── __init__.py
│   ├── assets.py         # Resource management
│   ├── constants.py      # Constants and configuration
│   ├── enemy_ai.py       # Artificial intelligence for enemies
│   ├── game.py           # Main game controller
│   ├── map.py            # Map creation and management
│   ├── powerups.py       # Power-up system
│   ├── screen_utils.py   # Screen utilities
│   ├── settings_menu.py  # Settings menu
│   └── sprites.py        # Game object classes
├── bomberman.py          # Entry point for the library
├── main.py               # Game starting point
└── README.md             # This documentation
```

## Contributing

Contributions are always welcome! If you want to contribute to this project:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

If you have any questions or suggestions, please open an issue in this repository or contact us via email.

---

Developed with ❤️ by [Your Name]
