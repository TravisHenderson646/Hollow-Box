import math
import random

import pygame as pg

from scripts.particle import Particle
from scripts.spark import Spark
from scripts import setup

class PhysicsEntity:
    def __init__(self, entity_type, pos, size):
        self.entity_type = entity_type
        self.pos = pg.Vector2(pos)
        self.size = size
        self.vel = pg.Vector2(0, 0)
        self.collisions = {'up': False, 'down': False, 'left': False, 'right': False}
        
        self.action = ''
        self.last_movement = [0, 0]
        self.anim_offset = pg.Vector2(-3, -3) #todo: this apparently a hack soln to match the idle to the run img padding and more
        self.flip = False
        self.set_action('idle')
        
        
        self.test_surf = pg.Surface(size)
        self.test_surf.fill((200, 0, 0))
        self.test_pos = self.pos
        
    def rect(self):
        return pg.Rect(*self.pos, *self.size)
    
    def set_action(self, action):
        if action !=self.action:
            self.action = action
            self.animation = setup.assets[self.entity_type + '/' + self.action].copy() # game from tools instead maybe... maybe call this set animation and update it from a layer above like entities.updateanimation()
        
    def update(self, tilemap, movement=(0, 0)):
        self.collisions = {'up': False, 'down': False, 'left': False, 'right': False}

        frame_movement = pg.Vector2(movement[0] + self.vel.x, movement[1] + self.vel.y)
     # this movement should be in the generic level class
     # if i had this movement in the level, there could more easily be different blocks
     # that dont just simply body block the player
        self.pos.x += frame_movement.x
        entity_rect = self.rect()
        for rect, type in tilemap.physics_rects_near(self.pos):
            if not type:
                if entity_rect.colliderect(rect):
                    if frame_movement.x > 0:
                        entity_rect.right = rect.left
                        self.collisions['right'] = True
                    if frame_movement.x < 0:
                        entity_rect.left = rect.right
                        self.collisions['left'] = True
                    self.pos.x = entity_rect.x
        
        self.pos.y += frame_movement.y
        entity_rect = self.rect()
        for rect, type in tilemap.physics_rects_near(self.pos):
            if not type:
                if entity_rect.colliderect(rect):
                    if frame_movement.y > 0:
                        entity_rect.bottom = rect.top
                        self.collisions['down'] = True
                    if frame_movement.y < 0:
                        entity_rect.top = rect.bottom
                        self.collisions['up'] = True
                    self.pos.y = entity_rect.y
                
        self.test_pos = self.pos 
                
        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True
        
        self.last_movement = movement
        
        #gravity with terminal vel
        self.vel.y = min(5, self.vel.y + 0.1)
        
        if self.collisions['down'] or self.collisions['up']:
            self.vel.y = 0
            
        self.animation.update()
        
    def render(self, surf:pg.Surface, offset):
        surf.blit(pg.transform.flip(self.animation.img(), self.flip, False), (self.pos - offset + self.anim_offset)) # maybe they should go in the same direction
