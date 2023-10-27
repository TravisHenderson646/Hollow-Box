from math import floor, cos

import pygame as pg

from scripts.entities.physics_entity import PhysicsEntity
from scripts.text_handler import DialogueBox
from scripts.debugger import debugger
from scripts.story import bird_guy_lines
from scripts.setup import assets

class BirdGuy(PhysicsEntity):
    def __init__(self, pos):
        self.size = (25, 25) # todo: could probably automate size generation from image but i guess most enemies will have a defined hitbox
        super().__init__('bird_guy', pos, self.size)
        self.dialogue = DialogueBox((80,17), bird_guy_lines)
        self.chevron = assets['chevron'].copy()
        self.chevron_width = self.chevron.get_width()
        self.chevron_tick = 0
        self.can_interact_flag = False
        self.speed = 0.4
        self.hp = 69
        self.dead = True
        self.movement.x = -1
        self.look_what_i_can_do = False
        self.ticks_since_look_what_i_can_do = 500
        
    def update(self, tilemap):
        super().update()
        
        if (self.collisions['right'] and (self.movement.x == 1)) or (self.collisions['left'] and (self.movement.x == -1)):
            self.movement.x = -self.movement.x
        
        if self.look_what_i_can_do == False:
            if (self.dialogue.active) and (self.dialogue.batch == 0) and (self.dialogue.message >= len(self.dialogue.script[0]) -1):
                self.look_what_i_can_do = True
                self.ticks_since_look_what_i_can_do = 0
        else:
            self.ticks_since_look_what_i_can_do += 1
            if self.dialogue.active == False:
                self.look_what_i_can_do = False
                self.ticks_since_look_what_i_can_do = 500
        
        ### Turn around at a ledge
        if self.movement.x == -1:    
            check_pos = (self.rect.left - 1, self.rect.bottom + 1)
        else:
            check_pos = (self.rect.right + 1, self.rect.bottom + 1)
        if not tilemap.check_point(check_pos, self.hot_chunk):
            self.movement.x = -self.movement.x 
        ###                   
        if self.dialogue.active:
            self.dialogue.pos = (self.rect.x - 30, self.rect.y - 18)
            self.frame_movement = pg.Vector2(0, 0)
        else:
            self.frame_movement.x = self.movement.x * self.speed
        self.vel.y = 0
        

    def render(self, surf:pg.Surface, offset):
        pos = pg.Vector2(floor(self.rect.x), floor(self.rect.y))
        if self.look_what_i_can_do:
            surf.blit(pg.transform.flip(self.animation.img(), self.flip, True), (pos - offset + self.anim_offset))
        else:
            surf.blit(pg.transform.flip(self.animation.img(), self.flip, False), (pos - offset + self.anim_offset))
            if self.can_interact_flag:
                self.chevron_tick += 1
                surf.blit(self.chevron, (pos[0] + 7 - offset[0], pos[1] - 10 - offset[1] + cos(self.chevron_tick / 15) * 3))