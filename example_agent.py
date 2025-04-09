import random

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

class MultiUnitAgent:
    def __init__(self, name="MultiUnitAgent"):
        self.name = name

    def select_actions(self, observation):
        """
        Returns a dictionary mapping unit IDs to actions
        """
        actions = {}
        
        for unit in observation["units"]:
            if unit["health"] > 0:  # Only act with living units
                unit_id = unit["id"]
                visible_grid = observation["grid"]
                
                # Simple example logic: move randomly if no enemies visible
                if not observation["visible_opponents"]:
                    actions[unit_id] = random.choice([MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT])
                else:
                    # Attack nearest visible opponent
                    nearest_opponent = min(
                        observation["visible_opponents"],
                        key=lambda x: abs(x["position"][0] - unit["position"][0]) + 
                                    abs(x["position"][1] - unit["position"][1])
                    )
                    if abs(nearest_opponent["position"][0] - unit["position"][0]) + \
                       abs(nearest_opponent["position"][1] - unit["position"][1]) == 1:
                        actions[unit_id] = ATTACK
                    else:
                        # Move toward nearest opponent
                        dx = nearest_opponent["position"][0] - unit["position"][0]
                        dy = nearest_opponent["position"][1] - unit["position"][1]
                        if abs(dx) > abs(dy):
                            actions[unit_id] = MOVE_DOWN if dx > 0 else MOVE_UP
                        else:
                            actions[unit_id] = MOVE_RIGHT if dy > 0 else MOVE_LEFT
                            
        return actions