import pygame as pg

from scripts.entities.player.attack import Attack
from scripts.setup import sfx

class Combat:
    def __init__(self, player):
        self.player = player
        self.hurtboxes = [player.rect]
        self.attack = Attack(player)
        self.dead = False
        self.frames_dead = 0
        self.death_duration = 120
        self.hit_by_spike = False
        self.ticks_since_got_hit = 500
        self.number_of_invuln_frames = 8 # should be 1 + (however long the player's attack is)
        self.got_hit_direction = 0 # 0right 1down 2left 3up
        self.invulnerable = False # todo this attr might be useless
        self.hp = 5
        self.damage = 1
        self.knockback_speed = 3
        self.knockback_direction = 1# left is -1
        self.got_hit_knockback_duration = 10
        self.in_got_hit = False
        self.invulnerable_duration = 120
        
    def frame_start(self):
        if self.hp <= 0:
            self.dead = True
        self.invulnerable = False
        self.attack.active = False
        self.attack.ticks_since_last += 1
        self.ticks_since_got_hit += 1