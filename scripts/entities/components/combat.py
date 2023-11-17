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
        
    def knockback(self):
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