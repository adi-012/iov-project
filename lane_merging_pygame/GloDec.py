import pygame as pg
from vehicle import Vehicle
import numpy as np

WIDTH = 1280
HEIGHT = 720

screen = None
clock = None
dt = 0.016
bg = 'gray'

vehicles = []

v1 = Vehicle('red', 50, 25, {'x':np.random.randint(100, 701), 'y':385}, 0, np.random.randint(30, 121))
v2 = Vehicle('blue', 50, 25, {'x':np.random.randint(100, 701), 'y':295}, 0, np.random.randint(30, 121))

vehicles.extend([v1, v2])

running = True