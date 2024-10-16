import pygame as pg
import GloDec as gd
import numpy as np
import gymnasium as gym
from gym import spaces
from gymnasium.envs.registration import register
import time

register(
    id = "lane-merging-env-v0",
    entry_point = "custom_env:VehicleEnv",
    max_episode_steps = 2000
)

class VehicleEnv(gym.Env):
    def __init__(self):
        super(VehicleEnv, self).__init__()

        # Actions: [turn_left, turn_right, accelerate, decelerate]
        self.action_space = spaces.Discrete(4)

        # Observation space: [x_position, y_position, angle, speed]
        self.observation_space = spaces.Box(low = np.array([0, 0, -40, 0]), 
                                            high = np.array([1280, 720, 40, 200]), dtype=np.float32)
        
        pg.init()

        self.done = False
        # self.reset()

    def reset(self):
        self.done = False
        gd.v1.origin = {'x': 600, 'y': 385}
        gd.v1.angle = 0
        gd.v1.speed = 60
        gd.v1.count = 0
        gd.v1.last_update_time = None
        gd.v1.timestamp = time.time()

        return np.array([gd.v1.origin['x'], gd.v1.origin['y'], gd.v1.angle, gd.v1.speed], dtype=np.float32)

    def step(self, action):
        if action == 0:  # turn left
            gd.v1.turn(-1)
        elif action == 1:  # turn right
            gd.v1.turn(1)
        elif action == 2:  # accelerate
            gd.v1.accelerate()
        elif action == 3:  # decelerate
            gd.v1.decelerate()

        collided = gd.v1.move(1)
        
        # self.done = gd.v1.out_of_screen() or gd.v1.check_collisions()

        obs = np.array([gd.v1.origin['x'], gd.v1.origin['y'], gd.v1.angle, gd.v1.speed], dtype=np.float32)

        reward = 0
        if gd.v1.out_of_screen():
            reward = -gd.v1.timestamp
            self.done = True
        
        if collided:
            reward = -1000
            self.done = True

        return obs, reward, self.done, {}

    def render(self, mode='human'):
        gd.screen.fill(gd.bg)

        pg.draw.line(gd.screen, "white", (0, 250), (gd.screen.get_width(), 250), 1)
        pg.draw.line(gd.screen, "white", (0, 430), (3 * gd.screen.get_width() / 4, 430), 1)
        pg.draw.line(gd.screen, "white", (3 * gd.screen.get_width() / 4, 430), (5 * gd.screen.get_width() / 6, 340), 1)
        pg.draw.line(gd.screen, "white", (5 * gd.screen.get_width() / 6, 340), (gd.screen.get_width(), 340), 1)
        gd.v1.draw()

        pg.display.flip()

        gd.dt = gd.clock.tick(60) / 1000

    def close(self):
        pg.quit()