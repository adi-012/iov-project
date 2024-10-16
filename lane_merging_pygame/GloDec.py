import pygame as pg
from vehicle import Vehicle

WIDTH = 1280
HEIGHT = 720

screen = pg.display.set_mode((WIDTH, HEIGHT))
clock = pg.time.Clock()
dt = 0
bg = 'gray'

vehicles = []

v1 = Vehicle('red', 50, 25, {'x':600, 'y':385}, 0)
# v2 = Vehicle('blue', 50, 25, {'x':300, 'y':295}, 0)

vehicles.extend([v1])

running = True