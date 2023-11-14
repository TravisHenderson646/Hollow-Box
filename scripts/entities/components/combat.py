import pygame as pg



class Combat:
    def __init__(self, entity):
        self.entity = entity
        self.hurtboxes = [entity.rect]
        self.hitboxes = [entity.rect]
        self.dead = False
        self.hit_by_spike = False
        self.ticks_since_got_hit = 500
        self.number_of_invuln_frames = 6 # should be 1 + (however long the player's attack is)
        self.got_hit_direction = 0 # 0right 1down 2left 3up
        self.invulnerable = False
        self.hp = 3
        self.geo = 2
        
    def frame_start(self):
        if self.hp <= 0:
            self.dead = True
        self.invulnerable = False
        
    def recovery_frames(self):
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
        