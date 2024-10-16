import gymnasium as gym
import sys
import os
from rl_env import VehicleEnv
import time


env =  VehicleEnv() 

num_episodes = 5


for episode in range(num_episodes):
    obs = env.reset()
    done = False
    total_reward = 0
    
    while not done:
        action = env.action_space.sample()
        obs, reward, done, _ = env.step(action)
        # print(f"obs = {obs}")
        # print(f"reward = {reward}")
        total_reward += reward
        env.render()
        if done : 
            print(f"Episode {episode + 1} finished with total reward: {total_reward}")
            env.reset()
        # time.sleep(1)
    

env.close()
