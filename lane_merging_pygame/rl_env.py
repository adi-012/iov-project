import pygame as pg
import GloDec as gd
import numpy as np
import gymnasium as gym
from gymnasium import spaces
import time
from gymnasium.envs.registration import register

register(
    id='lane-merging-v0',                                # call it whatever you want
    entry_point='rl_env:VehicleEnv', # module_name:class_name
)
class VehicleEnv(gym.Env):
    def __init__(self, render_mode=None):
        super(VehicleEnv, self).__init__()

        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(low=np.array([0, 0, -40, 0]), 
                                            high=np.array([1280, 720, 40, 200]), 
                                            dtype=np.int32)
        
        self.render_mode = render_mode        
        self.done = False
        self.truncated = False

        if render_mode == "human":
            pg.init()
            gd.screen = pg.display.set_mode((gd.WIDTH, gd.HEIGHT))
            gd.clock = pg.time.Clock()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.done = False
        self.truncated = False
        gd.v1.origin = {'x': 600, 'y': 385}
        gd.v1.angle = 0
        gd.v1.speed = 60
        gd.v1.count = 0
        gd.v1.last_update_time = None
        gd.v1.timestamp = time.time()

        self.render()

        return self._get_obs(), {'status' : 'reset'}

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
        
        obs = self._get_obs()
        reward = self._get_reward(collided)
        self.done = gd.v1.out_of_screen() or collided
        self.truncated = (time.time() - gd.v1.timestamp) > 60

        self.render()

        return obs, reward, self.done, self.truncated, {"status" : "step_success"}

    def _get_obs(self):
        return np.array([gd.v1.origin['x'], gd.v1.origin['y'], gd.v1.angle, gd.v1.speed], dtype=np.int32)

    def _get_reward(self, collided):
        if gd.v1.out_of_screen():
            return 100 / gd.v1.timestamp
        if collided:
            return -1000
        return -1

    def render(self):
        if self.render_mode == "human":
            return self._render_frame()

    def _render_frame(self):
        gd.screen.fill(gd.bg)

        pg.draw.line(gd.screen, "white", (0, 250), (gd.screen.get_width(), 250), 1)
        pg.draw.line(gd.screen, "white", (0, 430), (3 * gd.screen.get_width() / 4, 430), 1)
        pg.draw.line(gd.screen, "white", (3 * gd.screen.get_width() / 4, 430), (5 * gd.screen.get_width() / 6, 340), 1)
        pg.draw.line(gd.screen, "white", (5 * gd.screen.get_width() / 6, 340), (gd.screen.get_width(), 340), 1)
        
        gd.v1.draw()

        pg.display.flip()

        gd.dt = gd.clock.tick(60) / 1000

    def close(self):
        if self.render_mode == "human":
            pg.quit()