import math

import pygame as pg

class Spark:
    def __init__(self, color, pos, speed, angle):
        self.pos = list(pos)
        self.angle = angle
        self.speed = speed
        self.color = color
        
    def update(self):
        self.pos[0] += math.cos(self.angle) * self.speed
        self.pos[1] += math.sin(self.angle) * self.speed
        
        self.speed = max(0, self.speed - 0.05)
        return not self.speed
    
    def render(self, canvas, offset):
        render_points = [
            (self.pos[0] + math.cos(self.angle                ) * self.speed - offset[0], self.pos[1] + math.sin(self.angle                ) * self.speed - offset[1]),
            (self.pos[0] + math.cos(self.angle + math.pi * 0.5) * self.speed - offset[0], self.pos[1] + math.sin(self.angle + math.pi * 0.5) * self.speed - offset[1]),
            (self.pos[0] + math.cos(self.angle + math.pi      ) * self.speed - offset[0], self.pos[1] + math.sin(self.angle + math.pi      ) * self.speed - offset[1]),
            (self.pos[0] + math.cos(self.angle + math.pi * 1.5) * self.speed - offset[0], self.pos[1] + math.sin(self.angle + math.pi * 1.5) * self.speed - offset[1])
        ]
        
        pg.draw.polygon(canvas, self.color, render_points)