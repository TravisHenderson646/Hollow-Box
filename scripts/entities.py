'''
Note every time there is game.foo
'''

import math
import random

import pygame as pg

from scripts.particle import Particle
from scripts.spark import Spark

class PhysicsEntity:
    def __init__(self, game, entity_type, pos, size):
        self.game = game
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
        
    def rect(self):
        return pg.Rect(*self.pos, *self.size)
    
    def set_action(self, action):
        if action !=self.action:
            self.action = action
            self.animation = self.game.assets[self.entity_type + '/' + self.action].copy()
        
    def update(self, tilemap, movement=(0, 0)):
        self.collisions = {'up': False, 'down': False, 'left': False, 'right': False}

        frame_movement = pg.Vector2(movement[0] + self.vel.x, movement[1] + self.vel.y)

        self.pos.x += frame_movement.x
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_near(self.pos):
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
        for rect in tilemap.physics_rects_near(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement.y > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement.y < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos.y = entity_rect.y
                
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

class Enemy(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'enemy', pos, size)
        
        self.walking = 0
        
    def update(self, tilemap, movement=(0, 0)):
        if self.walking:
            if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.pos[1] + 23)):
                if (self.collisions['right'] or self.collisions['left']):
                    self.flip = not self.flip
                movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
            else:
                self.flip = not self.flip
            self.walking = max(0, self.walking - 1)
            if not self.walking: #should happen only 1 frame bc we're inside a if self.walking cond
                dist = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1])
                if (abs(dist[1]) < 80):
                    if (self.flip and dist[0] < 0):
                        self.game.sfx['shoot'].play()
                        self.game.projectiles.append([[self.rect().centerx - 7, self.rect().centery], -1.5, 0])
                        for i in range(4):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5 + math.pi, 2 + random.random()))
                    if (not self.flip and dist[0]> 0):
                        self.game.sfx['shoot'].play()
                        self.game.projectiles.append([[self.rect().centerx + 7, self.rect().centery], 1.5, 0])
                        for i in range(4):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5, 2 + random.random()))
        elif random.random() < 0.01:
            self.walking = random.randint(30, 120)
        
        super().update(tilemap, movement=movement) #handles physics in parent class
        
        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')
            
        if abs(self.game.player.dashing) >= 50:
            if self.rect().colliderect(self.game.player.rect()):
                self.game.screenshake = max(30, self.game.screenshake)
                self.game.sfx['hit'].play()
                for i in range(30):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                    self.game.particles.append(Particle(self.game, 'particle', self.rect().center, vel=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
                self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                return True
            
    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset=offset)
        
        if self.flip:
            surf.blit(pg.transform.flip(self.game.assets['gun'], True, False), (self.rect().centerx - 4 - self.game.assets['gun'].get_width() - offset[0], self.rect().centery - offset[1]))
        else:
            surf.blit(self.game.assets['gun'], (self.rect().centerx + 4 - offset[0], self.rect().centery - offset[1]))

class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        self.air_time = 0
        self.jumps = 1
        # todo: hes about to do something else but i think you could just do if you collide with a wall left or right set jumps to 1
        self.wallslide = False
        self.dashing = 0 # poor name for non bool
        
    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement=movement)
    
        self.air_time += 1
        
        if self.air_time > 180:
            self.game.screenshake = max(45, self.game.screenshake)
            self.game.dead += 1
        
        if self.collisions['down']:
            self.air_time = 0
            self.jumps = 1
            
        self.wallslide = False
        if (self.collisions['right'] or self.collisions['left']) and self.air_time > 4:
            self.wallslide = True
            self.vel[1] = min(self.vel[1], 0.7)
            if self.collisions['right']:
                self.flip = False
            else:
                self.flip = True
            self.set_action('wallslide')
        
        if not self.wallslide: #could just unindent the next block and make them elifs    
            if self.air_time > 12:
                self.set_action('jump')
                self.jumps -= 1
            elif movement[0] != 0:
                self.set_action('run')
            else:
                self.set_action('idle')
        
        # 10 frames fast then 50? frames slow? and those 50 frames are also a cooldown        
        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1)
        if self.dashing < 0:
            self.dashing = min(0, self.dashing + 1)
        if abs(self.dashing) > 50:
            self.vel[0] = abs(self.dashing) / self.dashing * 8
            if abs(self.dashing) == 51:
                self.vel[0] *= 0.1
            #visual effects of dash
            particle_velocity = [abs(self.dashing) / self.dashing * random.random() * 3, 0]
            self.game.particles.append(Particle(self.game, 'particle', self.rect().center, vel=particle_velocity, frame=random.randint(0, 7)))
        if abs(self.dashing) in {49, 59}: #start and end (-1)
            for i in range(20):
                angle = random.random() * math.pi * 2
                speed = random.random() * 0.5 + 0.5
                particle_velocity = [math.cos(angle) * speed, math.sin(angle) *speed]
                self.game.particles.append(Particle(self.game, 'particle', self.rect().center, vel=particle_velocity, frame=random.randint(0, 7)))
                
    def render(self, surf, offset=(0, 0)):
        if abs(self.dashing) <= 50:
            super().render(surf, offset = offset)


        # lower the base (non player) vel slowly toward 0
        if self.vel[0] > 0:
            self.vel[0] = max(self.vel[0] - 0.1, 0)
        if self.vel[0] < 0:
            self.vel[0] = min(self.vel[0] + 0.1, 0)
            
    def jump(self):
        if self.wallslide:
            if self.flip and self.last_movement[0] < 0:
                self.vel[0] = 2.5
                self.vel[1] = -2.8
                self.air_time = 5
                self.jumps -= 1
                self.game.sfx['jump'].play()
                # could add 'return True' (or even 'return 'walljump') to 'hook' on events to the jump like an animation``
                # or i guess so this class could have less coupling with 'game'
            if not self.flip and self.last_movement[0] > 0:
                self.vel[0] = -2.5
                self.vel[1] = -2.8
                self.air_time = 5
                self.jumps -= 1
                self.game.sfx['jump'].play()
                # could add 'return True' to 'hook' on events to the jump like an animation``
        elif self.jumps > 0:
            self.vel[1] = -3.1
            self.jumps -= 1
            self.air_time = 5
            self.game.sfx['jump'].play()
            
    def dash(self):
        if self.dashing == 0:
            self.game.sfx['dash'].play()
            if self.flip:
                self.dashing = -60
            else:
                self.dashing = 60
