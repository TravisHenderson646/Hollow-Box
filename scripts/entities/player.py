import math
import random

import pygame as pg

from scripts.particle import Particle
from scripts import setup
from scripts.entities.physics_entity import PhysicsEntity
from scripts.debugger import debugger


class Player(PhysicsEntity):
    def __init__(self, pos, size):
        super().__init__('player', pos, size)
        self.speed = 1
        self.dead = 0   
        
        self.wallslide = False
        self.dashing = 0 # poor name for non bool
          
        self.air_time = 0
        self.can_jump = False
        self.ticks_since_last_attack = 500
        self.attack_hitbox = pg.FRect(0, 0, size[1] * 2, size[0] * 3)
        self.attack_surface = pg.Surface(self.attack_hitbox.size)
        self.attack_surface.fill((200,200,200))
        self.attack_direction = 0
        self.attack_cooldown = 45
        self.ticks_since_attack_input = 500
        self.attack_buffer = 7
        self.ticks_since_jump_input = 500
        self.jump_buffer = 7
        self.coyote_time = 7
        self.holding_jump = False
        self.jumping = False
        self.float = False

    def try_jump(self):
        if self.can_jump:
            self.jump()
            if self.ticks_since_jump_input > 0:
                print('Buffered jump alert!!!')
            self.ticks_since_jump_input = 100
        else:
            self.ticks_since_jump_input += 1  
            
    def jump(self):
        if not self.collisions['down']:
            print('Coyote jump alert !!!')
        self.can_jump = False
        self.holding_jump = True
        self.jumping = True
        self.vel.y = -2.85
        setup.sfx['jump'].play()  
                      
    def try_attack(self):
        if self.ticks_since_last_attack > self.attack_cooldown:
            self.ticks_since_last_attack = 0 # this is what actually causes the attack in update()
            if self.ticks_since_attack_input > 0:
                print('Buffered attack alert!!!')
            self.ticks_since_attack_input = 100
        else:
            self.ticks_since_attack_input += 1
            
    def choose_attack_dir(self):
        print(self.movement, self.attack_direction)
        if self.movement[3] and (not self.collisions['down']):
            self.attack_direction = 3 #down
            print('test33')
        elif self.movement[2]:
            self.attack_direction = 2 #up
            print('test22')
        elif self.flip:
            self.attack_direction = 0 #left
            print('test00')
        else:
            self.attack_direction = 1 #right
            print('test11')
        
    def attack(self):
        match self.attack_direction:
            case 0:
                print('attack0')
                self.attack_hitbox.centery = self.rect.centery
                self.attack_hitbox.right = self.rect.left
            case 1:
                print('attack1')
                self.attack_hitbox.centery = self.rect.centery
                self.attack_hitbox.left = self.rect.right
            case 2:
                print('attack2')
                self.attack_hitbox.centerx = self.rect.centerx
                self.attack_hitbox.bottom = self.rect.top
            case 3:
                print('attack3')
                self.attack_hitbox.centerx = self.rect.centerx
                self.attack_hitbox.top = self.rect.bottom
        
    def dash(self):
        if self.dashing == 0:
            setup.sfx['dash'].play()
            if self.flip:
                self.dashing = -60
            else:
                self.dashing = 60
         
     
    def update(self, particles):
        super().update()

        if self.collisions['down']:
            self.set_animation('idle')
            self.can_jump = True
            self.air_time = 0

        if self.air_time > self.coyote_time: #base this on vel[1] > 0.3 instead
            self.can_jump = False
            self.set_animation('jump')
            
        if self.jumping:
            if self.holding_jump:
                self.vel.y -= 0.06
                self.set_animation('jump')
            else:
                self.set_animation('idle')
                self.vel.y += 0.64
            if self.vel.y > 0.3:
                self.set_animation('jump')
                self.jumping = False
                
        if self.ticks_since_last_attack < 20:
            if self.ticks_since_last_attack == 1:
                self.choose_attack_dir()
            self.attack()
                
        if self.ticks_since_jump_input < self.jump_buffer:
            self.try_jump()
        if self.ticks_since_attack_input < self.attack_buffer:
            self.try_attack()
        
            
        self.ticks_since_last_attack += 1
        self.air_time += 1
                       
    def render(self, surf, offset):
        super().render(surf, offset)
        pos = (self.attack_hitbox.x - offset[0], self.attack_hitbox.y - offset[1])
        surf.blit(self.attack_surface,pos)

        '''self.wallslide = False
        if (self.collisions['right'] or self.collisions['left']) and self.air_time > 4:
            self.wallslide = True
            self.vel[1] = min(self.vel[1], 0.7)
            if self.collisions['right']:
                self.flip = False
            else:
                self.flip = True
            self.set_animation('wallslide')
        
        if not self.wallslide: #could just unindent the next block and make them elifs    
            if self.air_time > 12:
                self.set_animation('jump')
                self.jumps -= 1
            elif movement[0] != 0:
                self.set_animation('run')
            else:
                self.set_animation('idle')
        
        # 10 frames on then 50 frames arecooldown        
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
            particles.append(Particle('particle', self.rect().center, vel=particle_velocity, frame=random.randint(0, 7)))
        if abs(self.dashing) in {49, 59}: #start and end (-1)
            for i in range(20):
                angle = random.random() * math.pi * 2
                speed = random.random() * 0.5 + 0.5
                particle_velocity = [math.cos(angle) * speed, math.sin(angle) *speed]
                particles.append(Particle('particle', self.rect().center, vel=particle_velocity, frame=random.randint(0, 7)))

        # lower the base (non player) vel slowly toward 0
        if self.vel[0] > 0:
            self.vel[0] = max(self.vel[0] - 0.1, 0)
        if self.vel[0] < 0:
            self.vel[0] = min(self.vel[0] + 0.1, 0)     '''
        
    '''
        if self.wallslide:
            if self.flip and self.last_movement[0] < 0:
                self.vel[0] = 2.5
                self.vel[1] = -2.8
                self.air_time = 5
                self.jumps -= 1
                setup.sfx['jump'].play()
                # could add 'return True' (or even 'return 'walljump') to 'hook' on events to the jump like an animation``
                # or i guess so this class could have less coupling with 'game'
            if not self.flip and self.last_movement[0] > 0:
                self.vel[0] = -2.5
                self.vel[1] = -2.8
                self.air_time = 5
                self.jumps -= 1
                setup.sfx['jump'].play()
                # could add 'return True' to 'hook' on events to the jump like an animation``'''