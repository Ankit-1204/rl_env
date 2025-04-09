import numpy as np
import random
import matplotlib.pyplot as plt

MAX_UNITS = 5
VISION_RANGE = 2
EMPTY = 0
WALL = 1
CAPTURE_NEUTRAL = 2
CAPTURE_P1 = 3
CAPTURE_P2 = 4
PLAYER1 = 5
PLAYER2 = 6

MOVE_NO = -1
MOVE_UP = 0
MOVE_DOWN = 1
MOVE_LEFT = 2
MOVE_RIGHT = 3
ATTACK = 4
DEFEND = 6

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

        # Initialize multiple units for each player
        self.player1 = {
            "units": [
                {
                    "position": self._get_random_empty_cell(),
                    "health": INITIAL_HEALTH,
                    "id": f"P1_U{i}"
                } for i in range(MAX_UNITS)
            ],
            "capture_points": 0
        }
        
        self.player2 = {
            "units": [
                {
                    "position": self._get_random_empty_cell(),
                    "health": INITIAL_HEALTH,
                    "id": f"P2_U{i}"
                } for i in range(MAX_UNITS)
            ],
            "capture_points": 0
        }

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
        # Clear previous player positions
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.grid[i, j] in [CAPTURE_P1, CAPTURE_P2]:
                    self.grid[i, j] = CAPTURE_NEUTRAL
                elif self.grid[i, j] in [PLAYER1, PLAYER2]:
                    self.grid[i, j] = EMPTY

        # Update positions for all units
        for unit in self.player1["units"]:
            if unit["health"] > 0:  # Only place living units
                x, y = unit["position"]
                self.grid[x, y] = PLAYER1

        for unit in self.player2["units"]:
            if unit["health"] > 0:  # Only place living units
                x, y = unit["position"]
                self.grid[x, y] = PLAYER2

    def _get_visible_area(self, position):
        """Get the visible area for a unit at given position"""
        x, y = position
        visible_grid = np.full_like(self.grid, -1)  # -1 represents fog of war
        
        for i in range(max(0, x - VISION_RANGE), min(self.grid_size, x + VISION_RANGE + 1)):
            for j in range(max(0, y - VISION_RANGE), min(self.grid_size, y + VISION_RANGE + 1)):
                visible_grid[i, j] = self.grid[i, j]
                
        return visible_grid

    def get_observation_for_agent(self, is_agent_one=True):
        """Get observation with limited visibility for each unit"""
        if is_agent_one:
            player = self.player1
            opponent = self.player2
        else:
            player = self.player2
            opponent = self.player1

        # Combine visible areas from all units
        combined_visibility = np.full_like(self.grid, -1)
        
        for unit in player["units"]:
            if unit["health"] > 0:  # Only consider living units
                visible_area = self._get_visible_area(unit["position"])
                # Update combined visibility (reveal areas visible to any unit)
                combined_visibility = np.where(visible_area != -1, visible_area, combined_visibility)

        return {
            "grid": combined_visibility,  # Limited visibility grid
            "units": [
                {
                    "position": unit["position"],
                    "health": unit["health"],
                    "id": unit["id"]
                } for unit in player["units"]
            ],
            "visible_opponents": [
                {
                    "position": unit["position"],
                    "health": unit["health"],
                    "id": unit["id"]
                } for unit in opponent["units"]
                if unit["health"] > 0 and 
                combined_visibility[unit["position"][0], unit["position"][1]] != -1
            ],
            "capture_points": player["capture_points"],
            "turn": self.turn
        }

    def _process_action(self, player,team, opponent_units, action, is_player1=True):
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
                if self.grid[new_x, new_y] not in [WALL, PLAYER1, PLAYER2 , CAPTURE_P1, CAPTURE_P2]:
                    player["position"] = (new_x, new_y)
                    if(self.grid[new_x,new_y]==CAPTURE_NEUTRAL):
                        self.grid[new_x, new_y] = CAPTURE_P1 if is_player1 else CAPTURE_P2
                        reward += 5
                        team["capture_points"] += 1
                    elif self.grid[new_x, new_y] == EMPTY:
                        self.grid[new_x, new_y] = PLAYER1 if is_player1 else PLAYER2                      
                    
                else:
                    reward -= 1  # penalty for invalid move
            else:
                reward -= 1  # penalty for moving out of bounds

        elif action == ATTACK:
        # Check for adjacent enemy units and attack if found
            attack_successful = False
            for opponent in opponent_units:
                if opponent["health"] > 0:  # Only consider living opponents
                    opp_x, opp_y = opponent["position"]
                    if abs(opp_x - x) + abs(opp_y - y) == 1:  # Manhattan distance = 1
                        if random.random() < 0.7:  # 70% hit chance
                            damage = 10
                            opponent["health"] -= damage
                            reward += 10
                            attack_successful = True
                            break  # Only attack one enemy per action

            if not attack_successful:
                reward -= 2  # Penalty for invalid attack

        return reward
        
    def step(self, actions):
        """
        Expects a tuple of action dictionaries (actions_p1, actions_p2)
        Each action dictionary should map unit IDs to their actions
        """
        actions_p1, actions_p2 = actions
        rewards = [0, 0]

        # Process actions for player 1's units
        for unit_id, action in actions_p1.items():
            unit = next((u for u in self.player1["units"] if u["id"] == unit_id), None)
            if unit and unit["health"] > 0:
                rewards[0] += self._process_action(unit,self.player1, self.player2["units"], action, is_player1=True)

        # Process actions for player 2's units
        for unit_id, action in actions_p2.items():
            unit = next((u for u in self.player2["units"] if u["id"] == unit_id), None)
            if unit and unit["health"] > 0:
                rewards[1] += self._process_action(unit,self.player2, self.player1["units"], action, is_player1=False)

        self._update_grid_positions()
        self.turn += 1

        # Check if game is over
        p1_alive = any(unit["health"] > 0 for unit in self.player1["units"])
        p2_alive = any(unit["health"] > 0 for unit in self.player2["units"])
        done = self.turn >= self.max_turns or not p1_alive or not p2_alive

        return self.get_observation_for_agent(True), self.get_observation_for_agent(False), rewards, done, {}
    
    def render_graphic(self, ax=None, fig=None):

        """Render the game state with multiple units"""
        # Define colors for each grid element
        color_map = {
            EMPTY: "white",
            WALL: "black",
            CAPTURE_NEUTRAL: "yellow",
            CAPTURE_P1: "blue",
            CAPTURE_P2: "red",
            PLAYER1: "blue",
            PLAYER2: "red"
        }

        # If no axis is provided, create new figure
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 12))  # Increased height for unit info

        # Clear previous plots
        ax.clear()

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

                # Add unit IDs as text for player positions
                if self.grid[i, j] == PLAYER1:
                    unit = next((u for u in self.player1["units"] 
                            if u["position"] == (i, j) and u["health"] > 0), None)
                    if unit:
                        ax.text(j + 0.5, self.grid_size - i - 0.5, f'{unit["id"][-1]}', 
                            ha='center', va='center', color='white', fontweight='bold')
                
                elif self.grid[i, j] == PLAYER2:
                    unit = next((u for u in self.player2["units"] 
                            if u["position"] == (i, j) and u["health"] > 0), None)
                    if unit:
                        ax.text(j + 0.5, self.grid_size - i - 0.5, f'{unit["id"][-1]}', 
                            ha='center', va='center', color='white', fontweight='bold')

        # Set axis properties
        ax.set_xlim(0, self.grid_size)
        ax.set_ylim(0, self.grid_size)
        ax.set_xticks(range(self.grid_size))
        ax.set_yticks(range(self.grid_size))
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_aspect("equal")

        # Create status text for units
        p1_status = "Player A Units:\n" + "\n".join(
            f"Unit {u['id'][-1]}: HP={u['health']}" 
            for u in self.player1["units"]
        )
        p2_status = "Player B Units:\n" + "\n".join(
            f"Unit {u['id'][-1]}: HP={u['health']}" 
            for u in self.player2["units"]
        )

        # Update title with game info
        title_text = (
            f"Turn: {self.turn}\n"
            f"Player A Points: {self.player1['capture_points']} | "
            f"Player B Points: {self.player2['capture_points']}\n"
            f"{p1_status}\n\n{p2_status}"
        )
        ax.set_title(title_text, pad=20, loc='left')

        # Only draw if in interactive mode
        if plt.isinteractive():
            fig.canvas.draw()
            fig.canvas.flush_events()