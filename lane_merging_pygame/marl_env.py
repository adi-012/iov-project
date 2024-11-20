import pygame as pg
import GloDec as gd
import numpy as np
import gymnasium as gym
from gymnasium import spaces
import time
import functools
from pettingzoo.utils.env import ParallelEnv
from pettingzoo.utils import agent_selector
from gymnasium.envs.registration import register

register(
    id='lane-merging-v1',                                
    entry_point='marl_env:MultipleVehicleEnv',
)

class MultipleVehicleEnv(ParallelEnv):
    metadata = {"name" : "lane-merging-v1", "render_modes" : ["human"], "render_fps" : 60}
    def __init__(self, render_mode=None, seed = None, **kwargs):
        super(MultipleVehicleEnv, self).__init__()

        self.agents = ['v1', 'v2']
        self.possible_agents = self.agents[:]
        self.agent_selector = agent_selector(self.agents)
        self.episode_limit = 3000
        self.granulation = 20

        self.observation_spaces = {
            agent: spaces.Box(
                low=np.array([[0 // self.granularity, 0 // self.granularity, -40, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0 // self.granularity, 0 // self.granularity, -40, 0, 0, 0, 0, 0, 0, 0, 0, 0]]), 
                high=np.array([[1280 // self.granularity, 720 // self.granularity, 40, 200, 50, 50, 50, 50, 50, 50, 50, 50], [1280 // self.granularity, 720 // self.granularity, 40, 200, 50, 50, 50, 50, 50, 50, 50, 50]]), 
                dtype=np.int32
            )
            for agent in self.agents
        }
        
        self.action_spaces = {agent: spaces.Discrete(5) for agent in self.agents}

        self.done = {agent: False for agent in ['v1', 'v2']}
        self.truncated = {agent: False for agent in ['v1', 'v2']}


        self.render_mode = render_mode
        self.seed = seed

        if not self.seed:
            np.random.seed(self.seed)

        if render_mode == "human":
            pg.init()
            gd.screen = pg.display.set_mode((gd.WIDTH, gd.HEIGHT))
            gd.clock = pg.time.Clock()

    def get_env_info(self):
        # Adjust these shapes based on the expected input sizes by your model or buffer
        obs_shape = self.observation_spaces['v1'].shape[0] * self.observation_spaces['v1'].shape[1]
        state_shape = obs_shape * len(self.agents)
        
        return {
            "n_agents": len(self.agents),
            "obs_shape": obs_shape,
            "state_shape": state_shape,
            "n_actions": self.action_spaces['v1'].n,
            "episode_limit": 3000
        }


    def get_state(self):
        # Flatten the observation arrays for each agent and concatenate them
        state = np.concatenate([
            self._get_obs(agent).flatten() for agent in self.agents
        ])
        return state

    def get_avail_actions(self):
        # Each agent has 4 discrete actions available (0 to 3), return the same for each agent
        return {agent: [1] * self.action_spaces[agent].n for agent in self.agents}

    def get_obs(self):
        # Flatten the observation arrays for each agent and concatenate them
        obs = np.concatenate([
            self._get_obs(agent).flatten() for agent in self.agents
        ])
        return obs

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
        
        gd.v1.origin = {'x': np.random.randint(100, 901), 'y': 385}
        gd.v1.angle = 0
        gd.v1.speed = np.random.randint(30, 121)
        gd.v1.count = 0
        gd.v1.timestamp = time.time()

        gd.v2.origin = {'x': np.random.randint(100, 901), 'y': 295}
        gd.v2.angle = 0
        gd.v2.speed = np.random.randint(30, 121)
        gd.v2.count = 0
        gd.v2.timestamp = time.time()
        
        self.agent_selector = agent_selector(self.agents)

        self.agent_selection = self.agent_selector.next() 
        return {agent : self._get_obs(agent) for agent in self.agents}, {agent : {'status' : 'reset'} for agent in self.agents}

    def step(self, actions):
        acceleration1 = 0
        if actions['v1'] == 0:  # turn left
            gd.v1.turn(-1)
        elif actions['v1'] == 1:  # turn right
            gd.v1.turn(1)
        elif actions['v1'] == 2:  # accelerate
            gd.v1.accelerate()
            acceleration1 = 1
        elif actions['v1'] == 3:  # decelerate
            gd.v1.decelerate()
            acceleration1 = -1
        elif actions['v1'] == 4:
            acceleration1 = 0

        acceleration2 = 0
        if actions['v2'] == 0:  # turn left
            gd.v2.turn(-1)
        elif actions['v2'] == 1:  # turn right
            gd.v2.turn(1)
        elif actions['v2'] == 2:  # accelerate
            gd.v2.accelerate()
            acceleration2 = 1
        elif actions['v2'] == 3:  # decelerate
            gd.v2.decelerate()
            acceleration2 = -1
        elif actions['v2'] == 4:
            acceleration2 = 0

        collided_v1 = gd.v1.move(1)
        collided_v2 = gd.v2.move(1)
        
        obs = {agent : self._get_obs(agent) for agent in self.agents}
        reward = {'v1' : self._get_reward(collided, acceleration, self.truncated, danger), 'v2' : self._get_reward('v2', collided_v2)}
        self.done = {'v1' : gd.v1.out_of_screen() or collided_v1, 'v2' : gd.v2.out_of_screen() or collided_v2}
        time_now = time.time()
        self.truncated = {'v1' : (time_now - gd.v1.timestamp) > 60, 'v2' : (time_now - gd.v2.timestamp) > 60}

        self.render()

        return obs, reward, self.done, self.truncated, {agent : {'status' : 'step_success'} for agent in self.agents}

    def _get_obs(self, agent):
        safety1 = gd.v1.safety_distance()
        safety2 = gd.v2.safety_distance()
        if agent == 'v1':
            return np.array([[gd.v1.origin['x'] // self.granularity, gd.v1.origin['y'] // self.granularity, gd.v1.angle, gd.v1.speed,
                         safety1[0], safety1[1], safety1[2], safety1[3], safety1[4], safety1[5], safety1[6], safety1[7]], 
                         [gd.v2.origin['x'] // self.granularity, gd.v2.origin['y'] // self.granularity, gd.v2.angle, gd.v2.speed,
                         safety2[0], safety2[1], safety2[2], safety2[3], safety2[4], safety2[5], safety2[6], safety2[7]]], dtype=np.int32)
        elif agent == 'v2':
            return np.array([[gd.v2.origin['x'] // self.granularity, gd.v2.origin['y'] // self.granularity, gd.v2.angle, gd.v2.speed,
                         safety2[0], safety2[1], safety2[2], safety2[3], safety2[4], safety2[5], safety2[6], safety2[7]], 
                         [gd.v1.origin['x'] // self.granularity, gd.v1.origin['y'] // self.granularity, gd.v1.angle, gd.v1.speed,
                         safety1[0], safety1[1], safety1[2], safety1[3], safety1[4], safety1[5], safety1[6], safety1[7]]], dtype=np.int32)

    def _get_reward(self, agent, collided, acceleration, isTruncated, danger):
        if isTruncated:
            # print("STAGNATED")
            return -10000
        if agent is 'v1':
            if gd.v1.out_of_screen():
                # print("DONE")
                return 10000 / gd.v1.timestamp
        else:
            if gd.v2.out_of_screen():
                # print("DONE")
                return 10000 / gd.v1.timestamp       
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