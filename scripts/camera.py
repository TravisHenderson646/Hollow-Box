from math import floor

import pygame as pg

class Camera:
    def __init__(self):
        self.pos = pg.Vector2()
        self.rounded_pos = [0, 0] # try ': tuple[(int, int)]'
        
        #premenition about what will be useful
        self.max_x = 999999
        self.max_y = 999999
        
    def update(self):
        self.rounded_pos[0] = min(floor(self.pos.x), self.max_x)
        self.rounded_pos[1] = min(floor(self.pos.y), self.max_y)