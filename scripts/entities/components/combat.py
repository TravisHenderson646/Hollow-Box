import pygame as pg

from scripts.setup import sfx

class Combat:
    def __init__(self, entity):
        self.entity = entity
        self.hurtboxes = [entity.rect]
        self.hitboxes = [entity.rect]
        self.dead = False
        self.hit_by_spike = False
        self.ticks_since_got_hit = 500
        self.number_of_invuln_frames = 8 # should be 1 + (however long the player's attack is)
        self.got_hit_direction = 0 # 0right 1down 2left 3up
        self.invulnerable = False # todo this attr might be useless
        self.hp = 3
        self.damage = 1
        self.geo = 2
        
    def frame_start(self):
        if self.hp <= 0:
            self.dead = True
        self.invulnerable = False
        
    def hit_player(self, player):
        if not player.invulnerable:
            for hitbox in self.hitboxes:
                if player.hurtboxes[0].colliderect(hitbox):
                    sfx['hit'].play()
                    player.jump.active = False
                    player.wallslide.active = False
                    player.dash.active = False
                    player.collisions['down'] = False
                    player.hp -= self.damage
                    player.vel.y = player.jump.double_impulse
                    player.invulnerable = True
                    player.air_time = player.jump.coyote_time + 1
                    player.ticks_since_player_got_hit = 0
                    if self.entity.rect.centerx > player.hurtboxes[0].centerx:
                        player.knockback_direction = -1
                    else:
                        player.knockback_direction = 1  
        
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
            if player.attack.ticks_since_last < player.attack.duration:
                for hurtbox in self.hurtboxes:
                    if hurtbox.collidelist(player.attack.hitbox_list[player.attack.active_hitboxes]) + 1:
                        player.attack.ticks_since_knockback = 0
                        player.invulnerable = False
                        self.hp -= player.attack.damage
                        self.ticks_since_got_hit = 0 # multi hit prevention from 1 attack
                        self.got_hit_direction = player.attack.direction
                        sfx['dash'].play()