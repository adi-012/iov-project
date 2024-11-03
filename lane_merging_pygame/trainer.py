import gymnasium as gym
import rl_env
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.vec_env import DummyVecEnv
import pygame as pg

env = gym.make('lane-merging-v0', render_mode="human")
obs, _ = env.reset()

model = PPO("MlpPolicy", env, verbose=1, ent_coef = 0.1)
model.learn(total_timesteps= 1, reset_num_timesteps=False, progress_bar=True)

model.save("ppo_vehicle_model")

env.close()

env = gym.make('lane-merging-v0', render_mode = "human")
obs, _ = env.reset()

for _ in range(1000):    
    obs, _ = env.reset()
    done = False
    total_reward = 0

    while not done:
        action, _ = model.predict(obs, deterministic=False)
        obs, reward, done, truncated, _ = env.step(action)
        total_reward += reward
        done = done or truncated


env.close()
