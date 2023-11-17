from random import random, randint
from math import floor

import pygame as pg

from scripts.entities.components.movement import Movement
from scripts.entities.components.animate import Animate
from scripts.setup import CHUNK_SIZE

class Geo:
    def __init__(self, pos, direction):
        self.name = 'geo'
        self.size = (7, 7)
        pos = (pos[0] - self.size[0], pos[1] - 3)
        self.rect = pg.FRect(*pos, *self.size)
        self.dead = False
        
        self.movement = Movement(self)
        self.movement.vel = pg.Vector2(random() * direction + direction, -1 * random() - 1)
        
        self.animate = Animate(self)
        self.animate.animation.image_dur = randint(6, 22)
        self.animate.animation.frame = randint(0, len(self.animate.animation.images * self.animate.animation.image_dur))
        
        self.ticks_since_bounce = 500
        self.bounce_active = False
        self.bounce_duration = 3
        self.restitution = 0.6
        self.can_bounce = True
        
    def picked_up(self, player):
        player.geo += 1
        # todo play sfx here
        
    def update(self, tilemap, player):
        if self.bounce_active:
            self.ticks_since_bounce += 1
            if self.ticks_since_bounce > 2:
                self.bounce_active = False
                if abs(self.movement.vel.y) < 0.2:
                    self.can_bounce = False
                    
        if self.movement.collisions['down']:
            if self.can_bounce:
                if not self.bounce_active:
                    self.bounce_active = True
                    self.movement.vel.y = self.movement.vel.y * - self.restitution
                    self.movement.vel.x = self.movement.vel.x * self.restitution
            else:
                self.movement.vel = pg.Vector2()
        elif self.movement.collisions['up']:
            self.movement.vel.y = 0
        elif self.movement.collisions['left'] or self.movement.collisions['right']:
            self.movement.vel.x = -self.movement.vel.x
            
        self.movement.vel.y = min(self.movement.terminal_vel, self.movement.vel.y + self.movement.gravity)
        
        self.movement.hot_chunk = ((self.rect.centerx + CHUNK_SIZE[0] / 2) // CHUNK_SIZE[0], (self.rect.centery + CHUNK_SIZE[1] / 2) // CHUNK_SIZE[1])
        
        self.movement.calculate_frame_movement()
        
        self.movement.collide_with_tilemap(tilemap)
        
        if self.rect.colliderect(player.rect):
            self.picked_up(player)
            self.dead = True
            
        self.animate.animation.tick() 
            
    def render(self, canvas:pg.Surface, offset):
        self.animate.render(canvas, offset)