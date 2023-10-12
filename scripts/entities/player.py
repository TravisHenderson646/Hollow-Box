import math
import random

from scripts.particle import Particle
from scripts import setup
from scripts.entities.physics_entity import PhysicsEntity


class Player(PhysicsEntity):
    def __init__(self, pos, size):
        super().__init__('player', pos, size)
        self.jump = Jump()
        self.air_time = 0
        self.jumps = 0
        # todo: hes about to do something else but i think you could just do if you collide with a wall left or right set jumps to 1
        self.wallslide = False
        self.dashing = 0 # poor name for non bool
        self.dead = 0
        
    def update(self, particles, movement):
        super().update(movement)
        if self.collisions['down']:
            self.jump.can_jump = True
            self.air_time = 0
            self.jumps = 1
    
        self.air_time += 1
        if self.air_time > 12:
            self.jump.can_jump = False
            
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
                       
    def render(self, surf, offset):
        super().render(surf, offset)
            
    def jumpold(self):
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
                # could add 'return True' to 'hook' on events to the jump like an animation``
        elif self.jumps > 0:
            self.vel[1] = -3.1
            self.jumps -= 1
            self.air_time = 5
            setup.sfx['jump'].play()
            
    def dash(self):
        if self.dashing == 0:
            setup.sfx['dash'].play()
            if self.flip:
                self.dashing = -60
            else:
                self.dashing = 60
                
class Jump:
    def __init__(self):
        self.can_jump = False
        self.jump_buffer = 5
        
    