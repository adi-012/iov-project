import pygame as pg
import GloDec as gd
import numpy as np
import gymnasium as gym
from gymnasium import spaces
import time
from gymnasium.envs.registration import register

register(
    id='lane-merging-v0',                                
    entry_point='rl_env:VehicleEnv',
)
class VehicleEnv(gym.Env):
    metadata = {"render_modes" : ["human"], "render_fps" : 60}
    def __init__(self, render_mode=None):
        super(VehicleEnv, self).__init__()

        self.granularity = 20

        self.action_space = spaces.Discrete(5)
        self.observation_space = spaces.Box(low=np.array([0 // self.granularity, 0 // self.granularity, -40, 0, 0, 0, 0, 0, 0, 0, 0, 0]), 
                                            high=np.array([1280 // self.granularity, 720 // self.granularity, 40, 200, 50, 50, 50, 50, 50, 50, 50, 50]), 
                                            dtype=np.int32)
        
        self.render_mode = render_mode        
        self.done = False
        self.truncated = False

        self.init_pos = gd.v1.origin.copy()

        if render_mode == "human":
            pg.init()
            gd.screen = pg.display.set_mode((gd.WIDTH, gd.HEIGHT))
            gd.clock = pg.time.Clock()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.done = False
        self.truncated = False
        gd.v1.origin = {'x': np.random.randint(100, 701), 'y': 385}
        gd.v1.angle = 0
        gd.v1.speed = np.random.randint(30, 121)
        gd.v1.count = 0
        gd.v1.last_update_time = None
        gd.v1.timestamp = time.time()

        gd.v2.origin = {'x': np.random.randint(100, 901), 'y': 295}
        gd.v2.angle = 0
        gd.v2.speed = np.random.randint(30, 121)
        gd.v2.count = 0
        gd.v2.last_update_time = None
        gd.v2.timestamp = time.time()

        self.init_pos = gd.v1.origin.copy()

        return self._get_obs(), {'status' : 'reset'}

    def step(self, action):
        acceleration = 0

        if action == 0:  # turn left
            gd.v1.turn(-1)
        elif action == 1:  # turn right
            gd.v1.turn(1)
        elif action == 2:  # accelerate
            gd.v1.accelerate()
            acceleration = 1
        elif action == 3:  # decelerate
            gd.v1.decelerate()
            acceleration -1
        else:
            acceleration = 0


        collided = gd.v1.move(1)
        v2_collision = gd.v2.move(1)
        collided = collided or v2_collision
        
        self.truncated = (time.time() - gd.v1.timestamp) > 30
        obs = self._get_obs()
        danger = min(50, min(obs[i + 3] for i in range(8)))
        self.done = gd.v1.out_of_screen() or collided
        reward = self._get_reward(collided, acceleration, self.truncated, danger)

        self.render()

        return obs, reward, self.done, self.truncated, {"status" : "step_success"}

    def _get_obs(self):
        safety = gd.v1.safety_distance()
        return np.array([gd.v1.origin['x'] // self.granularity, gd.v1.origin['y'] // self.granularity, gd.v1.angle, gd.v1.speed,
                         safety[0], safety[1], safety[2], safety[3], safety[4], safety[5], safety[6], safety[7]], dtype=np.int32)

    def _get_reward(self, collided, acceleration, isTruncated, danger):
        if isTruncated:
            # print("STAGNATED")
            return -10000
        if gd.v1.out_of_screen():
            # print("DONE")
            return 10000 / (time.time() - gd.v1.timestamp)
        if collided:
            # print("SAD but travelled " + str(gd.v1.origin['x'] - self.init_pos['x']))
            return -10000 + gd.v1.origin['x'] - self.init_pos['x']
        if danger < 10:
            # print("DANGER = ", danger)
            return -(10 - danger)
        
        return min(acceleration, 0)

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
        gd.v2.draw()

        pg.display.flip()

        gd.dt = gd.clock.tick(60) / 1000

    def close(self):
        if self.render_mode == "human":
            pg.quit()