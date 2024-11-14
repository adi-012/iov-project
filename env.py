import pygame
import math
import time

class Vehicle:
  def __init__(self, color, half_width, half_height, origin, speed=80):
    self.color = color
    self.half_width = half_width
    self.half_height = half_height
    self.origin = origin
    self.speed = speed
    self.angle = 0
    self.count = 0
    self.target_speed = speed
    self.done = False
    self.is_post_merge = False
    self.last_update_time = time.time()
  
  def get_transformed_points(self, x, y, theta=None):
        if theta == None:
          theta = self.angle
        
        angle_rad = math.radians(theta)
        cosx, sinx = math.cos(angle_rad), math.sin(angle_rad)
    
        w_c, w_s = cosx * self.half_width, sinx * self.half_width
        h_c, h_s = cosx * self.half_height, sinx * self.half_height
        
        return [
            (x + w_c - h_s, y + w_s + h_c),
            (x + w_c + h_s, y + w_s - h_c),
            (x - w_c + h_s, y - w_s - h_c),
            (x - w_c - h_s, y - w_s + h_c)
        ]
  
  def get_coordinates(self):
    return self.get_transformed_points(self.origin['x'], self.origin['y'])
    
  def get_lane(self):
    y_min = min(y[1] for y in self.get_coordinates())
    if y_min <= 330:
      return 1
    else:
      return 2
    
  def is_in_merge_zone(self):
    
    points = self.get_coordinates()
    x_min = min(x[0] for x in points)
    
    if self.origin['x'] > 400 and x_min < 5 * screen.get_width() / 6:
      return True
      
  def time_to_merge(self):
    distance = 750 - self.origin['x']
    return distance / self.speed if self.speed > 0 else float('inf')
  
  def is_past_merge(self):
    points = self.get_coordinates()
    x_min = min(x[0] for x in points)
    return x_min > 5 * screen.get_width()/6

  def accelerate(self, direction):
    if (self.count < 10 and direction > 0):
      self.count +=1
    elif (self.count > -10 and direction < 0):
      self.count -=1

    cur_time = time.time()
    
    if (cur_time - self.last_update_time >= 1):
      self.last_update_time = time.time()
      self.speed += self.count
      self.speed = max(min(200, self.speed), 0)
      if abs(self.speed - self.target_speed) < 10:
        self.speed = self.target_speed
      self.count = 0

  def check_collisions(self, rect=None):
    
    if rect == None:
      rect = self.get_coordinates()
    
    if (collide_rect_line(rect, (0,250), (screen.get_width(), 250)) or\
      collide_rect_line(rect, (0, 430), (3*screen.get_width()/4, 430)) or\
      collide_rect_line(rect, (3*screen.get_width()/4, 430), (5*screen.get_width()/6, 340)) or\
      collide_rect_line(rect, (5*screen.get_width()/6, 340), (screen.get_width(), 340))):
      return True
    for v in vehicles:
      if v == self:
        continue
      rect_temp = v.get_coordinates()
      
      if (collide_rect_rect(rect, rect_temp)):
        return True
    
    return False
    
  def out_of_screen(self):
    rect = self.get_coordinates()
    min_x = min(point[0] for point in rect)
    return (min_x > 1280)
  
  def draw(self):
    
    rect = self.get_coordinates()
    
    pygame.draw.polygon(screen, self.color, rect, 0)
    pygame.draw.line(screen, 'black', rect[0], rect[1], 1)
  
  def move(self, direction):
    
    angle_rad = math.radians(self.angle)
    cosx, sinx = math.cos(angle_rad), math.sin(angle_rad)
    
    new_x = self.origin['x'] + direction * self.speed * cosx * dt
    new_y = self.origin['y'] + direction * self.speed * sinx * dt
    
    rect = self.get_transformed_points(new_x, new_y)
    
    if not (self.check_collisions(rect)):
      self.origin['x'] = new_x
      self.origin['y'] = new_y
    
  def turn(self, direction):
    new_angle = self.angle + direction
    if -40 <= new_angle <= 40:
      angle_rad = math.radians(new_angle)
      rect = self.get_transformed_points(self.origin['x'], self.origin['y'], new_angle)
      
      if not (self.check_collisions(rect)):
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

def collide_rect_rect(rect1, rect2):
  return (collide_rect_line(rect1, rect2[0], rect2[1]) or\
    collide_rect_line(rect1, rect2[1], rect2[2]) or\
    collide_rect_line(rect1, rect2[2], rect2[3]) or\
    collide_rect_line(rect1, rect2[3], rect2[0]))
  

def manage_traffic(vehicles):
    # Sort vehicles by x position to help determine order
    # sorted_vehicles = sorted(vehicles, key=lambda v: v.origin['x'], reverse=True)
    
    for v in vehicles:
      if v.is_in_merge_zone():
        v.target_speed = 80
      if v.is_past_merge():
        v.is_post_merge = True

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0
bg = 'gray'

vehicles = []

v1 = Vehicle('red', 50, 25, {'x':600, 'y':385}, 60)
v2 = Vehicle('blue', 50, 25, {'x':300, 'y':295}, 120)

vehicles.extend([v1, v2])

while running:
  
  manage_traffic(vehicles)
  
  screen.fill(bg)
  
  for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
  
  keys = pygame.key.get_pressed()
  if keys[pygame.K_RIGHT]:
    v1.turn(1)
  if keys[pygame.K_LEFT]:
    v1.turn(-1)
  if keys[pygame.K_UP]:
    v1.accelerate(1)
  if keys[pygame.K_DOWN]:
    v1.accelerate(-1)
    
  v1.move(1)
  v2.move(1)
    
  for v in vehicles:
    if v.speed < v.target_speed:
      v.accelerate(1)
    elif v.speed > v.target_speed:
      v.accelerate(-1)
  
  min_y = min(x[1] for x in v1.get_coordinates())
  
  if (v1.origin['x'] > 800 and min_y > 320):
    v1.turn(-1)
  
  if (min_y < 275):
    if v1.angle != 0:
      v1.turn(1)
  
  
  pygame.draw.line(screen,"white",(0, 250), (screen.get_width(), 250), 1)
  pygame.draw.line(screen,"white",(0, 430), (3*screen.get_width()/4, 430), 1)
  pygame.draw.line(screen,"white",(3*screen.get_width()/4, 430), (5*screen.get_width()/6, 340), 1)
  pygame.draw.line(screen,"white",(5*screen.get_width()/6, 340), (screen.get_width(), 340), 1)
  
  for v in vehicles:
    if v.out_of_screen():
      vehicles.remove(v)
  
  v1.draw()
  v2.draw()
  
  # flip() the display to put your work on screen
  pygame.display.flip()

  # limits FPS to 60
  # dt is delta time in seconds since last frame, used for framerate-
  # independent physics.
  dt = clock.tick(20) / 1000

pygame.quit()
