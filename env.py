import pygame
import math

class Vehicle:
  def __init__(self, color, half_width, half_height, origin, angle):
    self.color = color
    self.half_width = half_width
    self.half_height = half_height
    self.origin = origin
    self.angle = angle
  
  def get_transformed_points(self, x, y, cosx, sinx):
        w_c, w_s = cosx * self.half_width, sinx * self.half_width
        h_c, h_s = cosx * self.half_height, sinx * self.half_height
        
        return [
            (x + w_c - h_s, y + w_s + h_c),
            (x + w_c + h_s, y + w_s - h_c),
            (x - w_c + h_s, y - w_s - h_c),
            (x - w_c - h_s, y - w_s + h_c)
        ]
  
  def draw(self):
    angle_rad = math.radians(self.angle)
    cosx, sinx = math.cos(angle_rad), math.sin(angle_rad)
    
    rect = self.get_transformed_points(self.origin['x'], self.origin['y'], cosx, sinx)
    
    pygame.draw.polygon(screen, self.color, rect, 0)
    pygame.draw.line(screen, 'black', rect[0], rect[1], 1)
  
  def move(self, direction):
    
    angle_rad = math.radians(self.angle)
    cosx, sinx = math.cos(angle_rad), math.sin(angle_rad)
    new_x = self.origin['x'] + direction * 150 * cosx * dt
    new_y = self.origin['y'] + direction * 150 * sinx * dt
    
    rect = self.get_transformed_points(new_x, new_y, cosx, sinx)
    
    if not (collide_rect_line(rect, (0,(screen.get_height())/4), (screen.get_width(), (screen.get_height())/4)) or\
      collide_rect_line(rect, (0,(3*screen.get_height())/4), (screen.get_width(), (3 * screen.get_height())/4))):
      self.origin['x'] = new_x
      self.origin['y'] = new_y
    
  def turn(self, direction):
    new_angle = self.angle + direction
    if -40 <= new_angle <= 40:
      angle_rad = math.radians(new_angle)
      cosx, sinx = math.cos(angle_rad), math.sin(angle_rad)
      rect = self.get_transformed_points(self.origin['x'], self.origin['y'], cosx, sinx)
      
      if not (collide_rect_line(rect, (0,(screen.get_height())/4), (screen.get_width(), (screen.get_height())/4)) or\
        collide_rect_line(rect, (0,(3*screen.get_height())/4), (screen.get_width(), (3 * screen.get_height())/4))):
        self.angle = new_angle

def collide_line_line(p1, p2, q1, q2):
  d = (p2[0]-p1[0]) * (q2[1]-q1[1]) + (p2[1]-p1[1]) * (q1[0]-q2[0]) 
  if d == 0:
    return False
  t = ((q1[0]-p1[0]) * (q2[1]-q1[1]) + (q1[1]-p1[1]) * (q1[0]-q2[0])) / d
  u = ((q1[0]-p1[0]) * (p2[1]-p1[1]) + (q1[1]-p1[1]) * (p1[0]-p2[0])) / d
  return 0 <= t <= 1 and 0 <= u <= 1

def collide_rect_line(rect, p1, p2):
  return (collide_line_line(rect[0], rect[1], p1, p2) or\
    collide_line_line(rect[1], rect[2], p1, p2) or\
    collide_line_line(rect[2], rect[3], p1, p2) or\
    collide_line_line(rect[3], rect[0], p1, p2))

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0
bg = 'gray'

v1 = Vehicle('red', 50, 25, {'x':600, 'y':400}, 0)

while running:
  
  screen.fill(bg)
  
  for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
  
  keys = pygame.key.get_pressed()
  if keys[pygame.K_UP]:
    v1.move(1)
  if keys[pygame.K_DOWN]:
    v1.move(-1)
  if keys[pygame.K_RIGHT]:
    v1.turn(1)
  if keys[pygame.K_LEFT]:
    v1.turn(-1)
  
  pygame.draw.line(screen,"white",(0,(screen.get_height())/4), (screen.get_width(), (screen.get_height())/4), 1)
  pygame.draw.line(screen,"white",(0,(3 * screen.get_height())/4), (screen.get_width(), (3*screen.get_height())/4), 1)
  
  v1.draw()
  
  # flip() the display to put your work on screen
  pygame.display.flip()

  # limits FPS to 60
  # dt is delta time in seconds since last frame, used for framerate-
  # independent physics.
  dt = clock.tick(60) / 1000

pygame.quit()