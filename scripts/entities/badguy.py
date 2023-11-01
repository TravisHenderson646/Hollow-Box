from random import random, choice
from math import floor

import pygame as pg

from scripts.entities.physics_entity import PhysicsEntity
from scripts.debugger import debugger

class Badguy(PhysicsEntity):
    def __init__(self, pos):
        self.size = (15, 25)
        super().__init__('badguy', pos, self.size)
        self.think = BadguyThink(self)
        self.charge = BadguyCharge(self)
        self.jump = BadguyJump(self)
        self.speed = 0.8
        self.movement.x = -1
        self.hp = 30
        self.status = 'patrol'
        self.idle_radius = 100
        self.active = False
        self.ticks_since_started_shoot = 500
        self.true_rect = pg.FRect(0, 0, 15, 25)
        
    def update(self, tilemap, player):
        super().update()
        self.hitboxes[0] = self.hurtboxes[0]
        
        debugger.debug('flag', self.status)
        
        self.invulnerable = False
        if self.ticks_since_got_hit < 6:
            self.ticks_since_got_hit += 1
            self.invulnerable = True
            match self.got_hit_direction:
                case 2: #left
                    self.vel.x -= .8
                case 0: #right
                    self.vel.x += .8
                case 3: #up
                    self.vel.y = -1      
        
        if not self.active:
            if (self.collisions['right'] and (self.movement.x == 1)) or (self.collisions['left'] and (self.movement.x == -1)):
                self.movement.x = -self.movement.x
            if pg.Vector2(self.hurtboxes[0].x, self.hurtboxes[0].y).distance_to((player.hurtboxes[0].x, player.hurtboxes[0].y)) < self.idle_radius:
                self.active = True
                self.status = 'think'     
        else: # perhaps this should automatically check if previous status is the same as current so each status doesn't have to update
            if self.status == 'think':
                if not self.think.active:
                    self.think.active = True
                    self.think.ticks_since_started = 0
                    self.set_animation('idle')
                self.think.update(player)
            if self.status == 'charge':
                if not self.charge.active:
                    self.charge.active = True
                    self.charge.ticks_since_started = 0
                    self.set_animation('charge')
                self.charge.update(player)
            if self.status == 'jump':
                if not self.jump.active:
                    self.jump.active = True
                    self.jump.ticks_since_started = 0
                    self.set_animation('idle')
                self.jump.update(player)
                
        self.calculate_frame_movement()
        
    def calculate_frame_movement(self):
        if self.vel.x:
            self.frame_movement = pg.Vector2(self.vel.x, self.vel.y)   
        else:
            self.frame_movement = pg.Vector2((self.movement.x) * self.speed, self.vel.y)    

    def render(self, surf:pg.Surface, offset):
        pos = pg.Vector2(floor(self.hurtboxes[0].x), floor(self.hurtboxes[0].y))
        surf.blit(pg.transform.flip(self.animation.img(), self.flip, False), (pos - offset + self.anim_offset))
        if len(self.hitboxes) > 1:
            print(len(self.hitboxes))
            surf.fill((100,100,100), (self.jump.attack.x - offset[0], self.jump.attack.y - offset[1], self.jump.attack.w, self.jump.attack.h))
  # TESTESTESTESTEST   
     #   surf.fill((100,100,100), (self.hurtboxes[0].x - offset[0], self.hurtboxes[0].y - offset[1], 15, 25))
      #  surf.fill((100,0, 0), (self.hitboxes[0].x - offset[0], self.hitboxes[0].y - offset[1], self.hitboxes[0].w, self.hitboxes[0].h))
        
class BadguyJump:
    def __init__(self, badguy):
        self.badguy = badguy
        self.active = False
        self.ticks_since_started = 500
        self.duration = 25
        self.direction = 1
        self.attack = pg.FRect(0, 0, 35, 11)
        
    def update(self, player):
        if self.ticks_since_started == 0:
            self.ticks_since_started = 1
            self.badguy.vel.y = -2.5
            self.badguy.speed = 0.4
            if player.hurtboxes[0].centerx > self.badguy.hurtboxes[0].centerx:
                self.badguy.movement.x = 1
            else:
                self.badguy.movement.x = -1
        elif self.badguy.collisions['down']:
            if self.ticks_since_started == 1:
                self.badguy.speed = 0
                self.badguy.hitboxes.append(self.attack)
                self.badguy.hitboxes[1].bottom = self.badguy.hurtboxes[0].bottom
                if self.badguy.movement.x == 1:
                    self.badguy.hitboxes[1].left = self.badguy.hurtboxes[0].right
                else:
                    self.badguy.hitboxes[1].right = self.badguy.hurtboxes[0].left
            self.ticks_since_started += 1
        if self.ticks_since_started >= self.duration:
            self.active = False
            self.badguy.hitboxes.pop()
            self.badguy.status = 'think'
        

class BadguyThink:
    def __init__(self, badguy):
        self.badguy = badguy
        self.active = False
        self.ticks_since_started = 500
        self.duration = 120
        
    def update(self, player):
        if self.ticks_since_started == 0:
            self.badguy.speed = random() * 0.4            
            self.badguy.movement.x = choice([-1, 1])
        if self.ticks_since_started >= self.duration:
            self.active = False
            self.badguy.status = choice(['jump', 'charge'])        
        if player.hurtboxes[0].centerx < self.badguy.hurtboxes[0].centerx:
            self.badguy.flip = True
        else:
            self.badguy.flip = False
        self.ticks_since_started += 1
        
class BadguyCharge:
    def __init__(self, badguy):
        self.badguy = badguy
        self.active = False
        self.ticks_since_started = 500
        self.windup_duration = 60
        self.duration = 120 # could randomize this at start of each charge
        self.direction = 1
        self.rect = pg.FRect(0, 0, 15, 15)
        
    def update(self, player):
        if self.ticks_since_started == 0:
            self.rect.x = self.badguy.hurtboxes[0].x
            self.rect.y = self.badguy.hurtboxes[0].y
            self.badguy.hurtboxes[0] = self.rect
            if player.hurtboxes[0].centerx > self.badguy.hurtboxes[0].centerx:
                self.badguy.movement.x = 1
            else:
                self.badguy.movement.x = -1
        elif self.ticks_since_started < self.windup_duration:
            self.badguy.speed = -0.2
        else:
            self.badguy.speed = 2
        if self.ticks_since_started >= self.duration:
            self.active = False
            self.badguy.status = 'think'
            self.badguy.hurtboxes[0] = self.badguy.true_rect
            self.badguy.hurtboxes[0].x = self.rect.x
            self.badguy.hurtboxes[0].bottom = self.rect.bottom
        self.ticks_since_started += 1
        