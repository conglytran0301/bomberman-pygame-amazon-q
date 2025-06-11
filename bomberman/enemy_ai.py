"""
Advanced AI for enemy robots in Bomberman game
"""
import random
import math
from .constants import *

class EnemyAI:
    def __init__(self, enemy, difficulty_level):
        self.enemy = enemy
        self.difficulty = difficulty_level
        self.target_x = None
        self.target_y = None
        self.path = []
        self.state = "wander"  # wander, hunt, escape
        self.last_decision_time = 0
        self.decision_cooldown = 30  # Frames between AI decisions
        
        # Personality traits (randomized for each enemy)
        self.aggression = random.uniform(0.3, 0.9)  # How likely to hunt player
        self.caution = random.uniform(0.3, 0.9)     # How careful about bombs
        self.intelligence = random.uniform(0.3, 0.9) # How smart in pathfinding
        
        # Adjust traits based on difficulty
        if difficulty_level == "HARD":
            self.aggression = min(1.0, self.aggression + 0.2)
            self.caution = min(1.0, self.caution + 0.1)
            self.intelligence = min(1.0, self.intelligence + 0.3)
        elif difficulty_level == "EASY":
            self.aggression = max(0.1, self.aggression - 0.2)
            self.caution = max(0.1, self.caution - 0.1)
            self.intelligence = max(0.1, self.intelligence - 0.2)
            
        # Behavior tracking
        self.last_bomb_time = 0
        self.bombs_placed = 0
        self.successful_hits = 0
        
    def update(self, game):
        """Update enemy AI state and actions"""
        # Decrease decision cooldown
        if self.last_decision_time > 0:
            self.last_decision_time -= 1
            return
            
        # Skip if frozen
        if self.enemy.frozen > 0:
            return
            
        # Update AI state based on situation
        self.update_state(game)
        
        # Take action based on current state
        if self.state == "wander":
            self.wander(game)
        elif self.state == "hunt":
            self.hunt_player(game)
        elif self.state == "escape":
            self.escape_danger(game)
            
        # Reset decision cooldown
        self.last_decision_time = self.decision_cooldown
    
    def update_state(self, game):
        """Determine the appropriate AI state based on game situation"""
        # Check if in danger - highest priority
        danger_level = self.assess_danger(game)
        if danger_level > self.caution:
            self.state = "escape"
            return
            
        # Check if player is nearby - second priority
        player_distance = self.distance_to_player(game)
        
        # Base hunt range on intelligence and difficulty
        base_hunt_range = 5
        if self.difficulty == "HARD":
            base_hunt_range = 7
        elif self.difficulty == "EASY":
            base_hunt_range = 3
            
        # Adjust hunt range based on intelligence
        hunt_range = int(base_hunt_range * (0.8 + self.intelligence * 0.4))
            
        if player_distance <= hunt_range:
            # Calculate hunt chance based on aggression and distance
            hunt_chance = self.aggression * (1.0 - player_distance / hunt_range)
            
            # Increase hunt chance if player is damaged
            if hasattr(game.player, 'health') and game.player.health < 3:
                hunt_chance += 0.2
                
            # Increase hunt chance if player is slowed
            if hasattr(game.player, 'speed_boost') and game.player.speed_boost < 0:
                hunt_chance += 0.15
                
            # Decrease hunt chance if player has shield
            if hasattr(game.player, 'shield') and game.player.shield:
                hunt_chance -= 0.2
                
            # Adjust based on success rate
            if self.bombs_placed > 0:
                success_rate = self.successful_hits / self.bombs_placed
                hunt_chance += success_rate * 0.2
                
            if random.random() < hunt_chance:
                self.state = "hunt"
                return
        
        # Check if there are good bombing opportunities nearby
        if self.check_for_bombing_opportunities(game):
            self.state = "hunt"  # Use hunt state to approach bombing target
            return
            
        # Default to wandering
        self.state = "wander"
        
    def assess_danger(self, game):
        """Assess the danger level more precisely"""
        # Check if directly in danger
        if self.is_in_danger(game):
            return 1.0  # Maximum danger
            
        # Check bombs in vicinity
        danger_level = 0.0
        for bomb in game.bombs:
            # Skip bombs that won't explode soon
            if bomb.timer > 90:  # Only worry about bombs that will explode in the next 1.5 seconds
                continue
                
            # Calculate distance to bomb
            distance = abs(bomb.x - self.enemy.x) + abs(bomb.y - self.enemy.y)
            bomb_range = getattr(bomb, 'range', 2)
            
            # Check if in potential blast radius
            if distance <= bomb_range + 1:
                # Calculate danger based on timer and distance
                time_factor = 1.0 - bomb.timer / 90.0  # 0 to 1, higher as timer gets lower
                distance_factor = 1.0 - distance / (bomb_range + 1)  # 0 to 1, higher as distance gets smaller
                
                # Combine factors
                bomb_danger = time_factor * distance_factor
                
                # Take the maximum danger from any bomb
                danger_level = max(danger_level, bomb_danger)
        
        return danger_level
        
    def check_for_bombing_opportunities(self, game):
        """Check if there are good opportunities to place bombs nearby"""
        # Skip if already has an active bomb or on cooldown
        if self.enemy.active_bomb or self.enemy.bomb_cooldown > 0:
            return False
            
        # Check for clusters of destructible walls
        wall_clusters = []
        
        # Search in a radius around the enemy
        search_radius = 3
        for y in range(max(0, self.enemy.y - search_radius), min(game.grid_size, self.enemy.y + search_radius + 1)):
            for x in range(max(0, self.enemy.x - search_radius), min(game.grid_size, self.enemy.x + search_radius + 1)):
                # Skip current position
                if x == self.enemy.x and y == self.enemy.y:
                    continue
                    
                # Count adjacent destructible walls
                adjacent_walls = 0
                for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    nx, ny = x + dx, y + dy
                    if (0 <= nx < game.grid_size and 0 <= ny < game.grid_size and 
                        game.grid[ny][nx] == DESTRUCTIBLE):
                        adjacent_walls += 1
                
                # If position has multiple adjacent walls and is empty
                if adjacent_walls >= 3 and game.grid[y][x] == EMPTY:
                    # Check if position is reachable
                    if self.can_reach_position(game, x, y):
                        wall_clusters.append((x, y, adjacent_walls))
        
        # If found good bombing opportunities, set target to the best one
        if wall_clusters:
            # Sort by number of adjacent walls (descending)
            wall_clusters.sort(key=lambda c: -c[2])
            
            # Set target to best opportunity
            self.target_x, self.target_y, _ = wall_clusters[0]
            return True
            
        return False
        
    def can_reach_position(self, game, x, y):
        """Check if a position is reachable"""
        # Simple BFS to check reachability
        queue = [(self.enemy.x, self.enemy.y)]
        visited = {(self.enemy.x, self.enemy.y)}
        
        while queue:
            cx, cy = queue.pop(0)
            
            # Check if we've reached the target
            if cx == x and cy == y:
                return True
                
            # Check neighbors
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = cx + dx, cy + dy
                
                # Skip if out of bounds, not walkable, or already visited
                if ((nx, ny) in visited or
                    nx < 0 or nx >= game.grid_size or
                    ny < 0 or ny >= game.grid_size or
                    game.grid[ny][nx] != EMPTY or
                    any(bomb.x == nx and bomb.y == ny for bomb in game.bombs)):
                    continue
                    
                # Add to queue and visited
                queue.append((nx, ny))
                visited.add((nx, ny))
        
        return False
    
    def wander(self, game):
        """Wander around the map intelligently"""
        # Check if we should place a bomb at current position
        if self.should_place_bomb_while_wandering(game):
            self.enemy.try_place_bomb(game)
            # After placing bomb, escape
            self.state = "escape"
            return
            
        # If we have a target and haven't reached it yet, continue moving toward it
        if self.target_x is not None and self.target_y is not None:
            if self.enemy.x == self.target_x and self.enemy.y == self.target_y:
                # Reached target, clear it
                self.target_x = None
                self.target_y = None
                
                # Check if we should place a bomb at the target
                if self.should_place_bomb_while_wandering(game):
                    self.enemy.try_place_bomb(game)
                    # After placing bomb, escape
                    self.state = "escape"
                    return
            else:
                # Continue moving toward target
                self.move_toward_target(game)
                return
                
        # No target or reached previous target, find a new one
        # Look for destructible walls, power-ups, or open spaces
        targets = []
        
        # Search in a radius around the enemy
        search_radius = 5
        if self.difficulty == "HARD":
            search_radius = 7  # Larger search radius on hard difficulty
            
        for y in range(max(0, self.enemy.y - search_radius), min(game.grid_size, self.enemy.y + search_radius + 1)):
            for x in range(max(0, self.enemy.x - search_radius), min(game.grid_size, self.enemy.x + search_radius + 1)):
                # Skip current position
                if x == self.enemy.x and y == self.enemy.y:
                    continue
                    
                # Look for empty spaces next to destructible walls
                if game.grid[y][x] == EMPTY:
                    # Check if there's a power-up here (highest priority)
                    has_powerup = False
                    if hasattr(game, 'powerup_manager'):
                        for powerup in game.powerup_manager.powerups:
                            if powerup.x == x and powerup.y == y:
                                has_powerup = True
                                targets.append((x, y, 4))  # Highest priority
                                break
                    
                    if not has_powerup:
                        # Check if adjacent to multiple destructible walls (higher priority)
                        adjacent_walls = 0
                        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                            nx, ny = x + dx, y + dy
                            if (0 <= nx < game.grid_size and 0 <= ny < game.grid_size and 
                                game.grid[ny][nx] == DESTRUCTIBLE):
                                adjacent_walls += 1
                        
                        if adjacent_walls > 1:
                            # This is an excellent target - near multiple destructible walls
                            targets.append((x, y, 3))  # Very high priority
                        elif adjacent_walls == 1:
                            # This is a good target - near a destructible wall
                            targets.append((x, y, 2))  # Higher priority
                        else:
                            # Just an empty space
                            targets.append((x, y, 1))  # Lower priority
        
        if targets:
            # Sort by priority (higher first) then by distance (closer first)
            targets.sort(key=lambda t: (-t[2], abs(t[0] - self.enemy.x) + abs(t[1] - self.enemy.y)))
            
            # Select one of the top targets with some randomness
            # More randomness on easy, less on hard
            if self.difficulty == "EASY":
                top_count = min(5, len(targets))
                selected = random.randint(0, top_count - 1)
            elif self.difficulty == "NORMAL":
                top_count = min(3, len(targets))
                selected = random.randint(0, top_count - 1)
            else:  # HARD
                top_count = min(2, len(targets))
                selected = 0  # Always choose the best target on hard
                
            self.target_x, self.target_y, _ = targets[selected]
            
            # Find path to target
            self.find_path_to_target(game)
            
            # Move toward target
            self.move_toward_target(game)
        else:
            # No good targets found, move randomly
            self.enemy.move_random(game)
            
    def should_place_bomb_while_wandering(self, game):
        """Check if we should place a bomb while wandering"""
        # Don't place bomb if already has an active bomb or on cooldown
        if self.enemy.active_bomb or self.enemy.bomb_cooldown > 0:
            return False
            
        # Count adjacent destructible walls
        adjacent_walls = 0
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = self.enemy.x + dx, self.enemy.y + dy
            if (0 <= nx < game.grid_size and 0 <= ny < game.grid_size and 
                game.grid[ny][nx] == DESTRUCTIBLE):
                adjacent_walls += 1
        
        # Place bomb if there are enough adjacent walls and we can escape
        if adjacent_walls >= 2:  # At least 2 adjacent walls
            # Check if we can escape
            can_escape = self.can_escape_after_bomb(game)
            if can_escape:
                # Higher chance on harder difficulties
                bomb_chance = 0.4  # Base chance
                if self.difficulty == "HARD":
                    bomb_chance = 0.9
                elif self.difficulty == "NORMAL":
                    bomb_chance = 0.7
                
                # Increase chance based on number of walls
                bomb_chance += adjacent_walls * 0.1
                
                return random.random() < bomb_chance
                
        return False
    
    def hunt_player(self, game):
        """Hunt the player intelligently"""
        # Check if we're already in a good position to place a bomb
        if self.should_place_bomb(game):
            self.enemy.try_place_bomb(game)
            # After placing bomb, escape
            self.state = "escape"
            return
        
        # Try to predict player's movement
        predicted_x, predicted_y = self.predict_player_movement(game)
        
        # If prediction is valid, target that position instead of current player position
        if predicted_x is not None and predicted_y is not None:
            self.target_x = predicted_x
            self.target_y = predicted_y
        else:
            # Fall back to current player position
            self.target_x = game.player.x
            self.target_y = game.player.y
            
        # Find path to target
        self.find_path_to_target(game)
        
        # If no path found or path is too long, try to find a position to intercept player
        if not self.path or len(self.path) > 10:
            intercept_x, intercept_y = self.find_intercept_position(game)
            if intercept_x is not None and intercept_y is not None:
                self.target_x = intercept_x
                self.target_y = intercept_y
                self.find_path_to_target(game)
        
        # Move toward target
        self.move_toward_target(game)
        
    def predict_player_movement(self, game):
        """Try to predict where the player will move next"""
        # Only predict on harder difficulties
        if self.difficulty == "EASY":
            return None, None
            
        # Get player's current position
        player_x, player_y = game.player.x, game.player.y
        
        # Check if player is near bombs that are about to explode
        in_danger = False
        danger_directions = []
        
        # Check all bombs
        for bomb in game.bombs:
            if bomb.timer <= 60:  # Bomb will explode soon
                bomb_range = getattr(bomb, 'range', 2)
                
                # Check if player is in bomb's range
                if (bomb.x == player_x and abs(bomb.y - player_y) <= bomb_range) or \
                   (bomb.y == player_y and abs(bomb.x - player_x) <= bomb_range):
                    in_danger = True
                    
                    # Determine safe directions away from bomb
                    if bomb.x == player_x:
                        # Bomb is in same column, move horizontally
                        danger_directions.extend([(0, 1), (0, -1)])
                    elif bomb.y == player_y:
                        # Bomb is in same row, move vertically
                        danger_directions.extend([(1, 0), (-1, 0)])
        
        # If player is in danger, predict they'll move to safety
        if in_danger:
            # Find safe directions (directions not in danger_directions)
            safe_directions = []
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                if (dx, dy) not in danger_directions:
                    nx, ny = player_x + dx, player_y + dy
                    if (0 <= nx < game.grid_size and 0 <= ny < game.grid_size and 
                        game.grid[ny][nx] == EMPTY and
                        not any(bomb.x == nx and bomb.y == ny for bomb in game.bombs)):
                        safe_directions.append((dx, dy))
            
            # If there are safe directions, predict player will move in one of them
            if safe_directions:
                # On hard difficulty, choose the direction that leads away from enemy
                if self.difficulty == "HARD":
                    # Calculate direction away from enemy
                    away_dx = player_x - self.enemy.x
                    away_dy = player_y - self.enemy.y
                    
                    # Normalize
                    if away_dx != 0:
                        away_dx = away_dx // abs(away_dx)
                    if away_dy != 0:
                        away_dy = away_dy // abs(away_dy)
                    
                    # Find direction most similar to away direction
                    best_dir = safe_directions[0]
                    best_similarity = -1
                    
                    for dx, dy in safe_directions:
                        similarity = (dx * away_dx + dy * away_dy)
                        if similarity > best_similarity:
                            best_similarity = similarity
                            best_dir = (dx, dy)
                    
                    dx, dy = best_dir
                else:
                    # On normal difficulty, choose a random safe direction
                    dx, dy = random.choice(safe_directions)
                
                return player_x + dx, player_y + dy
        
        # If player is not in danger or no safe directions, check if they're near power-ups
        if hasattr(game, 'powerup_manager') and game.powerup_manager.powerups:
            # Find closest power-up
            closest_powerup = None
            min_distance = float('inf')
            
            for powerup in game.powerup_manager.powerups:
                distance = abs(powerup.x - player_x) + abs(powerup.y - player_y)
                if distance < min_distance and distance <= 5:  # Only consider nearby power-ups
                    min_distance = distance
                    closest_powerup = powerup
            
            # If there's a nearby power-up, predict player will move toward it
            if closest_powerup:
                # Calculate direction toward power-up
                dx = 0
                dy = 0
                
                if closest_powerup.x > player_x:
                    dx = 1
                elif closest_powerup.x < player_x:
                    dx = -1
                    
                if closest_powerup.y > player_y:
                    dy = 1
                elif closest_powerup.y < player_y:
                    dy = -1
                
                # Choose horizontal or vertical movement
                if dx != 0 and dy != 0:
                    if random.random() < 0.5:
                        dy = 0
                    else:
                        dx = 0
                
                # Check if move is valid
                nx, ny = player_x + dx, player_y + dy
                if (0 <= nx < game.grid_size and 0 <= ny < game.grid_size and 
                    game.grid[ny][nx] == EMPTY and
                    not any(bomb.x == nx and bomb.y == ny for bomb in game.bombs)):
                    return nx, ny
        
        # No prediction
        return None, None
        
    def find_intercept_position(self, game):
        """Find a position to intercept the player"""
        # Only use on harder difficulties
        if self.difficulty == "EASY":
            return None, None
            
        # Get player's current position
        player_x, player_y = game.player.x, game.player.y
        
        # Calculate direction from enemy to player
        dx = player_x - self.enemy.x
        dy = player_y - self.enemy.y
        
        # Normalize direction
        if dx != 0:
            dx = dx // abs(dx)
        if dy != 0:
            dy = dy // abs(dy)
        
        # Try to find a position ahead of the player
        for i in range(1, 4):  # Look up to 3 tiles ahead
            nx, ny = player_x + dx * i, player_y + dy * i
            
            # Check if position is valid
            if (0 <= nx < game.grid_size and 0 <= ny < game.grid_size and 
                game.grid[ny][nx] == EMPTY and
                not any(bomb.x == nx and bomb.y == ny for bomb in game.bombs)):
                
                # Check if we can reach this position
                # Find path to this position
                start = (self.enemy.x, self.enemy.y)
                goal = (nx, ny)
                
                # Simple A* pathfinding
                open_set = {start}
                closed_set = set()
                g_score = {start: 0}
                f_score = {start: self.heuristic(start, goal)}
                came_from = {}
                
                while open_set:
                    current = min(open_set, key=lambda pos: f_score.get(pos, float('inf')))
                    
                    if current == goal:
                        # Path found, this is a good intercept position
                        return nx, ny
                        
                    open_set.remove(current)
                    closed_set.add(current)
                    
                    for d_x, d_y in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                        neighbor = (current[0] + d_x, current[1] + d_y)
                        
                        if (neighbor in closed_set or
                            neighbor[0] < 0 or neighbor[0] >= game.grid_size or
                            neighbor[1] < 0 or neighbor[1] >= game.grid_size or
                            game.grid[neighbor[1]][neighbor[0]] != EMPTY or
                            any(bomb.x == neighbor[0] and bomb.y == neighbor[1] for bomb in game.bombs)):
                            continue
                            
                        tentative_g_score = g_score[current] + 1
                        
                        if neighbor not in open_set or tentative_g_score < g_score.get(neighbor, float('inf')):
                            came_from[neighbor] = current
                            g_score[neighbor] = tentative_g_score
                            f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
                            
                            if neighbor not in open_set:
                                open_set.add(neighbor)
        
        # No good intercept position found
        return None, None
    
    def escape_danger(self, game):
        """Escape from dangerous situations"""
        # Find safe tiles
        safe_tiles = []
        
        # Search in a radius around the enemy
        search_radius = 5
        for y in range(max(0, self.enemy.y - search_radius), min(game.grid_size, self.enemy.y + search_radius + 1)):
            for x in range(max(0, self.enemy.x - search_radius), min(game.grid_size, self.enemy.x + search_radius + 1)):
                # Skip current position
                if x == self.enemy.x and y == self.enemy.y:
                    continue
                    
                # Check if this tile is safe
                if (game.grid[y][x] == EMPTY and 
                    not any(bomb.x == x and bomb.y == y for bomb in game.bombs) and
                    not self.is_tile_in_danger(x, y, game)):
                    
                    # Calculate distance
                    distance = abs(x - self.enemy.x) + abs(y - self.enemy.y)
                    safe_tiles.append((x, y, distance))
        
        if safe_tiles:
            # Sort by distance (closer first)
            safe_tiles.sort(key=lambda t: t[2])
            
            # Select the closest safe tile
            self.target_x, self.target_y, _ = safe_tiles[0]
            
            # Find path to safe tile
            self.find_path_to_target(game)
            
            # Move toward safe tile
            self.move_toward_target(game)
        else:
            # No safe tiles found, move randomly and hope for the best
            self.enemy.move_random(game)
    
    def find_path_to_target(self, game):
        """Find a path to the target using A* algorithm"""
        if self.target_x is None or self.target_y is None:
            return
            
        # A* pathfinding
        start = (self.enemy.x, self.enemy.y)
        goal = (self.target_x, self.target_y)
        
        # If start and goal are the same, no path needed
        if start == goal:
            self.path = []
            return
            
        # Initialize open and closed sets
        open_set = {start}
        closed_set = set()
        
        # Initialize g_score and f_score dictionaries
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}
        
        # Initialize came_from dictionary
        came_from = {}
        
        while open_set:
            # Find node with lowest f_score
            current = min(open_set, key=lambda pos: f_score.get(pos, float('inf')))
            
            # Check if we've reached the goal
            if current == goal:
                # Reconstruct path
                self.path = self.reconstruct_path(came_from, current)
                return
                
            # Move current from open_set to closed_set
            open_set.remove(current)
            closed_set.add(current)
            
            # Check neighbors
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                neighbor = (current[0] + dx, current[1] + dy)
                
                # Skip if out of bounds or not walkable
                if (neighbor[0] < 0 or neighbor[0] >= game.grid_size or
                    neighbor[1] < 0 or neighbor[1] >= game.grid_size or
                    game.grid[neighbor[1]][neighbor[0]] != EMPTY or
                    any(bomb.x == neighbor[0] and bomb.y == neighbor[1] for bomb in game.bombs)):
                    continue
                    
                # Skip if in closed set
                if neighbor in closed_set:
                    continue
                    
                # Calculate tentative g_score
                tentative_g_score = g_score[current] + 1
                
                # Check if this path is better
                if neighbor not in open_set or tentative_g_score < g_score.get(neighbor, float('inf')):
                    # Update path
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
                    
                    # Add to open set if not already there
                    if neighbor not in open_set:
                        open_set.add(neighbor)
        
        # No path found
        self.path = []
    
    def reconstruct_path(self, came_from, current):
        """Reconstruct path from came_from dictionary"""
        total_path = [current]
        while current in came_from:
            current = came_from[current]
            total_path.append(current)
        
        # Reverse to get path from start to goal
        total_path.reverse()
        
        # Remove the first element (current position)
        if total_path:
            total_path.pop(0)
            
        return total_path
    
    def heuristic(self, a, b):
        """Manhattan distance heuristic"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def move_toward_target(self, game):
        """Move toward the target using the calculated path"""
        if not self.path:
            # No path, try to find one
            self.find_path_to_target(game)
            
            # If still no path, move randomly
            if not self.path:
                self.enemy.move_random(game)
                return
        
        # Get next step in path
        next_x, next_y = self.path[0]
        
        # Calculate direction
        dx = next_x - self.enemy.x
        dy = next_y - self.enemy.y
        
        # Check if the move is valid
        new_x, new_y = self.enemy.x + dx, self.enemy.y + dy
        if (0 <= new_x < game.grid_size and 
            0 <= new_y < game.grid_size and 
            game.grid[new_y][new_x] == EMPTY and
            not any(bomb.x == new_x and bomb.y == new_y for bomb in game.bombs)):
            
            # Move to next position
            self.enemy.x, self.enemy.y = new_x, new_y
            
            # Remove this step from the path
            self.path.pop(0)
        else:
            # Path is blocked, recalculate
            self.path = []
            self.enemy.move_random(game)
    
    def should_place_bomb(self, game):
        """Determine if the enemy should place a bomb"""
        # Don't place bomb if already has an active bomb or on cooldown
        if self.enemy.active_bomb or self.enemy.bomb_cooldown > 0:
            return False
            
        # Check if player is nearby
        player_distance = self.distance_to_player(game)
        
        # Get bomb range based on difficulty
        bomb_range = 2
        if self.difficulty == "HARD":
            bomb_range = 3
        
        # Check if there are destructible walls nearby
        has_nearby_wall = False
        wall_positions = []
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), (2, 0), (-2, 0), (0, 2), (0, -2)]:
            nx, ny = self.enemy.x + dx, self.enemy.y + dy
            if (0 <= nx < game.grid_size and 0 <= ny < game.grid_size and 
                game.grid[ny][nx] == DESTRUCTIBLE):
                has_nearby_wall = True
                wall_positions.append((nx, ny))
        
        # Check if player is in bomb range (same row or column)
        player_in_range = False
        if (self.enemy.x == game.player.x and abs(self.enemy.y - game.player.y) <= bomb_range):
            # Check if there are walls blocking the path to player
            blocked = False
            min_y = min(self.enemy.y, game.player.y)
            max_y = max(self.enemy.y, game.player.y)
            for y in range(min_y + 1, max_y):
                if game.grid[y][self.enemy.x] != EMPTY:
                    blocked = True
                    break
            if not blocked:
                player_in_range = True
        
        elif (self.enemy.y == game.player.y and abs(self.enemy.x - game.player.x) <= bomb_range):
            # Check if there are walls blocking the path to player
            blocked = False
            min_x = min(self.enemy.x, game.player.x)
            max_x = max(self.enemy.x, game.player.x)
            for x in range(min_x + 1, max_x):
                if game.grid[self.enemy.y][x] != EMPTY:
                    blocked = True
                    break
            if not blocked:
                player_in_range = True
        
        # Strategic bomb placement - check if we can trap the player
        can_trap_player = False
        if player_distance <= bomb_range + 2:  # Player is close enough to potentially trap
            # Check if player has limited escape routes
            player_escape_routes = self.count_player_escape_routes(game)
            if player_escape_routes <= 2:  # Player has limited escape options
                can_trap_player = True
        
        # Check if we have an escape route before placing a bomb
        if player_in_range or has_nearby_wall or can_trap_player:
            # Simulate bomb placement
            can_escape = self.can_escape_after_bomb(game)
            if can_escape:
                # Higher chance to place bomb on harder difficulties
                base_chance = 0.3
                if self.difficulty == "HARD":
                    base_chance = 0.8
                elif self.difficulty == "NORMAL":
                    base_chance = 0.5
                
                # Increase chance if player is in range
                if player_in_range:
                    base_chance += 0.2
                
                # Increase chance if we can trap the player
                if can_trap_player:
                    base_chance += 0.3
                
                # Increase chance if there are multiple walls to destroy
                if len(wall_positions) >= 2:
                    base_chance += 0.1
                
                # Cap the chance at 0.95
                bomb_chance = min(0.95, base_chance)
                
                return random.random() < bomb_chance
        
        return False
        
    def count_player_escape_routes(self, game):
        """Count how many escape routes the player has"""
        escape_routes = 0
        
        # Check in all four directions
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = game.player.x + dx, game.player.y + dy
            
            # Check if this direction is a valid escape route
            if (0 <= nx < game.grid_size and 
                0 <= ny < game.grid_size and 
                game.grid[ny][nx] == EMPTY and
                not any(bomb.x == nx and bomb.y == ny for bomb in game.bombs) and
                not self.is_tile_in_danger(nx, ny, game)):
                escape_routes += 1
        
        return escape_routes
    
    def can_escape_after_bomb(self, game):
        """Check if the enemy can escape after placing a bomb"""
        # Temporarily mark current position as having a bomb
        has_bomb_at_position = any(bomb.x == self.enemy.x and bomb.y == self.enemy.y for bomb in game.bombs)
        
        # If there's already a bomb here, we can't place another one
        if has_bomb_at_position:
            return False
            
        # Calculate danger tiles if a bomb was placed here
        danger_tiles = set()
        bomb_range = 2  # Default bomb range
        
        # Add bomb position
        danger_tiles.add((self.enemy.x, self.enemy.y))
        
        # Add tiles in bomb range
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            for i in range(1, bomb_range + 1):
                nx, ny = self.enemy.x + (dx * i), self.enemy.y + (dy * i)
                
                # Stop at grid boundaries
                if nx < 0 or nx >= game.grid_size or ny < 0 or ny >= game.grid_size:
                    break
                
                # Stop at walls
                if game.grid[ny][nx] != EMPTY:
                    break
                
                # Add to danger tiles
                danger_tiles.add((nx, ny))
        
        # Check if there's a safe tile we can reach
        for y in range(max(0, self.enemy.y - bomb_range - 1), min(game.grid_size, self.enemy.y + bomb_range + 2)):
            for x in range(max(0, self.enemy.x - bomb_range - 1), min(game.grid_size, self.enemy.x + bomb_range + 2)):
                # Skip danger tiles
                if (x, y) in danger_tiles:
                    continue
                    
                # Check if this tile is safe and reachable
                if (game.grid[y][x] == EMPTY and 
                    not any(bomb.x == x and bomb.y == y for bomb in game.bombs) and
                    not self.is_tile_in_danger(x, y, game) and
                    self.can_reach_tile(x, y, game, danger_tiles)):
                    return True
        
        return False
    
    def can_reach_tile(self, x, y, game, danger_tiles):
        """Check if the enemy can reach a tile without going through danger tiles"""
        # Simple BFS to find path
        queue = [(self.enemy.x, self.enemy.y)]
        visited = {(self.enemy.x, self.enemy.y)}
        
        while queue:
            cx, cy = queue.pop(0)
            
            # Check if we've reached the target
            if cx == x and cy == y:
                return True
                
            # Check neighbors
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = cx + dx, cy + dy
                
                # Skip if out of bounds, not walkable, or already visited
                if ((nx, ny) in visited or
                    nx < 0 or nx >= game.grid_size or
                    ny < 0 or ny >= game.grid_size or
                    game.grid[ny][nx] != EMPTY or
                    any(bomb.x == nx and bomb.y == ny for bomb in game.bombs) or
                    (nx, ny) in danger_tiles):
                    continue
                    
                # Add to queue and visited
                queue.append((nx, ny))
                visited.add((nx, ny))
        
        return False
    
    def is_in_danger(self, game):
        """Check if the enemy is in danger"""
        return self.is_tile_in_danger(self.enemy.x, self.enemy.y, game)
    
    def is_tile_in_danger(self, x, y, game):
        """Check if a tile is in danger from bombs"""
        # Check all bombs
        for bomb in game.bombs:
            # Skip bombs that won't explode soon
            if bomb.timer > 60:  # Only worry about bombs that will explode in the next second
                continue
                
            # Check if tile is in bomb's explosion range
            bomb_range = getattr(bomb, 'range', 2)  # Default to 2 if range not specified
            
            # Check if in same row or column
            if bomb.x == x and abs(bomb.y - y) <= bomb_range:
                # Check if there are walls blocking the explosion
                blocked = False
                step = 1 if bomb.y < y else -1
                for cy in range(bomb.y + step, y, step):
                    if game.grid[cy][x] != EMPTY:
                        blocked = True
                        break
                if not blocked:
                    return True
            
            if bomb.y == y and abs(bomb.x - x) <= bomb_range:
                # Check if there are walls blocking the explosion
                blocked = False
                step = 1 if bomb.x < x else -1
                for cx in range(bomb.x + step, x, step):
                    if game.grid[y][cx] != EMPTY:
                        blocked = True
                        break
                if not blocked:
                    return True
        
        return False
    
    def distance_to_player(self, game):
        """Calculate Manhattan distance to player"""
        return abs(self.enemy.x - game.player.x) + abs(self.enemy.y - game.player.y)