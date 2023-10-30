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
        self.attack = PlayerAttack(self)
        self.jump = PlayerJump(self)
        self.dash = PlayerDash(self)
        self.wallslide = PlayerWallSlide(self)
        self.lt = False
        
        self.speed = 1.2
        self.hp = 5 
        
        self.invulnerable = False
        self.knockback_speed = 3
        self.knockback_direction = 1# left is -1
        self.ticks_since_player_got_hit = 500
        self.player_got_hit_knockback_duration = 10
        self.in_got_hit = False
        self.invulnerable_duration = 120
        self.air_time = 0
        self.can_interact_flag = False
        self.try_interact_flag = False
       
    def got_hit(self, enemy):
        setup.sfx['hit'].play()
        self.jump.active = False
        self.wallslide.active = False
        self.dash.active = False
        self.collisions['down'] = False
        self.hp -= 1
        self.vel.y = self.jump.double_impulse
        self.invulnerable = True
        self.air_time = self.jump.coyote_time + 1
        self.ticks_since_player_got_hit = 0
        if enemy.rect.centerx > self.rect.centerx:
            self.knockback_direction = -1
        else:
            self.knockback_direction = 1  
                 
    def got_hit_by_spike(self):
        setup.sfx['hit'].play()
        self.jump.active = False
        self.wallslide.active = False
        self.dash.active = False
        self.collisions['down'] = False
        self.hp -= 1
        self.vel.y = self.jump.double_impulse
        self.invulnerable = True
        self.ticks_since_player_got_hit = 0
        self.air_time = self.jump.coyote_time + 1
        if self.flip:
            self.knockback_direction = 1
        else:
            self.knockback_direction = -1
     
    def update(self, tilemap):
        if setup.joysticks:
            axis0 = setup.joysticks[0].get_axis(0)
            axis1 = setup.joysticks[0].get_axis(1)
            if axis0 < -0.5:
                self.movement.x = -1
            elif axis0 > 0.5:
                self.movement.x = 1
            else:
                self.movement.x = 0
            if axis1 < -0.5:
                self.movement.y = -1
            elif axis1 > 0.5:
                self.movement.y = 1
            else:
                self.movement.y = 0
            axis4 = setup.joysticks[0].get_axis(4)
            if axis4 > 0.8:
                self.lt = True
            else:
                self.lt = False
        else:
            keys = pg.key.get_pressed()
            self.movement = pg.Vector2(keys[pg.K_d] - keys[pg.K_a], keys[pg.K_s] - keys[pg.K_w])
            self.lt = keys[pg.K_i]
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
            if self.movement.x:
                self.set_animation('run')
        elif self.collisions['right']:
            if not self.jump.active:
                if not self.vel.x:
                    if self.movement.x == 1:
                        if not self.wallslide.active:
                            self.wallslide.start(self.movement.x)
        elif self.collisions['left']:
            if not self.jump.active:
                if not self.vel.x:
                    if self.movement.x == -1:
                        if not self.wallslide.active:
                            self.wallslide.start(self.movement.x)
                        
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
            self.wallslide.update(tilemap)
        if self.jump.active:
            self.jump.update()
        if self.dash.active:
            self.dash.update()
            
        
        # add can_lt like jump.able
        #!!! could decay over time based on length of hover
   #     if self.lt:
    #        self.vel.y = min(.4,self.vel.y)
            
        self.jump.ticks_since_input += 1
        self.dash.ticks_since_input += 1  
        self.attack.ticks_since_input += 1

        if self.wallslide.active:
            self.frame_movement = pg.Vector2(self.vel.x, self.vel.y)  
        else:
            super().calculate_frame_movement()
        self.jump.walljump_active = False
                       
    def render(self, surf, offset):
        super().render(surf, offset)
        
        if self.attack.ticks_since_last < self.attack.duration:
            if self.attack.direction in [0, 2]:
                for hitbox, surface in zip(self.attack.hitboxes, self.attack.surfaces):
                    pos = (hitbox.x - offset[0], hitbox.y - offset[1])
                    surf.blit(surface,pos)
            if self.attack.direction in [1, 3]:
                for hitbox, surface in zip(self.attack.hitboxes_vertical, self.attack.surfaces_vertical):
                    pos = (hitbox.x - offset[0], hitbox.y - offset[1])
                    surf.blit(surface,pos)

class PlayerJump:
    def __init__(self, player):
        self.player = player
        self.unlocked = True
        self.double_unlocked = True
        self.able = False
        self.coyote_time = 7
        self.buffer = 7
        self.held = False
        self.active = False
        self.ticks_since_input = 500
        self.can_double = False
        self.ticks_since_walljump = 500
        self.walljump_active = False
        self.walljump_duration = 4
        self.walljump_speed = 2
        self.walljump_direction = 1 # -1 left or 1 right
        self.impulse = -1.8
        self.double_impulse = -1.4
        self.walljump_impulse = -1.4
        
    def check(self):
        if self.able:
            if self.unlocked:
                if self.ticks_since_input > 0:
                    print('Buffered jump alert!!!')
                self.start()
        else:
            if self.can_double:
                if self.double_unlocked:
                    if self.ticks_since_input > 0:
                        print('Buffered double jump alert!!!')
                    self.start_double()
                
    def start_double(self):
        self.ticks_since_input = 100
        print('Double jump!!!')
        self.active = True
        self.can_double = False
        self.player.vel.y = min(self.player.vel.y, self.double_impulse)
        
    def start_walljump(self):
        print('Wall jump!!!')
        self.player.wallslide.active = False
        self.ticks_since_walljump = 0
        self.active = True
        self.player.vel.y = self.walljump_impulse
        self.ticks_since_input = 100
        self.walljump_direction = -self.player.wallslide.direction
            
    def start(self):
        self.ticks_since_input = 100
        if not self.player.collisions['down']:
            print('Coyote jump alert !!!')
        self.able = False
        self.active = True
        self.player.vel.y = self.impulse
        setup.sfx['jump'].play()  
        
    def update(self):
        if self.held:
            self.player.vel.y -= self.player.gravity * 0.5
            self.player.set_animation('jump')
            if self.player.vel.y > 0:
                self.active = False
        else:
            self.player.vel.y = 0.5
            self.active = False
   #     if self.player.vel.y == 0:
 #           self.active = False
        if self.ticks_since_walljump < self.walljump_duration:
            self.player.vel.x = self.walljump_speed * self.walljump_direction
            self.walljump_active = True
         
class PlayerAttack:
    def __init__(self, player):
        self.player = player
        self.unlocked = True
        self.damage = 2
        self.direction = 0 # 0,1,2,3=right,down,left,up
        self.duration = 4
        self.cooldown = 33
        self.ticks_since_input = 500
        self.ticks_since_knockback = 500
        self.knockback_duration = 7
        self.buffer = 7
        self.ticks_since_last = 500
        self.in_knockback = False
        self.active_hitboxes = 0 # could be active hitboxes
        
        self.hitboxes = []
        self.hitboxes_vertical = []
        self.surfaces = []
        self.surfaces_vertical = [] # these could be in a dict with names
        self.hitboxes.append(pg.FRect(0, 0,  7, 12))
        self.hitboxes.append(pg.FRect(0, 0,  7,  9))
        self.hitboxes.append(pg.FRect(0, 0, 13,  5))
        self.hitboxes.append(pg.FRect(0, 0,  3,  2))
        self.hitboxes_vertical.append(pg.FRect(0, 0, 12,  7))
        self.hitboxes_vertical.append(pg.FRect(0, 0,  9,  7))
        self.hitboxes_vertical.append(pg.FRect(0, 0,  5, 12))
        self.hitboxes_vertical.append(pg.FRect(0, 0,  2,  3))
        self.hitbox_list = [self.hitboxes, self.hitboxes_vertical]
        for hitbox in self.hitboxes:
            self.surfaces.append(pg.Surface(hitbox.size))
            self.surfaces[-1].fill((150,50,100))
        for hitbox in self.hitboxes_vertical:
            self.surfaces_vertical.append(pg.Surface(hitbox.size))
            self.surfaces_vertical[-1].fill((150,50,100))
        
    def update(self):
        match self.direction:
            case 2: #left
                self.hitboxes[0].centery = self.player.rect.centery
                self.hitboxes[0].right = self.player.rect.centerx
                self.hitboxes[1].centery = self.player.rect.centery
                self.hitboxes[1].right = self.hitboxes[0].left
                self.hitboxes[2].centery = self.player.rect.centery
                self.hitboxes[2].right = self.hitboxes[1].left
                self.hitboxes[3].centery = self.player.rect.centery
                self.hitboxes[3].right = self.hitboxes[2].left
            case 0: #right
                self.hitboxes[0].centery = self.player.rect.centery
                self.hitboxes[0].left = self.player.rect.centerx
                self.hitboxes[1].centery = self.player.rect.centery
                self.hitboxes[1].left = self.hitboxes[0].right
                self.hitboxes[2].centery = self.player.rect.centery
                self.hitboxes[2].left = self.hitboxes[1].right
                self.hitboxes[3].centery = self.player.rect.centery
                self.hitboxes[3].left = self.hitboxes[2].right
            case 3: #up
                self.hitboxes_vertical[0].centerx = self.player.rect.centerx
                self.hitboxes_vertical[0].bottom = self.player.rect.centery
                self.hitboxes_vertical[1].centerx = self.player.rect.centerx
                self.hitboxes_vertical[1].bottom = self.hitboxes_vertical[0].top
                self.hitboxes_vertical[2].centerx = self.player.rect.centerx
                self.hitboxes_vertical[2].bottom = self.hitboxes_vertical[1].top
                self.hitboxes_vertical[3].centerx = self.player.rect.centerx
                self.hitboxes_vertical[3].bottom = self.hitboxes_vertical[2].top
            case 1: #down
                self.hitboxes_vertical[0].centerx = self.player.rect.centerx
                self.hitboxes_vertical[0].top = self.player.rect.centery
                self.hitboxes_vertical[1].centerx = self.player.rect.centerx
                self.hitboxes_vertical[1].top = self.hitboxes_vertical[0].bottom
                self.hitboxes_vertical[2].centerx = self.player.rect.centerx
                self.hitboxes_vertical[2].top = self.hitboxes_vertical[1].bottom
                self.hitboxes_vertical[3].centerx = self.player.rect.centerx
                self.hitboxes_vertical[3].top = self.hitboxes_vertical[2].bottom
    
    def check(self):
        if self.ticks_since_last > self.cooldown:
            if self.unlocked:
                if not self.player.dash.active:
                    if self.ticks_since_input > 0:
                        print('Buffered attack alert!!!', self.ticks_since_input)
                    self.start()
            
    def start(self):
        self.ticks_since_last = 0 # this is what actually causes the attack in update()
        self.ticks_since_input = 100
        if self.player.wallslide.active:
            if self.player.wallslide.direction == 1:
                self.direction = 2 #left
                self.active_hitboxes = 0
            if self.player.wallslide.direction == -1:
                self.direction = 0 #right
                self.active_hitboxes = 0
        elif (self.player.movement.y == 1) and (not self.player.collisions['down']):
            self.direction = 1 #down
            self.active_hitboxes = 1
        elif self.player.movement.y == -1:
            self.direction = 3 #up
            self.active_hitboxes = 1
        elif self.player.flip:
            self.direction = 2 #left
            self.active_hitboxes = 0
        else:
            self.direction = 0 #right
            self.active_hitboxes = 0
                
    def knockback(self):
        match self.direction:
            case 2: #left
                self.player.vel.x = 1.5 # could use max here to make sure it doesn't override a bigger knockback
            case 0: #right
                self.player.vel.x = -1.5
            case 3: #up
                self.player.vel.y = max(1, self.player.vel.y)
            case 1: #down pogo
                if self.ticks_since_knockback == 0:
                    self.player.jump.active = False
                    self.player.vel.y = min(self.player.vel.y, self.player.jump.double_impulse)
                    self.player.jump.can_double = True
                    self.player.dash.able = True
        self.ticks_since_knockback += 1

class PlayerWallSlide:
    def __init__(self, player):
        self.player = player
        self.unlocked = True
        self.active = False
        self.speed = 0.8
        self.detach_buffer = 7
        self.ticks_detaching = 500
        self.direction = 1 # 1 or -1
        
    def start(self, direction):
        if self.unlocked:
            self.active = True
            self.player.jump.active = False
            self.player.jump.can_double = True
            self.player.dash.able = True
            self.ticks_detaching = 0
            self.direction = direction
        
    def update(self, tilemap):
        self.player.vel[1] = min(self.player.vel[1], self.speed)
        self.player.set_animation('wallslide')
        if self.direction == -1:
            self.player.flip = True
            self.active = tilemap.check_wallslide(self.player)
            if self.player.movement.x == 1:
                self.ticks_detaching += 1
                if self.ticks_detaching > self.detach_buffer:
                    self.active = False
            else:
                self.ticks_detaching = 0
        if self.direction == 1:
            self.player.flip = False
            self.active = tilemap.check_wallslide(self.player)
            if self.player.movement.x == -1:
                self.ticks_detaching += 1
                if self.ticks_detaching > self.detach_buffer:
                    self.active = False
            else:
                self.ticks_detaching = 0    
                            
class PlayerDash:
    def __init__(self, player):
        self.player = player
        self.unlocked = True
        self.able = False
        self.buffer = 7
        self.active = False
        self.ticks_since_input = 500
        self.ticks_since_last = 500
        self.cooldown = 33
        self.direction = 1 # -1 or 1 (L or R)
        self.duration = 9
        self.speed = 2.5
        
    def check(self):
        if self.able:
            if self.unlocked:
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
                self.direction = -self.player.wallslide.direction
            elif self.player.movement.x:
                self.direction = self.player.movement.x
            else:
                if self.player.flip:
                    self.direction = -1
                else:
                    self.direction = 1

    def update(self):
        if self.ticks_since_last < self.duration:
            self.player.vel.y = 0
            self.player.vel.x = self.player.speed * self.speed * self.direction
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