import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from typing import Dict, Any
import numpy as np
from marl_env import MultipleVehicleEnv
import os
from tqdm import tqdm

class SingleAgentWrapper(gym.Env):
    def __init__(self, env: MultipleVehicleEnv, agent_id: str):
        super().__init__()
        self.env = env
        self.agent_id = agent_id
        self.action_space = env.action_spaces[agent_id]
        self.observation_space = env.observation_spaces[agent_id]

    def reset(self, **kwargs):
        obs, info = self.env.reset(**kwargs)
        return obs[self.agent_id], info

    def step(self, action):
        actions = {agent: self.env.action_spaces[agent].sample() for agent in self.env.agents}
        actions[self.agent_id] = action
        
        obs, rewards, terminated, truncated, info = self.env.step(actions)
        
        return (
            obs[self.agent_id],
            rewards[self.agent_id],
            terminated[self.agent_id],
            truncated[self.agent_id],
            info
        )

    def render(self):
        return self.env.render()

    def close(self):
        self.env.close()

class VehicleTrainer:
    def __init__(self, save_dir: str = "models"):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
        
        self.env = MultipleVehicleEnv(render_mode=None)
        self.models: Dict[str, PPO] = {}
        
        for agent_id in self.env.agents:
            wrapped_env = SingleAgentWrapper(self.env, agent_id)
            wrapped_env = DummyVecEnv([lambda: wrapped_env])
            
            self.models[agent_id] = PPO(
                "MlpPolicy",
                wrapped_env,
                verbose=0,
                ent_coef=0.1,
                learning_rate=3e-4,
                n_steps=2048,
                batch_size=64,
                n_epochs=10,
                gamma=0.99,
                gae_lambda=0.95,
                clip_range=0.2,
                tensorboard_log=f"./tensorboard/{agent_id}/"
            )

    def train(self, total_timesteps: int = 50000, save_interval: int = 10000):
        print("Starting training...")
        
        for agent_id, model in self.models.items():
            print(f"\nTraining agent {agent_id}")
            model.learn(
                total_timesteps=total_timesteps,
                progress_bar=True,
                reset_num_timesteps=False,
                tb_log_name=f"PPO_{agent_id}"
            )
            model.save(f"{self.save_dir}/ppo_{agent_id}")
            print(f"Model for {agent_id} saved")

    def evaluate(self, n_episodes: int = 10, render: bool = True):
        print("\nStarting evaluation...")
        
        eval_env = MultipleVehicleEnv(render_mode="human" if render else None)
        
        total_rewards = {agent: 0.0 for agent in eval_env.agents}
        success_count = {agent: 0 for agent in eval_env.agents}
        
        for episode in tqdm(range(n_episodes), desc="Evaluating"):
            obs, _ = eval_env.reset()
            terminated = {agent: False for agent in eval_env.agents}
            truncated = {agent: False for agent in eval_env.agents}
            episode_rewards = {agent: 0.0 for agent in eval_env.agents}
            
            while not any(terminated.values()) and not any(truncated.values()):
                actions = {}
                for agent_id in eval_env.agents:
                    actions[agent_id], _ = self.models[agent_id].predict(
                        obs[agent_id],
                        deterministic=False
                    )
                
                obs, rewards, terminated, truncated, _ = eval_env.step(actions)
                
                for agent_id in eval_env.agents:
                    episode_rewards[agent_id] += rewards[agent_id]
                    
                    if terminated[agent_id] and rewards[agent_id] > 0:
                        success_count[agent_id] += 1
            
            for agent_id in eval_env.agents:
                total_rewards[agent_id] += episode_rewards[agent_id]
        
        print("\nEvaluation Results:")
        for agent_id in eval_env.agents:
            avg_reward = total_rewards[agent_id] / n_episodes
            success_rate = (success_count[agent_id] / n_episodes) * 100
            print(f"\n{agent_id}:")
            print(f"Average Reward: {avg_reward:.2f}")
            print(f"Success Rate: {success_rate:.2f}%")
        
        eval_env.close()

def main():
    trainer = VehicleTrainer()
    
    trainer.train(total_timesteps=200000)
    
    trainer.evaluate(n_episodes=10, render=True)

if __name__ == "__main__":
    main()