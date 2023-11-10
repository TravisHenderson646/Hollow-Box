import pygame as pg



class Movement:
    def __init__(self, entity):
        self.entity = entity
        self.movement = pg.Vector2() # input movement of entity
        self.speed = 1
        self.vel = pg.Vector2()
        
        self.collisions = {'up': False, 'down': False, 'left': False, 'right': False}
        self.frame_movement = pg.Vector2()
        self.hot_chunk = (0, 0)
        
        self.gravity = 0.11
        self.terminal_vel = 3

    def calculate_frame_movement(self):
        if self.vel.x:
            self.frame_movement = pg.Vector2(self.vel.x, self.vel.y)   
        else:
            self.frame_movement = pg.Vector2((self.movement.x) * self.speed, self.vel.y)  