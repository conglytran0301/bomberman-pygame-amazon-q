// Game constants
const GRID_SIZE = 15;
const TILE_TYPES = {
    EMPTY: 'empty',
    PLAYER: 'player',
    ENEMY: 'enemy',
    DESTRUCTIBLE: 'destructible',
    INDESTRUCTIBLE: 'indestructible',
    BOMB: 'bomb',
    EXPLOSION: 'explosion'
};

// Game state
const game = {
    grid: [],
    player: { x: 0, y: 0 },
    enemies: [],
    bombs: [],
    explosions: [],
    score: 0,
    gameOver: false,
    activeBomb: false
};

// Initialize the game
function initGame() {
    createGrid();
    placeBlocks();
    createEnemies(4);
    updateScore(0);
    updateEnemyCount();
    setupEventListeners();
    gameLoop();
}

// Create the game grid
function createGrid() {
    const gameGrid = document.getElementById('game-grid');
    gameGrid.innerHTML = '';
    game.grid = [];

    for (let y = 0; y < GRID_SIZE; y++) {
        const row = [];
        for (let x = 0; x < GRID_SIZE; x++) {
            const tile = document.createElement('div');
            tile.classList.add('tile', TILE_TYPES.EMPTY);
            tile.dataset.x = x;
            tile.dataset.y = y;
            gameGrid.appendChild(tile);
            row.push(TILE_TYPES.EMPTY);
        }
        game.grid.push(row);
    }

    // Place player at starting position
    game.player = { x: 0, y: 0 };
    updateTile(0, 0, TILE_TYPES.PLAYER);
}

// Place blocks randomly on the grid
function placeBlocks() {
    // Place indestructible blocks in a pattern (every other tile)
    for (let y = 0; y < GRID_SIZE; y++) {
        for (let x = 0; x < GRID_SIZE; x++) {
            if ((x % 2 === 0 && y % 2 === 0) && !(x === 0 && y === 0)) {
                updateTile(x, y, TILE_TYPES.INDESTRUCTIBLE);
            }
        }
    }

    // Place destructible blocks randomly (30% of remaining empty tiles)
    for (let y = 0; y < GRID_SIZE; y++) {
        for (let x = 0; x < GRID_SIZE; x++) {
            if (game.grid[y][x] === TILE_TYPES.EMPTY && Math.random() < 0.3) {
                // Keep the starting area (0,0), (1,0), (0,1) clear for player movement
                if ((x === 0 && y === 0) || (x === 1 && y === 0) || (x === 0 && y === 1)) {
                    continue;
                }
                updateTile(x, y, TILE_TYPES.DESTRUCTIBLE);
            }
        }
    }
}

// Create enemies at random positions
function createEnemies(count) {
    game.enemies = [];
    for (let i = 0; i < count; i++) {
        let x, y;
        do {
            x = Math.floor(Math.random() * GRID_SIZE);
            y = Math.floor(Math.random() * GRID_SIZE);
        } while (
            game.grid[y][x] !== TILE_TYPES.EMPTY || 
            (x === game.player.x && y === game.player.y) ||
            (Math.abs(x - game.player.x) < 3 && Math.abs(y - game.player.y) < 3)
        );

        game.enemies.push({ x, y });
        updateTile(x, y, TILE_TYPES.ENEMY);
    }
    updateEnemyCount();
}

// Update a tile on the grid
function updateTile(x, y, type) {
    if (x < 0 || x >= GRID_SIZE || y < 0 || y >= GRID_SIZE) return;
    
    game.grid[y][x] = type;
    const tile = document.querySelector(`.tile[data-x="${x}"][data-y="${y}"]`);
    
    // Remove all classes except 'tile'
    tile.className = 'tile';
    
    // Add the new type class
    tile.classList.add(type);
}

// Move the player
function movePlayer(dx, dy) {
    if (game.gameOver) return;
    
    const newX = game.player.x + dx;
    const newY = game.player.y + dy;
    
    // Check if the new position is valid
    if (
        newX >= 0 && newX < GRID_SIZE && 
        newY >= 0 && newY < GRID_SIZE && 
        [TILE_TYPES.EMPTY, TILE_TYPES.EXPLOSION].includes(game.grid[newY][newX])
    ) {
        // Update the old position
        updateTile(game.player.x, game.player.y, TILE_TYPES.EMPTY);
        
        // Update the new position
        game.player.x = newX;
        game.player.y = newY;
        updateTile(newX, newY, TILE_TYPES.PLAYER);
        
        // Check for collision with explosion
        if (isExplosionAt(newX, newY)) {
            gameOver("You were caught in an explosion!");
        }
        
        // Check for collision with enemy
        checkEnemyCollision();
    }
}

// Place a bomb at the player's position
function placeBomb() {
    if (game.gameOver || game.activeBomb) return;
    
    const { x, y } = game.player;
    
    // Create a new bomb
    const bomb = { x, y, timer: 2000 };
    game.bombs.push(bomb);
    game.activeBomb = true;
    
    // Update the tile
    updateTile(x, y, TILE_TYPES.BOMB);
}

// Explode a bomb
function explodeBomb(bomb) {
    const { x, y } = bomb;
    const explosionRange = 2;
    
    // Process each direction
    const directions = [
        { dx: 0, dy: 0 },  // Center
        { dx: 1, dy: 0 },  // Right
        { dx: -1, dy: 0 }, // Left
        { dx: 0, dy: 1 },  // Down
        { dx: 0, dy: -1 }  // Up
    ];
    
    for (const dir of directions) {
        // Skip the center for range calculation
        const isCenter = dir.dx === 0 && dir.dy === 0;
        
        // Process tiles in the direction up to range
        for (let i = isCenter ? 0 : 1; i <= (isCenter ? 0 : explosionRange); i++) {
            const currentX = x + (dir.dx * i);
            const currentY = y + (dir.dy * i);
            
            // Skip if out of bounds
            if (currentX < 0 || currentX >= GRID_SIZE || currentY < 0 || currentY >= GRID_SIZE) break;
            
            // Skip if indestructible block
            if (game.grid[currentY][currentX] === TILE_TYPES.INDESTRUCTIBLE) break;
            
            // If it's a destructible block, destroy it and stop the explosion in this direction
            if (game.grid[currentY][currentX] === TILE_TYPES.DESTRUCTIBLE) {
                updateTile(currentX, currentY, TILE_TYPES.EXPLOSION);
                game.explosions.push({ x: currentX, y: currentY, timer: 500 });
                playSound('block-break');
                break;
            }
            
            // Check for player hit
            if (currentX === game.player.x && currentY === game.player.y) {
                gameOver("You were caught in an explosion!");
            }
            
            // Check for enemy hit
            const enemyIndex = game.enemies.findIndex(enemy => enemy.x === currentX && enemy.y === currentY);
            if (enemyIndex !== -1) {
                // Remove the enemy
                game.enemies.splice(enemyIndex, 1);
                updateScore(game.score + 100);
                updateEnemyCount();
                
                // Check if all enemies are defeated
                if (game.enemies.length === 0) {
                    gameOver("You win! All enemies defeated!");
                }
            }
            
            // Create explosion
            updateTile(currentX, currentY, TILE_TYPES.EXPLOSION);
            game.explosions.push({ x: currentX, y: currentY, timer: 500 });
        }
    }
    
    // Play explosion sound
    playSound('explosion');
    
    // Reset active bomb flag
    game.activeBomb = false;
}

// Check if there's an explosion at the given position
function isExplosionAt(x, y) {
    return game.explosions.some(explosion => explosion.x === x && explosion.y === y);
}

// Check for collision with enemies
function checkEnemyCollision() {
    for (const enemy of game.enemies) {
        if (enemy.x === game.player.x && enemy.y === game.player.y) {
            gameOver("You were caught by an enemy!");
            return;
        }
    }
}

// Game over
function gameOver(message) {
    game.gameOver = true;
    
    // Create game over screen
    const gameOverScreen = document.createElement('div');
    gameOverScreen.className = 'game-over';
    
    const gameOverMessage = document.createElement('h2');
    gameOverMessage.textContent = message || "Game Over!";
    
    const scoreDisplay = document.createElement('p');
    scoreDisplay.textContent = `Your score: ${game.score}`;
    
    const restartButton = document.createElement('button');
    restartButton.textContent = "Play Again";
    restartButton.addEventListener('click', () => {
        document.body.removeChild(gameOverScreen);
        resetGame();
    });
    
    gameOverScreen.appendChild(gameOverMessage);
    gameOverScreen.appendChild(scoreDisplay);
    gameOverScreen.appendChild(restartButton);
    
    document.body.appendChild(gameOverScreen);
}

// Reset the game
function resetGame() {
    game.grid = [];
    game.player = { x: 0, y: 0 };
    game.enemies = [];
    game.bombs = [];
    game.explosions = [];
    game.score = 0;
    game.gameOver = false;
    game.activeBomb = false;
    
    initGame();
}

// Update the score display
function updateScore(newScore) {
    game.score = newScore;
    document.getElementById('score').textContent = newScore;
}

// Update the enemy count display
function updateEnemyCount() {
    document.getElementById('enemies').textContent = game.enemies.length;
}

// Move enemies randomly
function moveEnemies() {
    if (game.gameOver) return;
    
    for (const enemy of game.enemies) {
        // Store the original position
        const originalX = enemy.x;
        const originalY = enemy.y;
        
        // Try to move in a random direction
        const directions = [
            { dx: 1, dy: 0 },
            { dx: -1, dy: 0 },
            { dx: 0, dy: 1 },
            { dx: 0, dy: -1 }
        ];
        
        // Shuffle directions for randomness
        directions.sort(() => Math.random() - 0.5);
        
        let moved = false;
        for (const dir of directions) {
            const newX = enemy.x + dir.dx;
            const newY = enemy.y + dir.dy;
            
            if (
                newX >= 0 && newX < GRID_SIZE && 
                newY >= 0 && newY < GRID_SIZE && 
                [TILE_TYPES.EMPTY, TILE_TYPES.EXPLOSION].includes(game.grid[newY][newX])
            ) {
                // Update the old position
                updateTile(enemy.x, enemy.y, TILE_TYPES.EMPTY);
                
                // Update the new position
                enemy.x = newX;
                enemy.y = newY;
                updateTile(newX, newY, TILE_TYPES.ENEMY);
                
                moved = true;
                break;
            }
        }
        
        // If the enemy couldn't move, keep it in the same position
        if (!moved) {
            updateTile(originalX, originalY, TILE_TYPES.ENEMY);
        }
        
        // Check for collision with player
        if (enemy.x === game.player.x && enemy.y === game.player.y) {
            gameOver("You were caught by an enemy!");
        }
    }
}

// Play a sound effect
function playSound(type) {
    if (type === 'explosion') {
        const sound = document.getElementById('explosion-sound');
        sound.currentTime = 0;
        sound.play().catch(e => console.log("Sound play error:", e));
    } else if (type === 'block-break') {
        const sound = document.getElementById('block-break-sound');
        sound.currentTime = 0;
        sound.play().catch(e => console.log("Sound play error:", e));
    }
}

// Game loop
function gameLoop() {
    // Update bomb timers
    for (let i = game.bombs.length - 1; i >= 0; i--) {
        game.bombs[i].timer -= 16; // Approximately 16ms per frame at 60fps
        
        if (game.bombs[i].timer <= 0) {
            explodeBomb(game.bombs[i]);
            game.bombs.splice(i, 1);
        }
    }
    
    // Update explosion timers
    for (let i = game.explosions.length - 1; i >= 0; i--) {
        game.explosions[i].timer -= 16;
        
        if (game.explosions[i].timer <= 0) {
            const { x, y } = game.explosions[i];
            updateTile(x, y, TILE_TYPES.EMPTY);
            game.explosions.splice(i, 1);
        }
    }
    
    // Request the next frame
    if (!game.gameOver) {
        requestAnimationFrame(gameLoop);
    }
}

// Set up event listeners
function setupEventListeners() {
    // Keyboard controls
    document.addEventListener('keydown', (e) => {
        switch (e.key) {
            case 'ArrowUp':
                movePlayer(0, -1);
                break;
            case 'ArrowDown':
                movePlayer(0, 1);
                break;
            case 'ArrowLeft':
                movePlayer(-1, 0);
                break;
            case 'ArrowRight':
                movePlayer(1, 0);
                break;
            case ' ':
                placeBomb();
                break;
        }
    });
}

// Move enemies every second
setInterval(() => {
    if (!game.gameOver) {
        moveEnemies();
    }
}, 1000);

// Start the game when the page loads
window.addEventListener('load', initGame);