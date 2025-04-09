import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle, Circle
import numpy as np
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
class GameVisualizer:
    def __init__(self, env, figsize=(10, 10)):
        self.env = env
        self.frames = []
        self.figsize = figsize
        
        # Define colors for grid elements
        self.color_map = {
            EMPTY: "white",
            WALL: "black",
            CAPTURE_NEUTRAL: "yellow",
            CAPTURE_P1: "blue",
            CAPTURE_P2: "red",
            PLAYER1: "blue",
            PLAYER2: "red"
        }
    
    def capture_frame(self):
        """Capture current game state including all units"""
        frame_data = {
            'grid': self.env.grid.copy(),
            'turn': self.env.turn,
            'player1_units': [{
                'position': unit['position'],
                'health': unit['health'],
                'id': unit['id']
            } for unit in self.env.player1['units']],
            'player2_units': [{
                'position': unit['position'],
                'health': unit['health'],
                'id': unit['id']
            } for unit in self.env.player2['units']],
            'p1_capture_points': self.env.player1['capture_points'],
            'p2_capture_points': self.env.player2['capture_points']
        }
        self.frames.append(frame_data)
    
    def _create_frame(self, frame_data, ax):
        """Create visualization for a single frame with multiple units"""
        ax.clear()
        
        # Draw base grid
        for i in range(self.env.grid_size):
            for j in range(self.env.grid_size):
                cell_type = frame_data['grid'][i, j]
                if cell_type not in [PLAYER1, PLAYER2]:  # Don't draw player cells, we'll add units separately
                    color = self.color_map.get(cell_type, "gray")
                    rect = Rectangle((j, self.env.grid_size - i - 1), 
                                  1, 1, 
                                  facecolor=color,
                                  edgecolor="black")
                    ax.add_patch(rect)
        
        # Draw units for both players
        for unit in frame_data['player1_units']:
            if unit['health'] > 0:  # Only draw living units
                x, y = unit['position']
                health_ratio = unit['health'] / INITIAL_HEALTH
                circle = Circle((y + 0.5, self.env.grid_size - x - 0.5), 
                              radius=0.4 * health_ratio,
                              facecolor='blue',
                              edgecolor='blue',
                              alpha=0.7)
                ax.add_patch(circle)
                # Add unit ID
                ax.text(y + 0.5, self.env.grid_size - x - 0.5, 
                       unit['id'].split('_')[1],
                       ha='center', va='center',
                       color='white', fontsize=8)

        for unit in frame_data['player2_units']:
            if unit['health'] > 0:
                x, y = unit['position']
                health_ratio = unit['health'] / INITIAL_HEALTH
                circle = Circle((y + 0.5, self.env.grid_size - x - 0.5), 
                              radius=0.4 * health_ratio,
                              facecolor='red',
                              edgecolor='red',
                              alpha=0.7)
                ax.add_patch(circle)
                ax.text(y + 0.5, self.env.grid_size - x - 0.5, 
                       unit['id'].split('_')[1],
                       ha='center', va='center',
                       color='white', fontsize=8)

        # Set grid properties
        ax.set_xlim(0, self.env.grid_size)
        ax.set_ylim(0, self.env.grid_size)
        ax.set_xticks(range(self.env.grid_size))
        ax.set_yticks(range(self.env.grid_size))
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_aspect("equal")
        
        # Update title with team information
        ax.set_title(f"Turn: {frame_data['turn']}\n"
                    f"Team A Points: {frame_data['p1_capture_points']} | "
                    f"Team B Points: {frame_data['p2_capture_points']}\n"
                    f"Units A: {sum(1 for u in frame_data['player1_units'] if u['health'] > 0)} | "
                    f"Units B: {sum(1 for u in frame_data['player2_units'] if u['health'] > 0)}")
    
    def save_animation(self, filename="game_replay.gif", fps=2):
        """Save captured frames as animation"""
        if not self.frames:
            raise ValueError("No frames captured!")
            
        fig, ax = plt.subplots(figsize=self.figsize)
        
        def animate(frame_idx):
            self._create_frame(self.frames[frame_idx], ax)
            return ax.patches + [ax.title]
        
        anim = animation.FuncAnimation(
            fig, animate, frames=len(self.frames),
            interval=1000/fps, blit=True
        )
        
        try:
            if filename.endswith('.mp4'):
                try:
                    writer = animation.FFMpegWriter(fps=fps)
                    anim.save(filename, writer=writer)
                except (FileNotFoundError, RuntimeError):
                    print("FFmpeg not found. Saving as GIF instead...")
                    filename = filename.replace('.mp4', '.gif')
                    anim.save(filename, writer='pillow', fps=fps)
            else:
                anim.save(filename, writer='pillow', fps=fps)
                
            print(f"Animation saved as: {filename}")
            
        except Exception as e:
            print(f"Error saving animation: {str(e)}")
            
        finally:
            plt.close(fig)