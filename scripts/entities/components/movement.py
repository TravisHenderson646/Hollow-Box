import pygame as pg

from setup import CHUNK_SIZE



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
        
    def frame_start(self):
        self.vel.x = 0
        
        if self.movement.x == 1:
            self.entity.animate.flip = False
        if self.movement.x == -1:
            self.entity.animate.flip = True
            
        if self.collisions['down'] or self.collisions['up']:
            self.vel.y = 0
            
        self.vel.y = min(self.terminal_vel, self.vel.y + self.gravity)
        
        self.hot_chunk = ((self.entity.rect.centerx + CHUNK_SIZE[0] / 2) // CHUNK_SIZE[0], (self.entity.rect.centery + CHUNK_SIZE[1] / 2) // CHUNK_SIZE[1])
      
    def turn_around_at_ledge(self, tilemap):
        if self.collisions['down']:
            if self.movement.x == -1:    
                check_pos = (self.entity.rect.left - 1, self.entity.rect.bottom + 1)
            else:
                check_pos = (self.entity.rect.right + 1, self.entity.rect.bottom + 1)
            if not tilemap.check_point(check_pos, self.hot_chunk):
                self.movement.x = -self.movement.x 
        
    def bonk(self):
        if (self.collisions['right'] and (self.movement.x == 1)) or (self.collisions['left'] and (self.movement.x == -1)):
            self.movement.x = -self.movement.x

    def calculate_frame_movement(self):
        if self.vel.x:
            self.frame_movement = pg.Vector2(self.vel.x, self.vel.y)   
        else:
            self.frame_movement = pg.Vector2((self.movement.x) * self.speed, self.vel.y)  