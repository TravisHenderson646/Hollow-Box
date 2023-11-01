from math import floor

import pygame as pg

from scripts.particle import Particle
from scripts.spark import Spark
from scripts import setup
from scripts.debugger import debugger
class PhysicsEntity:
    def __init__(self, name, pos, size):
        self.name = name
        self.hitboxes = [pg.FRect(*pos, *size)]
        self.hurtboxes = [pg.FRect(*pos, *size)]
        self.vel = pg.Vector2(0, 0) # velocity imparted from other action
        self.speed = 1
        self.collisions = {'up': False, 'down': False, 'left': False, 'right': False}
        self.movement = pg.Vector2() # input movement of entity
        self.terminal_vel = 3
        self.animation = ''
        self.last_movement = pg.Vector2()
        self.anim_offset = pg.Vector2(0, 0)
        self.flip = False
        self.set_animation('idle') # could use self.animation_flag
        self.frame_movement = pg.Vector2(0, 0)        
        self.hot_chunk = (0, 0)
        self.dead = False
        self.hit_by_spike = False
        self.ticks_since_got_hit = 500
        self.got_hit_direction = 0 # 0right 1down 2left 3up
        self.invulnerable = False
        self.gravity = 0.11

    
    def set_animation(self, animation):
        if animation !=self.animation:
            self.animation = animation
            self.animation = setup.assets[self.name + '/' + self.animation].copy() # game from tools instead maybe... maybe call this set animation and update it from a layer above like entities.updateanimation()
        
    def update(self):
        self.vel.x = 0
        
        if self.hp <= 0:
            self.dead = True
        
        if self.movement.x == 1:
            self.flip = False
        if self.movement.x == -1:
            self.flip = True
        
        self.last_movement = self.movement
        
        # Important that this happens then gravity so the player hits the ground every tick
        if self.collisions['down'] or self.collisions['up']:
            self.vel.y = 0
        #gravity with terminal vel
        self.vel.y = min(self.terminal_vel, self.vel.y + self.gravity)   

        self.hot_chunk = ((self.hurtboxes[0].centerx + setup.CHUNK_SIZE[0] / 2) // setup.CHUNK_SIZE[0], (self.hurtboxes[0].centery + setup.CHUNK_SIZE[1] / 2) // setup.CHUNK_SIZE[1])
        #self.animation.tick(self.animation_flag) also shouldn't this be at the end of the update? it will be off by 1 frame
        self.animation.tick()
        
    # !!ALWAYS call this at the very end of every entities update function!!!                    
    def calculate_frame_movement(self):
        if self.vel.x:
            self.frame_movement = pg.Vector2(self.vel.x, self.vel.y)   
        else:
            self.frame_movement = pg.Vector2((self.movement.x) * self.speed, self.vel.y)    


    def render(self, surf:pg.Surface, offset):
        pos = pg.Vector2(floor(self.hurtboxes[0].x), floor(self.hurtboxes[0].y))
        surf.blit(pg.transform.flip(self.animation.img(), self.flip, False), (pos - offset + self.anim_offset))