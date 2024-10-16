import gymnasium as gym
import rl_env
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.vec_env import DummyVecEnv
import pygame as pg

# def create_env():
#     return VehicleEnv(render_mode="nothuman")

# # Check the environment
# check_env(create_env())

env = gym.make('lane-merging-v0', render_mode=None)

# Create and train the model
model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps= 500000, reset_num_timesteps=False, progress_bar=True)
# Custom training loop
# total_timesteps = 10_000
# obs = env.reset()

# for step in range(total_timesteps):
#     obs = env.reset()
#     done = False
#     total_reward = 0
    
#     while not done:
#         action, _ = model.predict(obs, deterministic=True)  # Use the model to predict the action
#         obs, reward, done, _ = env.step(action)
#         total_reward += reward
#         env.render()
#         if done.any():
#             obs = env.reset()
#     # Check if episode is done

#     # Update the model
#     model.learn(total_timesteps=1, reset_num_timesteps=False, progress_bar=True)

#     # Optional: Print progress
#     if step % 100 == 0:
#         print(f"Step: {step}/{total_timesteps}")

# Save the trained model
model.save("ppo_vehicle_model")

# Close the environment
env.close()

env = gym.make('lane-merging-v0', render_mode = "human")
obs, _ = env.reset()

for _ in range(5):    
    obs, _ = env.reset()
    done = False
    total_reward = 0

    while not done:
        action, _ = model.predict(obs, deterministic=False)  # Use the model to predict the action
        obs, reward, done, truncated, _ = env.step(action)
        total_reward += reward
        env.render()
        done = done or truncated


env.close()

# import gymnasium as gym
# import sys
# import os
# from rl_env import VehicleEnv
# from stable_baselines3 import PPO
# from stable_baselines3.common.vec_env import DummyVecEnv
# from stable_baselines3.common.monitor import Monitor
# from stable_baselines3.common.env_checker import check_env

# def create_env():
#     env = VehicleEnv(render_mode="human")  # Your custom environment
#     env = Monitor(env)  # Wrapping with Monitor to allow logging of rewards, episodes, etc.
#     return env

# # Create vectorized environment
# env = DummyVecEnv([create_env])
# check_env(create_env())

# # Train the model using PPO
# model = PPO("MlpPolicy", env, verbose=1, ent_coef=0.1, learning_rate=0.03)
# print(model)
# model.learn(total_timesteps=100000, progress_bar=True)

# # Get the environment from the trained model
# vec_env = model.get_env()

# # Reset environment and run
# obs = vec_env.reset()

# num_episodes = 5

# for episode in range(num_episodes):
#     obs = vec_env.reset()
#     done = False
#     total_reward = 0
    
#     while not done:
#         action, _ = model.predict(obs, deterministic=True)  # Use the model to predict the action
#         obs, reward, done, _ = vec_env.step(action)
#         total_reward += reward
#         vec_env.render()
        
#     print(f"Episode {episode + 1} finished with total reward: {total_reward}")

# vec_env.close()