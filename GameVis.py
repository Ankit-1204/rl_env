import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle
import numpy as np

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

GRID_SIZE = 10
MAX_TURNS = 30
INITIAL_HEALTH = 100

class GameVisualizer:
    def __init__(self, env, figsize=(8, 8)):
        self.env = env
        self.frames = []  
        self.figsize = figsize
        
        self.color_map = {
            EMPTY: "white",
            WALL: "black",
            CAPTURE_NEUTRAL: "yellow",
            CAPTURE_P1: "blue",
            CAPTURE_P2: "red",
            PLAYER1: "green",
            PLAYER2: "orange"
        }
    
    def capture_frame(self):
        """Capture current game state as frame data"""
        frame_data = {
            'grid': self.env.grid.copy(),
            'turn': self.env.turn,
            'p1_health': self.env.player1['health'],
            'p2_health': self.env.player2['health']
        }
        self.frames.append(frame_data)
    
    def _create_frame(self, frame_data, ax):
        """Create visualization for a single frame"""
        ax.clear()
        
        for i in range(self.env.grid_size):
            for j in range(self.env.grid_size):
                color = self.color_map.get(frame_data['grid'][i, j], "gray")
                rect = Rectangle((j, self.env.grid_size - i - 1), 
                               1, 1, 
                               facecolor=color,
                               edgecolor="black")
                ax.add_patch(rect)

        ax.set_xlim(0, self.env.grid_size)
        ax.set_ylim(0, self.env.grid_size)
        ax.set_xticks(range(self.env.grid_size))
        ax.set_yticks(range(self.env.grid_size))
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_aspect("equal")
        
        ax.set_title(f"Turn: {frame_data['turn']}\n"
                    f"Player A (Health: {frame_data['p1_health']}) | "
                    f"Player B (Health: {frame_data['p2_health']})")
    
    def save_animation(self, filename="game_replay.gif", fps=2):
        """
        Save captured frames as animation.
        Supports .gif and .mp4 formats.
        """
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