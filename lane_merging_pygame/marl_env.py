import pygame as pg
import GloDec as gd
import numpy as np
import gymnasium as gym
from gymnasium import spaces
import time
import functools
from pettingzoo.utils.env import ParallelEnv
from pettingzoo.utils import agent_selector


class MultipleVehicleEnv(ParallelEnv):
    metadata = {"name" : "lane-merging-v1", "render_modes" : ["human"], "render_fps" : 60}
    def __init__(self, render_mode=None):
        super(MultipleVehicleEnv, self).__init__()

        self.agents = ['v1', 'v2']
        self.possible_agents = self.agents[:]
        self.agent_selector = agent_selector(self.agents)

        self.observation_spaces = {
            agent: spaces.Box(
                low=np.array([[0, 0, -40, 0], [0, 0, -40, 0]]), 
                high=np.array([[1280, 720, 40, 200], [1280, 720, 40, 200]]), 
                dtype=np.int32
            )
            for agent in self.agents
        }
        
        self.action_spaces = {agent: spaces.Discrete(4) for agent in self.agents}

        self.done = {agent: False for agent in ['v1', 'v2']}
        self.truncated = {agent: False for agent in ['v1', 'v2']}


        self.render_mode = render_mode


        if render_mode == "human":
            pg.init()
            gd.screen = pg.display.set_mode((gd.WIDTH, gd.HEIGHT))
            gd.clock = pg.time.Clock()

    # @functools.lru_cache(maxsize=None)
    # def observation_space(self, agent):
    #     return spaces.Box(
    #         low=np.array([[0, 0, -40, 0], [0, 0, -40, 0]]), 
    #         high=np.array([[1280, 720, 40, 200], [1280, 720, 40, 200]]), 
    #         dtype=np.int32
    #     )

    # @functools.lru_cache(maxsize=None)
    # def action_space(self, agent):
    #     return spaces.Discrete(4)
    
    def reset(self, seed=None, options=None):

        self.done = {agent: False for agent in self.agents}
        self.truncated = {agent: False for agent in self.agents}
        
        gd.v1.origin = {'x': 600, 'y': 385}
        gd.v1.angle = 0
        gd.v1.speed = 60
        gd.v1.count = 0
        gd.v1.timestamp = time.time()

        gd.v2.origin = {'x': 300, 'y': 295}
        gd.v2.angle = 0
        gd.v2.speed = 60
        gd.v2.count = 0
        gd.v2.timestamp = time.time()
        
        self.agent_selector = agent_selector(self.agents)

        self.agent_selection = self.agent_selector.next() 
        return {agent : self._get_obs(agent) for agent in self.agents}, {agent : {'status' : 'reset'} for agent in self.agents}

    def step(self, actions):
        if actions['v1'] == 0:  # turn left
            gd.v1.turn(-1)
        elif actions['v1'] == 1:  # turn right
            gd.v1.turn(1)
        elif actions['v1'] == 2:  # accelerate
            gd.v1.accelerate()
        elif actions['v1'] == 3:  # decelerate
            gd.v1.decelerate()

        if actions['v2'] == 0:  # turn left
            gd.v2.turn(-1)
        elif actions['v2'] == 1:  # turn right
            gd.v2.turn(1)
        elif actions['v2'] == 2:  # accelerate
            gd.v2.accelerate()
        elif actions['v2'] == 3:  # decelerate
            gd.v2.decelerate()

        collided_v1 = gd.v1.move(1)
        collided_v2 = gd.v2.move(1)
        
        obs = {agent : self._get_obs(agent) for agent in self.agents}
        reward = {'v1' : self._get_reward('v1', collided_v1), 'v2' : self._get_reward('v2', collided_v2)}
        self.done = {'v1' : gd.v1.out_of_screen() or collided_v1, 'v2' : gd.v2.out_of_screen() or collided_v2}
        time_now = time.time()
        self.truncated = {'v1' : (time_now - gd.v1.timestamp) > 60, 'v2' : (time_now - gd.v2.timestamp) > 60}

        self.render()

        return obs, reward, self.done, self.truncated, {agent : {'status' : 'step_success'} for agent in self.agents}

    def _get_obs(self, agent):
        if agent == 'v1':
            return np.array([[gd.v1.origin['x'], gd.v1.origin['y'], gd.v1.angle, gd.v1.speed], [gd.v2.origin['x'], gd.v2.origin['y'], gd.v2.angle, gd.v2.speed]], dtype=np.int32)
        elif agent == 'v2':
            return np.array([[gd.v2.origin['x'], gd.v2.origin['y'], gd.v2.angle, gd.v2.speed], [gd.v1.origin['x'], gd.v1.origin['y'], gd.v1.angle, gd.v1.speed]], dtype=np.int32)

    def _get_reward(self, agent, collided):
        if collided:
            return -1000
        
        if agent == 'v1':
            if gd.v1.out_of_screen():
                return 100 / gd.v1.timestamp
        elif agent == 'v2':
            if gd.v2.out_of_screen():
                return 100 / gd.v2.timestamp
        
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
        gd.v2.draw()

        pg.display.flip()

        gd.dt = gd.clock.tick(60) / 1000

    def close(self):
        if self.render_mode == "human":
            pg.quit()