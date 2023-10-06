import math
import random

import pygame as pg

from scripts.particle import Particle
from scripts.spark import Spark
from scripts import setup
from .physics_entity import PhysicsEntity


class Enemy(PhysicsEntity):
    def __init__(self, pos, size):
        super().__init__('enemy', pos, size)
        
        self.walking = 0
        self.movement = [0, 0, 0, 0] # desired L/R movement of entity???
        
    def update(self, tilemap, player_rect, player_dashing, projectiles, sparks, particles, movement=(0, 0)):
        if self.walking:
            if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.pos[1] + 23)):
                if (self.collisions['right'] or self.collisions['left']):
                    self.flip = not self.flip
                movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
            else:
                self.flip = not self.flip
            self.walking = max(0, self.walking - 1)
            ### Enemies shoot at player
            ###### GAME this block should be moved into the level
            if not self.walking: #should happen only 1 frame bc we're inside a if self.walking cond
                dist = (player_rect.x - self.pos[0], player_rect.y - self.pos[1]) 
                if (abs(dist[1]) < 80):
                    if (self.flip and dist[0] < 0):
                        setup.sfx['shoot'].play()
                        projectiles.append([[self.rect().centerx - 7, self.rect().centery], -1.5, 0])
                        for i in range(4):
                            sparks.append(Spark(projectiles[-1][0], random.random() - 0.5 + math.pi, 2 + random.random()))
                    if (not self.flip and dist[0]> 0):
                        setup.sfx['shoot'].play()
                        projectiles.append([[self.rect().centerx + 7, self.rect().centery], 1.5, 0])
                        for i in range(4):
                            sparks.append(Spark(projectiles[-1][0], random.random() - 0.5, 2 + random.random()))
            ###
        elif random.random() < 0.01:
            self.walking = random.randint(30, 120)
        
        super().update(tilemap, movement=movement) #handles physics in parent class
        
        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')
            
        if abs(player_dashing) >= 50: 
            if self.rect().colliderect(player_rect):
                setup.sfx['hit'].play()
                for i in range(30):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                    particles.append(Particle('particle', self.rect().center, vel=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
                sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                return True
            
    def render(self, surf, offset):
        super().render(surf, offset)
        
        if self.flip:
            surf.blit(pg.transform.flip(setup.assets['gun'], True, False), (self.rect().centerx - 4 - setup.assets['gun'].get_width() - offset[0], self.rect().centery - offset[1]))
        else:
            surf.blit(setup.assets['gun'], (self.rect().centerx + 4 - offset[0], self.rect().centery - offset[1]))
