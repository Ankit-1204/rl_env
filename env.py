import numpy as np
import random
import matplotlib.pyplot as plt


# Define constants for grid elements
EMPTY = 0
WALL = 1
CAPTURE_NEUTRAL = 2
CAPTURE_P1 = 3
CAPTURE_P2 = 4
PLAYER1 = 5
PLAYER2 = 6
# Define action constants
MOVE_NO = -1
MOVE_UP = 0
MOVE_DOWN = 1
MOVE_LEFT = 2
MOVE_RIGHT = 3
ATTACK = 4
DEFEND = 6
# Game settings
GRID_SIZE = 15
MAX_TURNS = 30
INITIAL_HEALTH = 100

class CombatArenaEnv:
    def __init__(self, grid_size=GRID_SIZE, max_turns=MAX_TURNS):
        self.grid_size = grid_size
        self.max_turns = max_turns
        self.turn = 0
        self.reset()
    def reset(self):
        # Create an empty grid and add random walls and capture points
        self.grid = np.full((self.grid_size, self.grid_size), EMPTY)
        self._place_walls()
        self._place_capture_points()

        # Place players in random empty positions
        self.player1 = {"position": self._get_random_empty_cell(), "health": INITIAL_HEALTH, "capture_points": 0}
        self.player2 = {"position": self._get_random_empty_cell(), "health": INITIAL_HEALTH, "capture_points": 0}

        # Mark players on the grid
        self._update_grid_positions()
        self.turn = 0
        self.render_graphic()
        return self.get_observation_for_agent(True), self.get_observation_for_agent(False)

    def _place_walls(self):
    # Randomly place a few walls
        num_walls = int(self.grid_size * self.grid_size * 0.1)  # 10% cells are walls
        for _ in range(num_walls):
            x, y = random.randint(0, self.grid_size-1), random.randint(0, self.grid_size-1)
            self.grid[x, y] = WALL
    
    def _place_capture_points(self):
        # Randomly place some capture points (neutral)
        num_points = int(self.grid_size * self.grid_size * 0.05)  # 5% cells are capture points
        for _ in range(num_points):
            x, y = random.randint(0, self.grid_size-1), random.randint(0, self.grid_size-1)
            # Place a capture point only on an empty cell
            if self.grid[x, y] == EMPTY:
                self.grid[x, y] = CAPTURE_NEUTRAL
            
    def _get_random_empty_cell(self):
            while True:
                x, y = random.randint(0, self.grid_size-1), random.randint(0, self.grid_size-1)
                if self.grid[x, y] == EMPTY:
                    return (x, y)

    def _update_grid_positions(self):
        # Clear previous player positions (set to empty or preserve capture points)
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.grid[i, j] in [CAPTURE_P1, CAPTURE_P2]:
                    self.grid[i, j] = CAPTURE_NEUTRAL
                elif self.grid[i, j] in [PLAYER1, PLAYER2]:
                    self.grid[i, j] = EMPTY

        p1_x, p1_y = self.player1["position"]
        p2_x, p2_y = self.player2["position"]
        self.grid[p1_x, p1_y] = PLAYER1
        self.grid[p2_x, p2_y] = PLAYER2
    
    def get_observation_for_agent(self, is_agent_one=True):
        if is_agent_one:
            player = self.player1
            opponent = self.player2
        else:
            player = self.player2
            opponent = self.player1
            
        return {
            "grid": self.grid.copy(),
            "player": {
                "position": player["position"],
                "health": player["health"],
                "capture_points": player["capture_points"]
            },
            "opponent": {
                "position": opponent["position"],
                "health": opponent["health"]
            },
            "turn": self.turn
        }
    
    def step(self, actions):
        """
        Expects a tuple of actions (action_p1, action_p2)
        Both players act simultaneously.
        Returns:
            observation, rewards, done, info
        """
        action_p1, action_p2 = actions
        rewards = [0, 0]

        # Process player 1 action
        rewards[0] += self._process_action(self.player1, self.player2, action_p1, is_player1=True)
        # Process player 2 action
        rewards[1] += self._process_action(self.player2, self.player1, action_p2, is_player1=False)

        # Update grid positions after actions
        self._update_grid_positions()
        self.turn += 1

        # Check if game is over
        done = self.turn >= self.max_turns or self.player1["health"] <= 0 or self.player2["health"] <= 0
        info = {}
        return self.get_observation_for_agent(True),self.get_observation_for_agent(False), rewards, done, info
    
    def _process_action(self, player, opponent, action, is_player1=True):
        reward = 0
        # Get current position
        x, y = player["position"]

        # Movement: compute new position
        if action in [MOVE_NO,MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT]:
            new_x, new_y = x, y
            if action == MOVE_UP:
                new_x -= 1
            elif action == MOVE_DOWN:
                new_x += 1
            elif action == MOVE_LEFT:
                new_y -= 1
            elif action == MOVE_RIGHT:
                new_y += 1

            # Check boundaries and obstacles
            if 0 <= new_x < self.grid_size and 0 <= new_y < self.grid_size:
                if self.grid[new_x, new_y] not in [WALL, PLAYER1, PLAYER2]:
                    player["position"] = (new_x, new_y)
                    if(self.grid[new_x,new_y]==CAPTURE_NEUTRAL):
                        self.grid[new_x, new_y] = CAPTURE_P1 if is_player1 else CAPTURE_P2
                        reward += 5
                        player["capture_points"] += 1
                else:
                    reward -= 1  # penalty for invalid move
            else:
                reward -= 1  # penalty for moving out of bounds

        elif action == ATTACK:
            opp_x, opp_y = opponent["position"]
            if abs(opp_x - x) + abs(opp_y - y) == 1 and random.random() < 0.7:
                damage = 10
                opponent["health"] -= damage
                player["capture_points"] += 5
                reward += 10  
            else:
                reward -= 2  # invalid attack

        return reward

    def render_graphic(self, ax=None, fig=None):
        # Define colors for each grid element
        color_map = {
            EMPTY: "white",
            WALL: "black",
            CAPTURE_NEUTRAL: "yellow",
            CAPTURE_P1: "blue",
            CAPTURE_P2: "red",
            PLAYER1: "green",
            PLAYER2: "orange"
        }

        # If no axis is provided, create new figure
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 8))

        # Create a color grid
        color_grid = np.empty((self.grid_size, self.grid_size), dtype=object)
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                color_grid[i, j] = color_map.get(self.grid[i, j], "gray")

        # Plot the grid
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                rect = plt.Rectangle((j, self.grid_size - i - 1), 1, 1, 
                                facecolor=color_grid[i, j], edgecolor="black")
                ax.add_patch(rect)

        # Set axis limits and labels
        ax.set_xlim(0, self.grid_size)
        ax.set_ylim(0, self.grid_size)
        ax.set_xticks(range(self.grid_size))
        ax.set_yticks(range(self.grid_size))
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_aspect("equal")
        
        # Update title
        ax.set_title(f"Turn: {self.turn}\nPlayer A (Health: {self.player1['health']}) Capture Points: {self.player1['capture_points']} | " 
                    f"Player B (Health: {self.player2['health']}) Player B Capture Points: {self.player2['capture_points']}")
        
        # Only draw if in interactive mode
        if plt.isinteractive():
            fig.canvas.draw()
            fig.canvas.flush_events()

    

