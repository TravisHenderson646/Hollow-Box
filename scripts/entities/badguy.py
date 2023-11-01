from random import random, randint, choice, choices
from math import floor

import pygame as pg

from scripts.entities.physics_entity import PhysicsEntity
from scripts.debugger import debugger
from scripts.projectile import Projectile

class Badguy(PhysicsEntity):
    def __init__(self, pos):
        self.size = (15, 25)
        super().__init__('badguy', pos, self.size)
        self.think = BadguyThink(self)
        self.charge = BadguyCharge(self)
        self.jump = BadguyJump(self)
        self.shoot = BadguyShoot(self)
        self.speed = 0.2
        self.movement.x = -1
        self.hp = 15
        self.geo = 15
        self.status = 'patrol' # 'patrol' never used
        self.idle_radius = 100
        self.active = False
        self.ticks_since_started_shoot = 500
        self.true_rect = pg.FRect(0, 0, 15, 25)
        self.gravity = 0.07
        self.moves = {'shoot': 0, 'charge': 0, 'jump': 0}
        
    def update(self, tilemap, player):
        super().update()
        self.hitboxes[0] = self.hurtboxes[0]
        
        debugger.debug('flag', self.moves)
        
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
                    self.vel.y = -0.5   
        
        if not self.active:
            if (self.collisions['right'] and (self.movement.x == 1)) or (self.collisions['left'] and (self.movement.x == -1)):
                self.movement.x = -self.movement.x
            if pg.Vector2(self.hurtboxes[0].centerx, self.hurtboxes[0].centery).distance_to((player.hurtboxes[0].centerx, player.hurtboxes[0].centery)) < self.idle_radius:
                self.active = True
                self.status = 'think'     
        else: # perhaps this should automatically check if previous status is the same as current so each status doesn't have to update
            if self.status == 'think':
                if not self.think.active:
                    self.think.active = True
                    self.think.ticks_since_started = 0
                    self.set_animation('idle')
                self.think.update(tilemap, player)
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
            if self.status == 'shoot':
                if not self.shoot.active:
                    self.shoot.active = True
                    self.shoot.ticks_since_started = 0
                    self.set_animation('idle')
                self.shoot.update(player)
                
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
            surf.fill((100,100,100), (self.jump.attack.x - offset[0], self.jump.attack.y - offset[1], self.jump.attack.w, self.jump.attack.h))
  # TESTESTESTESTEST   
     #   surf.fill((100,100,100), (self.hurtboxes[0].x - offset[0], self.hurtboxes[0].y - offset[1], 15, 25))
      #  surf.fill((100,0, 0), (self.hitboxes[0].x - offset[0], self.hitboxes[0].y - offset[1], self.hitboxes[0].w, self.hitboxes[0].h))

class BadguyThink:
    def __init__(self, badguy):
        self.badguy = badguy
        self.active = False
        self.ticks_since_started = 500
        self.duration = 120
        self.range_spacing = 50
        
    def update(self, tilemap, player):
        if self.ticks_since_started == 0:
            self.duration = randint(30, 90)
            for key in self.badguy.moves.keys():
                self.badguy.moves[key] += 1
            self.badguy.speed = random() * 0.3  + 0.1           
            self.badguy.movement.x = choice([-1, 1])
        if self.ticks_since_started >= self.duration:
            self.active = False
            if self.badguy.flip:
                if tilemap.check_point((self.badguy.hurtboxes[0].left - 4, self.badguy.hurtboxes[0].bottom - 2), self.badguy.hot_chunk):
                    self.badguy.moves['charge'] += 4
            else:
                if tilemap.check_point((self.badguy.hurtboxes[0].right + 4, self.badguy.hurtboxes[0].bottom - 2), self.badguy.hot_chunk):
                    self.badguy.moves['charge'] += 4                
            if pg.Vector2(self.badguy.hurtboxes[0].centerx, self.badguy.hurtboxes[0].centery).distance_to((player.hurtboxes[0].centerx, player.hurtboxes[0].centery)) < self.range_spacing:
                self.badguy.moves['jump'] += 1
            else:
                self.badguy.moves['shoot'] += 1
            self.badguy.status = choices(list(self.badguy.moves.keys()), weights = list(self.badguy.moves.values()))[0]        
        if player.hurtboxes[0].centerx < self.badguy.hurtboxes[0].centerx:
            self.badguy.flip = True
        else:
            self.badguy.flip = False
        self.ticks_since_started += 1
                           
class BadguyShoot:
    def __init__(self, badguy):
        self.badguy = badguy
        self.active = False
        self.ticks_since_started = 500
        self.duration = 60
        self.direction = 1
        self.dash_back_duration = 8
        self.shoot_timing = 40
        self.attack = pg.FRect(0, 0, 35, 11)
        
    def update(self, player):
        if self.ticks_since_started == 0:
            self.badguy.moves['shoot'] = 0
            self.ticks_since_started = 1
            if player.hurtboxes[0].centerx > self.badguy.hurtboxes[0].centerx:
                self.badguy.movement.x = 1
            else:
                self.badguy.movement.x = -1
        elif self.ticks_since_started < self.dash_back_duration:
            self.badguy.speed = -4
        elif self.ticks_since_started == self.shoot_timing:
            self.badguy.projectiles.append(Projectile((self.badguy.hurtboxes[0].centerx, self.badguy.hurtboxes[0].bottom), ( self.badguy.movement.x * 2.2, -1.8)))
        else:
            self.badguy.speed = 0
        if self.ticks_since_started >= self.duration:
            self.active = False
            self.badguy.status = 'think'
        self.ticks_since_started += 1
                
class BadguyJump:
    def __init__(self, badguy):
        self.badguy = badguy
        self.active = False
        self.ticks_since_started = 500
        self.duration = 17
        self.direction = 1
        self.attack = pg.FRect(0, 0, 35, 11)
        
    def update(self, player):
        if self.ticks_since_started == 0:
            self.badguy.moves['jump'] = 0
            self.ticks_since_started = 1
            self.badguy.vel.y = -2.1
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


class BadguyCharge:
    def __init__(self, badguy):
        self.badguy = badguy
        self.active = False
        self.ticks_since_started = 500
        self.windup_duration = 60
        self.duration = 90 # could randomize this at start of each charge
        self.direction = 1
        self.rect = pg.FRect(0, 0, 15, 15)
        
    def update(self, player):
        if self.ticks_since_started == 0:
            self.badguy.moves['charge'] = 0
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
        