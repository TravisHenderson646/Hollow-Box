import pygame as pg

from scripts.particle import Particle
from scripts.spark import Spark
from scripts import setup

class PhysicsEntity:
    def __init__(self, entity_type, pos, size):
        self.entity_type = entity_type
        self.pos = pg.Vector2(pos)
        self.size = size
        self.vel = pg.Vector2(0, 0) # velocity imparted from other action
        self.speed = 1
        self.collisions = {'up': False, 'down': False, 'left': False, 'right': False}
        
        self.animation = ''
        self.last_movement = [0, 0, 0, 0]
        self.anim_offset = pg.Vector2(0, 0) #todo: this apparently a hack soln to match the idle to the run img padding and more
        self.flip = False
        self.set_animation('idle')
        
        
        self.test_surf = pg.Surface(size)
        self.test_surf.fill((200, 0, 0))
        self.test_pos = self.pos
        
    def rect(self): # This version is better trust, think about it
        return pg.Rect(*self.pos, *self.size)
    
    def set_animation(self, animation):
        if animation !=self.animation:
            self.animation = animation
            self.animation = setup.assets[self.entity_type + '/' + self.animation].copy() # game from tools instead maybe... maybe call this set animation and update it from a layer above like entities.updateanimation()
        
    def update(self, movement):
        self.test_pos = self.pos 
                
        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True
        
        self.last_movement = movement
        
        #gravity with terminal vel
        self.vel.y = min(5, self.vel.y + 0.1)
            
        self.animation.tick()
        
    def render(self, surf:pg.Surface, offset):
        surf.blit(pg.transform.flip(self.animation.img(), self.flip, False), (self.pos - offset + self.anim_offset))