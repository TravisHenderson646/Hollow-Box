import pygame as pg

from scripts.setup import sfx

class Combat:
    def __init__(self, entity):
        self.entity = entity
        self.hurtboxes = [entity.rect]
        self.hitboxes = [entity.rect]
        self.dead = False
        self.frames_dead = 0
        self.death_duration = 120
        self.death_angle = 0
        self.death_speed = 2
        self.hit_by_spike = False
        self.ticks_since_got_hit = 500
        self.number_of_invuln_frames = 8 # should be 1 + (however long the player's attack is)
        self.got_hit_direction = 0 # 0right 1down 2left 3up
        self.invulnerable = False # todo this attr might be useless
        self.hp = 3
        self.damage = 1
        self.geo = 5
        
    def frame_start(self):
        if self.hp <= 0:
            self.dead = True
        self.invulnerable = False
        
    def hit_player(self, player):
        if not player.combat.invulnerable:
            for hitbox in self.hitboxes:
                if player.rect.colliderect(hitbox):
                    player.combat.invulnerable = True
                    sfx['hit'].play()
                    player.jump.active = False
                    player.wallslide.active = False
                    player.dash.active = False
                    player.movement.collisions['down'] = False
                    player.combat.hp -= self.damage
                    player.movement.vel.y = player.jump.double_impulse
                    player.movement.air_time = player.jump.coyote_time + 1
                    player.combat.ticks_since_got_hit = 0
                    if self.entity.rect.centerx > player.rect.centerx:
                        player.combat.knockback_direction = -1
                    else:
                        player.combat.knockback_direction = 1  
        
    def hit_by_player(self, player):
        if self.ticks_since_got_hit < self.number_of_invuln_frames:
            self.ticks_since_got_hit += 1
            self.invulnerable = True
            match self.got_hit_direction:
                case 2: #left
                    self.entity.movement.vel.x -= 1.5
                case 0: #right
                    self.entity.movement.vel.x += 1.5
                case 3: #up
                    self.entity.movement.vel.y = -1
        else:
            if player.combat.attack.ticks_since_last < player.combat.attack.duration:
                for hurtbox in self.hurtboxes:
                    if hurtbox.collidelist(player.combat.attack.hitbox_list[player.combat.attack.active_hitboxes]) + 1:
                        player.combat.attack.ticks_since_knockback = 0
                        player.combat.attack.in_knockback = True
                        player.combat.invulnerable = False
                        self.hp -= player.combat.attack.damage
                        self.ticks_since_got_hit = 0 # multi hit prevention from 1 attack
                        self.got_hit_direction = player.combat.attack.direction
                        sfx['dash'].play()