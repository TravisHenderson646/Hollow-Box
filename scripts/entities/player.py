import math
import random

import pygame as pg

from scripts.particle import Particle
from scripts import setup
from scripts.entities.physics_entity import PhysicsEntity
from scripts.debugger import debugger

class PlayerWallSlide:
    def __init__(self, player):
        self.player = player
        self.active = False
        self.speed = 0.4
        self.detach_buffer = 7
        self.ticks_detaching = 500
        self.direction = 1 # 1 or -1
        
    def start(self, direction):
        self.active = True
        self.player.jump.active = False
        self.player.jump.can_double = True
        self.player.dash.able = True
        self.ticks_detaching = 0
        self.direction = direction
        
    def update(self):
        self.player.vel[1] = min(self.player.vel[1], 0.2)
        self.player.set_animation('wallslide')
        if self.direction == -1:
            self.player.vel.x = -1
            if self.player.movement[1]:
                self.ticks_detaching += 1
                if self.detach_buffer < self.ticks_detaching:
                    self.active = False
            if not self.player.collisions['left']:
                self.player.rect.x += 1
                self.active = False
                self.player.vel.x = 0
        else:
            self.player.vel.x = 1
            if self.player.movement[0]:
                self.ticks_detaching += 1
                if self.detach_buffer < self.ticks_detaching:
                    self.active = False
            if not self.player.collisions['right']:
                self.player.rect.x -= 1
                self.active = False
                self.player.vel.x = 0

class Player(PhysicsEntity):
    def __init__(self, pos, size):
        super().__init__('player', pos, size)
        self.attack = PlayerAttack(self)
        self.jump = PlayerJump(self)
        self.dash = PlayerDash(self)
        self.wallslide = PlayerWallSlide(self)
        
        self.speed = 1.1
        self.hp = 5 
        
        self.lt = False
        
        self.invulnerable = False
        self.knockback_speed = 3
        self.knockback_direction = 1# left is -1
        self.ticks_since_player_got_hit = 500
        self.player_got_hit_knockback_duration = 13
        self.in_got_hit = False
        self.invulnerable_duration = 120
        self.air_time = 0
        self.float = False # depreciated
       
    def got_hit(self, enemy):
        setup.sfx['hit'].play()
        self.jump.active = False
        self.wallslide.active = False
        self.dash.active = False
        self.collisions['down'] = False
        self.hp -= 1
        self.vel.y = -2.4
        self.invulnerable = True
        self.air_time = self.jump.coyote_time + 1
        self.ticks_since_player_got_hit = 0
        if enemy.rect.centerx > self.rect.centerx:
            self.knockback_direction = -1
        else:
            self.knockback_direction = 1
     
    def update(self, tilemap):
        super().update()    
        self.invulnerable = False
        self.ticks_since_player_got_hit += 1
        self.attack.ticks_since_last += 1
        self.dash.ticks_since_last += 1
        self.jump.ticks_since_walljump += 1
        self.air_time += 1
        
        if self.air_time > self.jump.coyote_time: #base this on vel[1] > 0.3 instead
            self.jump.able = False
            self.set_animation('jump')    
        if self.collisions['down']:
            #i think this will reset the run animation to first frame every frame of running
            #solve with a animation_flag and only set_anim at the end of update
            self.set_animation('idle')
            self.jump.able = True
            self.dash.able = True
            self.jump.can_double = True
            self.wallslide.active = False
            self.air_time = 0
            if self.movement[0] or self.movement[1]:
                self.set_animation('run')
        elif self.collisions['right'] or self.collisions['left']:
            if not self.jump.active:
                if not self.in_got_hit:
                    if not self.wallslide.active:
                        if self.movement[1]:
                            self.wallslide.start(1)
                        elif self.movement[0]:
                            self.wallslide.start(-1)
                        
        if not self.dash.active:
            if self.jump.ticks_since_input < self.jump.buffer:
                if self.wallslide.active:
                    self.jump.start_walljump()
                else:
                    self.jump.check()
        if self.attack.ticks_since_input < self.attack.buffer:
            self.attack.check()
        if self.dash.ticks_since_input < self.dash.buffer:
            self.dash.check()
        in_attack_knockback = self.attack.ticks_since_knockback < self.attack.knockback_duration
        if in_attack_knockback:
            self.attack.knockback()

        self.in_got_hit = False
        if self.ticks_since_player_got_hit < self.invulnerable_duration:
            self.invulnerable = True
            self.in_got_hit = self.ticks_since_player_got_hit < self.player_got_hit_knockback_duration
            if self.in_got_hit:
                self.vel.x = self.knockback_speed * self.knockback_direction
                
        if self.wallslide.active:
            self.wallslide.update()
        if self.jump.active:
            self.jump.update()
        if self.dash.active:
            self.dash.update()
            
        
        # add can_rt like jump.able
        #!!! could decay over time based on length of hover
        if self.lt:
            self.vel.y = min(.4,self.vel.y)
            
        self.jump.ticks_since_input += 1
        self.dash.ticks_since_input += 1  
        self.attack.ticks_since_input += 1
        
        if self.dash.active:
            self.frame_movement = (self.vel.x, self.vel.y)
        elif self.wallslide.active:
            self.frame_movement = (self.vel.x, self.vel.y)
        elif self.jump.walljump_active:
            self.frame_movement = (self.vel.x, self.vel.y)
        elif in_attack_knockback and self.attack.direction in [0, 2]:
            self.frame_movement = (self.vel.x, self.vel.y)
        elif self.in_got_hit:
            self.frame_movement = (self.vel.x, self.vel.y)
        else:
            super().calculate_frame_movement()
                       
    def render(self, surf, offset):
        super().render(surf, offset)
        if self.attack.ticks_since_last < self.attack.duration:
            if self.attack.direction in [0, 2]:
                pos = (self.attack.hitbox.x - offset[0], self.attack.hitbox.y - offset[1])
                surf.blit(self.attack.surface,pos)
            if self.attack.direction in [1, 3]:
                pos = (self.attack.hitbox_vertical.x - offset[0], self.attack.hitbox_vertical.y - offset[1])
                surf.blit(self.attack.surface_vertical,pos)

class PlayerJump:
    def __init__(self, player):
        self.player = player
        self.able = False
        self.coyote_time = 7
        self.buffer = 7
        self.held = False
        self.active = False
        self.ticks_since_input = 500
        self.can_double = False
        self.ticks_since_walljump = 500
        self.walljump_active = False
        self.walljump_duration = 8
        self.walljump_speed = 2
        self.walljump_direction = 1 # -1 left or 1 right
        
    def check(self):
        if self.able:
            if self.ticks_since_input > 0:
                print('Buffered jump alert!!!')
            self.start()
        else:
            if self.can_double:
                if self.ticks_since_input > 0:
                    print('Buffered double jump alert!!!')
                self.start_double()
                
    def start_double(self):
        self.ticks_since_input = 100
        print('Double jump!!!')
        self.active = True
        self.can_double = False
        self.player.vel.y = -2.3
        
    def start_walljump(self):
        print('Wall jump!!!')
        self.player.wallslide.active = False
        self.ticks_since_walljump = 0
        self.active = True
        self.player.vel.y = -2.3
        self.ticks_since_input = 100
        self.walljump_direction = -self.player.wallslide.direction
            
    def start(self):
        self.ticks_since_input = 100
        if not self.player.collisions['down']:
            print('Coyote jump alert !!!')
        self.able = False
        self.active = True
        self.player.vel.y = -2.85
        setup.sfx['jump'].play()  
        
    def update(self):
        if self.held:
            self.player.vel.y -= 0.06
            self.player.set_animation('jump')
        else:
            self.player.vel.y += 0.48
        if self.player.vel.y > 0.3:
            self.active = False
        if self.ticks_since_walljump < self.walljump_duration:
            self.player.vel.x = self.walljump_speed * self.walljump_direction
            self.walljump_active = True
        else:
            self.walljump_active = False
         
class PlayerAttack:
    def __init__(self, player):
        self.player = player
        self.damage = 2
        self.direction = 0 # 0,1,2,3=right,down,left,up
        self.duration = 4
        self.cooldown = 33
        self.hitbox = pg.FRect(0, 0, setup.PLAYER_COLLISION_SIZE[1] * 2, setup.PLAYER_COLLISION_SIZE[0] * 3)
        self.hitbox_vertical = pg.FRect(0, 0, self.hitbox.height, self.hitbox.width)
        self.hitbox_list = [self.hitbox, self.hitbox_vertical]
        self.active_hitbox = 0
        self.surface = pg.Surface(self.hitbox.size)
        self.surface_vertical = pg.Surface(self.hitbox_vertical.size)    
        self.surface.fill((30,50,20))
        self.surface_vertical.fill((50,20,40))
        self.ticks_since_input = 500
        self.ticks_since_knockback = 500
        self.knockback_duration = 7
        self.buffer = 7
        self.ticks_since_last = 500
        
    def update(self):
        match self.direction:
            case 2: #left
                self.hitbox.centery = self.player.rect.centery
                self.hitbox.right = self.player.rect.centerx
            case 0: #right
                self.hitbox.centery = self.player.rect.centery
                self.hitbox.left = self.player.rect.centerx
            case 3: #up
                self.hitbox_vertical.centerx = self.player.rect.centerx
                self.hitbox_vertical.bottom = self.player.rect.centery
            case 1: #down
                self.hitbox_vertical.centerx = self.player.rect.centerx
                self.hitbox_vertical.top = self.player.rect.centery
    
    def check(self):
        if self.ticks_since_last > self.cooldown:
            if self.ticks_since_input > 0:
                print('Buffered attack alert!!!', self.ticks_since_input)
            self.start()
            
    def start(self):
        self.ticks_since_last = 0 # this is what actually causes the attack in update()
        self.ticks_since_input = 100
        if self.player.movement[3] and (not self.player.collisions['down']):
            self.direction = 1 #down
            self.active_hitbox = 1
        elif self.player.movement[2]:
            self.direction = 3 #up
            self.active_hitbox = 1
        elif self.player.flip:
            self.direction = 2 #left
            self.active_hitbox = 0
        else:
            self.direction = 0 #right
            self.active_hitbox = 0
                
    def knockback(self):
        match self.direction:
            case 2: #left
                self.player.vel.x += 1.5
            case 0: #right
                self.player.vel.x -= 1.5
            case 3: #up
                self.player.vel.y = max(0, self.player.vel.y)
            case 1: #down pogo
                if self.ticks_since_knockback == 0:
                    self.player.vel.y = -2.35
                    self.player.jump.can_double = True
                    self.player.dash.able = True
        self.ticks_since_knockback += 1
                
class PlayerDash:
    def __init__(self, player):
        self.player = player
        self.able = False
        self.buffer = 7
        self.active = False
        self.ticks_since_input = 500
        self.ticks_since_last = 500
        self.cooldown = 33
        self.direction = (0, 0)
        self.duration = 20
        self.speed = 3.3
        
    def check(self):
        if self.able:
            self.start()
            if self.ticks_since_input > 0:
                print('Buffered dash alert!!!')
            self.ticks_since_input = 100
            
    def start(self):
        if self.ticks_since_last > self.cooldown:
            setup.sfx['jump'].play()
            self.player.jump.active = False
            self.active = True
            self.ticks_since_last = 0
            self.able = False
            if self.player.wallslide.active:
                self.direction = (-self.player.wallslide.direction, 0)
            else:
                self.direction = (
                    (self.player.movement[1] - self.player.movement[0]),
                    (self.player.movement[3] - self.player.movement[2]))
            match self.direction:
                case ( 0,  0):
                    if self.player.flip:
                        self.direction = (-1, 0)
                    else:
                        self.direction = (1, 0)
                case ( 0,  1):
                    self.player.vel.y =  self.player.terminal_vel
                case ( 0, -1):
                    self.player.vel.y = -3.2
                case (-1, -1):
                    self.player.vel.y = -3
                case ( 1, -1):
                    self.player.vel.y = -3

    def update(self):
        if self.ticks_since_last < self.duration:
            match self.direction:
                case ( 1,  0):
                    self.player.vel.y = 0
                    self.player.vel.x = self.player.speed * self.speed
                case (-1,  0):
                    self.player.vel.y = 0
                    self.player.vel.x = -self.player.speed * self.speed
                case ( 0,  1):
                    pass
                case ( 0, -1):
                    pass
                case ( 1,  1):
                    self.player.vel.y = 0
                    self.player.vel.x = self.player.speed * self.speed
                case (-1,  1):
                    self.player.vel.y = 0
                    self.player.vel.x = -self.player.speed * self.speed
                case (-1, -1):
                    self.player.vel.x = -self.player.speed * self.speed / 2
                case ( 1, -1):
                    self.player.vel.x = self.player.speed * self.speed / 2
        else:
            self.active = False



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