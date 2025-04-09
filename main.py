from GameVis import GameVisualizer
from new_env import CombatArenaEnv
from example_agent import MultiUnitAgent

if __name__ == "__main__":
    env = CombatArenaEnv()
    agent_A = MultiUnitAgent(name="Squad A")
    agent_B = MultiUnitAgent(name="Squad B")
    
    vis = GameVisualizer(env)
    
    obs_A, obs_B = env.reset()
    done = False
    
    vis.capture_frame()
    
    while not done:
        actions_A = agent_A.select_actions(obs_A)
        actions_B = agent_B.select_actions(obs_B)
        
        obs_A, obs_B, rewards, done, info = env.step((actions_A, actions_B))
        
        vis.capture_frame()
        print(f"Rewards: {rewards}\n")
    
    vis.save_animation("multi_unit_battle.gif", fps=2)