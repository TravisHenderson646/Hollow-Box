import pygame as pg

from scripts.particle import Particle
from scripts.entities.player.combat import Combat
from scripts.entities.player.movement import Movement
from scripts.entities.player.animate import Animate
from scripts.entities.player.jump import Jump
from scripts.entities.player.wallslide import WallSlide
from scripts.entities.player.dash import Dash
from scripts import setup
from scripts.debugger import debugger

class Player:
    def __init__(self, pos, size):
        self.name = 'player'
        self.size = size
        self.rect = pg.FRect(*pos, *self.size)
        self.jump = Jump(self)
        self.dash = Dash(self)
        self.wallslide = WallSlide(self)
        
        self.movement = Movement(self)
        self.combat = Combat(self)
        self.animate = Animate(self)
        self.animate.anim_offset = pg.Vector2(0, -2)
        
        self.lt = False
        self.geo = 0
        
        self.can_interact_flag = False
        self.try_interact_flag = False
       
     
    def update(self, level):
        debugger.debug('geo', ('geo:', self.geo))
        ### Get user input
        if setup.joysticks:
            axis0 = setup.joysticks[0].get_axis(0)
            axis1 = setup.joysticks[0].get_axis(1)
            if axis0 < -0.5:
                self.movement.movement.x = -1
            elif axis0 > 0.5:
                self.movement.movement.x = 1
            else:
                self.movement.movement.x = 0
            if axis1 < -0.5:
                self.movement.movement.y = -1
            elif axis1 > 0.5:
                self.movement.movement.y = 1
            else:
                self.movement.movement.y = 0
            axis4 = setup.joysticks[0].get_axis(4)
            if axis4 > 0.8:
                self.lt = True
            else:
                self.lt = False
        else:
            keys = pg.key.get_pressed()
            self.movement.movement = pg.Vector2(keys[pg.K_d] - keys[pg.K_a], keys[pg.K_s] - keys[pg.K_w])
            self.lt = keys[pg.K_i] 
        ###
        
        self.combat.frame_start()
        self.movement.frame_start()
        
        self.dash.ticks_since_last += 1
        self.jump.ticks_since_walljump += 1
        
        if self.movement.air_time > self.jump.coyote_time: #base this on vel[1] > 0.3 instead
            self.jump.able = False
            self.animate.set_animation('jump')    
        if self.movement.collisions['down']:
            #i think this will reset the run animation to first frame every frame of running
            #solve with a animation_flag and only set_anim at the end of update
            self.animate.set_animation('idle')
            self.jump.able = True
            self.dash.able = True
            self.jump.can_double = True
            self.wallslide.active = False
            self.movement.air_time = 0
            if self.movement.movement.x:
                self.animate.set_animation('run')
        elif self.movement.collisions['right']:
            if not self.jump.active:
                if not self.movement.vel.x:
                    if self.movement.movement.x == 1:
                        if not self.wallslide.active:
                            self.wallslide.start(self.movement.movement.x)
        elif self.movement.collisions['left']:
            if not self.jump.active:
                if not self.movement.vel.x:
                    if self.movement.movement.x == -1:
                        if not self.wallslide.active:
                            self.wallslide.start(self.movement.movement.x)
                        
        if not self.dash.active:
            if self.jump.ticks_since_input < self.jump.buffer:
                if self.wallslide.active:
                    self.jump.start_walljump()
                else:
                    self.jump.check()
        if self.combat.attack.ticks_since_input < self.combat.attack.buffer:
            self.combat.attack.check()
        if self.dash.ticks_since_input < self.dash.buffer:
            self.dash.check()
        if self.combat.attack.in_knockback:
            self.combat.attack.knockback()

        self.combat.in_got_hit = False
        if self.combat.ticks_since_got_hit < self.combat.invulnerable_duration:
            self.combat.invulnerable = True
            self.combat.in_got_hit = self.combat.ticks_since_got_hit < self.combat.got_hit_knockback_duration
            if self.combat.in_got_hit:
                self.movement.vel.x = self.combat.knockback_speed * self.combat.knockback_direction
                
        if self.wallslide.active:
            self.wallslide.update(level.tilemap)
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
        self.combat.attack.ticks_since_input += 1
        
        if self.combat.invulnerable:
            self.combat.hit_by_spike = False
        elif self.combat.hit_by_spike:
            self.wallslide.active = False
            self.combat.hit_by_spike = False
            self.got_hit_by_spike()

        if self.wallslide.active:
            self.movement.frame_movement = pg.Vector2(self.movement.vel.x, self.movement.vel.y)  
        else:
            self.movement.calculate_frame_movement()
        self.jump.walljump_active = False
        
        self.movement.collide_with_tilemap(level.tilemap)
                       
        if self.combat.attack.ticks_since_last < self.combat.attack.duration:
            self.combat.attack.active = True
            self.combat.attack.update()
            self.combat.attack_tiles(level)
            self.combat.attack_enemies(level)
            
        self.combat.enemies_attack(level)
            
            
    def render(self, canvas, offset):
        self.animate.render(canvas, offset)
        
        if self.combat.attack.active:
            if self.combat.attack.direction in [0, 2]:
                for hitbox, surface in zip(self.combat.attack.hitboxes, self.combat.attack.surfaces):
                    pos = (hitbox.x - offset[0], hitbox.y - offset[1])
                    canvas.blit(surface,pos)
            if self.combat.attack.direction in [1, 3]:
                for hitbox, surface in zip(self.combat.attack.hitboxes_vertical, self.combat.attack.surfaces_vertical):
                    pos = (hitbox.x - offset[0], hitbox.y - offset[1])
                    canvas.blit(surface,pos)

    def got_hit(self, enemy):
        setup.sfx['hit'].play()
        self.jump.active = False
        self.wallslide.active = False
        self.dash.active = False
        self.movement.collisions['down'] = False
        self.combat.hp -= 1
        self.movement.vel.y = self.jump.double_impulse
        self.combat.invulnerable = True
        self.movement.air_time = self.jump.coyote_time + 1
        self.combat.ticks_since_got_hit = 0
        if enemy.rect.centerx > self.rect.centerx:
            self.combat.knockback_direction = -1
        else:
            self.combat.knockback_direction = 1  
                   
    def got_hit_by_projectile(self, pos):
        setup.sfx['hit'].play()
        self.jump.active = False
        self.wallslide.active = False
        self.dash.active = False
        self.movement.collisions['down'] = False
        self.combat.hp -= 1
        self.movement.vel.y = self.jump.double_impulse
        self.combat.invulnerable = True
        self.movement.air_time = self.jump.coyote_time + 1
        self.combat.ticks_since_got_hit = 0
        if pos.x > self.rect.centerx:
            self.combat.knockback_direction = -1
        else:
            self.combat.knockback_direction = 1  
                 
    def got_hit_by_spike(self):
        setup.sfx['hit'].play()
        self.jump.active = False
        self.wallslide.active = False
        self.dash.active = False
        self.movement.collisions['down'] = False
        self.combat.hp -= 1
        self.movement.vel.y = self.jump.double_impulse
        self.combat.invulnerable = True
        self.combat.ticks_since_got_hit = 0
        self.movement.air_time = self.jump.coyote_time + 1
        if self.animate.flip:
            self.combat.knockback_direction = 1
        else:
            self.combat.knockback_direction = -1
            