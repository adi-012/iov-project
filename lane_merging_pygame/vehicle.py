import pygame
import math
import time
import GloDec as gd

class Vehicle:
    def __init__(self, color, half_width, half_height, origin, angle, speed=60, count=0, last_update_time=None):
        self.color = color
        self.half_width = half_width
        self.half_height = half_height
        self.origin = origin
        self.angle = angle
        self.speed = speed
        self.count = count
        self.last_update_time = last_update_time
        self.timestamp = time.time()

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
    
    def accelerate(self):
        # print(f"Current Speed: {self.speed}")
        if self.count < 5:
            self.count += 1
        if self.last_update_time is None:
            last_update_time = time.time()
            self.speed += self.count
            self.speed = min(200, self.speed)
            self.count = 0
            return

        cur_time = time.time()
        if (cur_time - self.last_update_time) >= 1:
            last_update_time = time.time()
            self.speed += self.count
            self.speed = min(200, self.speed)
            self.count = 0

    def decelerate(self):
        # print(f"Current Speed: {self.speed}")
        if self.count < 5:
            self.count += 1
        if self.last_update_time is None:
            last_update_time = time.time()
            self.speed -= self.count
            self.speed = max(0, self.speed)
            self.count = 0
            return

        cur_time = time.time()
        if (cur_time - self.last_update_time) >= 1:
            last_update_time = time.time()
            self.speed -= self.count
            self.speed = max(0, self.speed)
            self.count = 0


    def _collide_line_line(self, p1, p2, q1, q2):
        d = (p2[0]-p1[0]) * (q2[1]-q1[1]) + (p2[1]-p1[1]) * (q1[0]-q2[0]) 
        if d == 0:
            return False
        t = ((q1[0]-p1[0]) * (q2[1]-q1[1]) + (q1[1]-p1[1]) * (q1[0]-q2[0])) / d
        u = ((q1[0]-p1[0]) * (p2[1]-p1[1]) + (q1[1]-p1[1]) * (p1[0]-p2[0])) / d
        return 0 <= t <= 1 and 0 <= u <= 1

    def _collide_rect_line(self, rect, p1, p2):
        return (self._collide_line_line(rect[0], rect[1], p1, p2) or
                self._collide_line_line(rect[1], rect[2], p1, p2) or
                self._collide_line_line(rect[2], rect[3], p1, p2) or
                self._collide_line_line(rect[3], rect[0], p1, p2))

    def _collide_rect_rect(self, rect1, rect2):
        return (self._collide_rect_line(rect1, rect2[0], rect2[1]) or
                self._collide_rect_line(rect1, rect2[1], rect2[2]) or
                self._collide_rect_line(rect1, rect2[2], rect2[3]) or
                self._collide_rect_line(rect1, rect2[3], rect2[0]))
    
    def check_collisions(self, rect=None):

        if rect == None:
            rect = self.get_coordinates()

        if (self._collide_rect_line(rect, (0,250), (gd.screen.get_width(), 250)) or\
            self._collide_rect_line(rect, (0, 430), (3*gd.screen.get_width()/4, 430)) or\
            self._collide_rect_line(rect, (3*gd.screen.get_width()/4, 430), (5*gd.screen.get_width()/6, 340)) or\
            self._collide_rect_line(rect, (5*gd.screen.get_width()/6, 340), (gd.screen.get_width(), 340))):
            return True
        
        for v in gd.vehicles:
            if v == self:
                continue

            rect_temp = v.get_coordinates()
            
            if (self._collide_rect_rect(rect, rect_temp)):
                return True
            
        return False

    def out_of_screen(self):
        rect = self.get_coordinates()
        min_x = min(point[0] for point in rect)
        
        if min_x > 1280:
            self.timestamp = time.time() - self.timestamp
            return True;
        else:
            return False
        
    def draw(self):

        rect = self.get_coordinates()

        pygame.draw.polygon(gd.screen, self.color, rect, 0)
        pygame.draw.line(gd.screen, 'black', rect[0], rect[1], 1)

    def move(self, direction):
        angle_rad = math.radians(self.angle)
        cosx, sinx = math.cos(angle_rad), math.sin(angle_rad)

        new_x = self.origin['x'] + direction * self.speed * cosx * gd.dt
        new_y = self.origin['y'] + direction * self.speed * sinx * gd.dt

        rect = self.get_transformed_points(new_x, new_y)

        if not (self.check_collisions(rect)):
            self.origin['x'] = new_x
            self.origin['y'] = new_y
            return False
        else:
            return True

    def turn(self, direction):
        new_angle = self.angle + direction
        if -40 <= new_angle <= 40:
            angle_rad = math.radians(new_angle)
            rect = self.get_transformed_points(self.origin['x'], self.origin['y'], new_angle)
            
            if not (self.check_collisions(rect)):
                self.angle = new_angle
                return False
            else:
                return True

