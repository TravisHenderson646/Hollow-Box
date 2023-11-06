from random import random, randint

import pygame as pg

from scripts.entities.physics_entity import PhysicsEntity
from scripts import setup

class Geo(PhysicsEntity):
    def __init__(self, pos, direction):
        self.size = (7, 7)
        pos = (pos[0] - 7, pos[1] - 3)
        super().__init__('geo', pos, self.size)
        self.vel = pg.Vector2(random() * direction + direction, -1 * random() - 1)
        self.ticks_since_bounce = 500
        self.bounce_active = False
        self.bounce_duration = 3
        self.restitution = 0.6
        self.rect = pg.FRect(0,0,0,0)
        self.can_bounce = True
        self.animation.frame = randint(0, len(self.animation.images * self.animation.image_dur))
        self.animation.image_dur = randint(6, 22)
            
    def picked_up(self, player):
        player.geo += 1
        
    def update(self):
        self.rect = self.hurtboxes[0]
        if self.bounce_active:
            self.ticks_since_bounce += 1
            if self.ticks_since_bounce > 2:
                self.bounce_active = False
                if abs(self.vel.y) < 0.2:
                    self.can_bounce = False
        
        if self.collisions['down']:
            if self.can_bounce:
                if not self.bounce_active:
                    self.bounce_active = True
                    self.vel.y = self.vel.y * -self.restitution
                    self.vel.x = self.vel.x * self.restitution
                    self.ticks_since_bounce = 0
            else:
                self.vel = pg.Vector2()
        elif self.collisions['up']:
            self.vel.y = 0
        elif self.collisions['left'] or self.collisions['right']:
            self.vel.x = -self.vel.x
        
                
        #gravity with terminal vel
        self.vel.y = min(self.terminal_vel, self.vel.y + self.gravity)   

        self.hot_chunk = ((self.hurtboxes[0].centerx + setup.CHUNK_SIZE[0] / 2) // setup.CHUNK_SIZE[0], (self.hurtboxes[0].centery + setup.CHUNK_SIZE[1] / 2) // setup.CHUNK_SIZE[1])
        
        self.frame_movement = pg.Vector2(self.vel.x, self.vel.y)   
        
        self.animation.tick()