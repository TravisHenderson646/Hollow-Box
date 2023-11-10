import pygame as pg



class Combat:
    def __init__(self, entity):
        self.entity = entity
        self.hurtboxes = [entity.rect]
        self.hitboxes = [entity.rect]
        self.dead = False
        self.hit_by_spike = False
        self.ticks_since_got_hit = 500
        self.got_hit_direction = 0 # 0right 1down 2left 3up
        self.invulnerable = False