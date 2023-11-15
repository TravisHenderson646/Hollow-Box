from math import floor, cos

import pygame as pg

from scripts.entities.physics_entity import PhysicsEntity
from scripts.text_handler import DialogueBox
from scripts.debugger import debugger
from scripts.setup import assets

class Signpost(PhysicsEntity):
    def __init__(self, pos, text):
        self.size = (7, 10) # todo: could probably automate size generation from image but i guess most enemies will have a defined hitbox
        super().__init__('signpost', pos, self.size)
        self.dialogue = DialogueBox((80,9), text)
        self.dialogue.pos = (self.hurtboxes[0].x - 30, self.hurtboxes[0].y - 18)
        self.chevron = assets['chevron'].copy()
        self.chevron_width = self.chevron.get_width()
        self.chevron_tick = 0
        self.can_interact_flag = False
        self.speed = 0.4
        self.hp = 69
        self.dead = True
        self.movement.x = 0
        
    def update(self, tilemap, player):
        self.frame_movement = pg.Vector2(0, 0) # todo try putting this in init

    def render(self, canvas:pg.Surface, offset):
        pos = pg.Vector2(floor(self.hurtboxes[0].x), floor(self.hurtboxes[0].y))
        canvas.blit(pg.transform.flip(self.animation.img(), self.flip, False), (pos - offset + self.anim_offset))
        if self.can_interact_flag:
            self.chevron_tick += 1
            canvas.blit(self.chevron, (pos[0] - offset[0], pos[1] - 10 - offset[1] + cos(self.chevron_tick / 15) * 3))