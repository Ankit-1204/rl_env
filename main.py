from GameVis import GameVisualizer
from env import CombatArenaEnv

if __name__ == "__main__":
    env = CombatArenaEnv()
    agent_A = TacticalAgent(name="Tactical A")
    agent_B = RandomAgent(name="Random B")
    
    # Create visualizer
    vis = GameVisualizer(env)
    
    # Reset environment
    obs = env.reset()
    done = False
    
    # Capture initial state
    vis.capture_frame()
    
    while not done:
        # Get observations for both agents
        obs_A = env.get_observation_for_agent(is_agent_one=True)
        obs_B = env.get_observation_for_agent(is_agent_one=False)
        
        # Get actions from agents
        action_A = agent_A.select_action(obs_A)
        action_B = agent_B.select_action(obs_B)
        
        # Step environment
        obs1, obs2, rewards, done, info = env.step((action_A, action_B))
        
        # Capture frame
        vis.capture_frame()
        print(f"Rewards: {rewards}\n")
    
    # Save animation
    vis.save_animation("game_replay.gif", fps=2)