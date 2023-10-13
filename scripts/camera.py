from math import floor

import pygame as pg

from scripts.setup import CANVAS_SIZE
from scripts.debugger import debugger

class Camera:
    def __init__(self):
        self.rounded_pos = [0, 0] # try ': tuple[(int, int)]'
        self.cage = pg.Rect(0, 0, CANVAS_SIZE[0] // 8, CANVAS_SIZE[1] // 4) # Move camera if player leaves this
        
        #premenition about what will be useful
        self.max_x = 999999
        self.max_y = 999999
        
    def update(self, pos):
        if pos[0] < self.cage.left:
            self.cage.left = pos[0]
        if pos[0] > self.cage.right:
            self.cage.right = pos[0]
        if pos[1] < self.cage.top:
            self.cage.top = pos[1]
        if pos[1] > self.cage.bottom:
            self.cage.bottom = pos[1]
            
        self.rounded_pos = [self.cage.centerx - CANVAS_SIZE[0] // 2, self.cage.centery - CANVAS_SIZE[1] // 2] # magic numbers
        
        
        
        
        
       # self.rounded_pos[0] = min(floor(self.pos.x), self.max_x)
        #self.rounded_pos[1] = min(floor(self.pos.y), self.max_y)