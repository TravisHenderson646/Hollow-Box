from math import floor, cos

import pygame as pg

from scripts.entities.physics_entity import PhysicsEntity
from scripts.text_handler import DialogueBox
from scripts.debugger import debugger
from scripts.story import bee_guy_lines
from scripts.setup import assets

class BeeGuy(PhysicsEntity):
    def __init__(self, pos):
        self.size = (25, 25) # todo: could probably automate size generation from image but i guess most enemies will have a defined hitbox
        super().__init__('bee_guy', pos, self.size)
        self.dialogue = DialogueBox((80,17), bee_guy_lines)
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
                self.speed = 3
                self.ticks_since_look_what_i_can_do = 0
        else:
            self.ticks_since_look_what_i_can_do += 1
            if self.dialogue.active == False:
                self.look_what_i_can_do = False
                self.speed = 0.4
                self.ticks_since_look_what_i_can_do = 500
        
        
        ### Turn around at a ledge
        if self.movement.x == -1:    
            check_pos = (self.hurtboxes[0].left - 1, self.hurtboxes[0].bottom + 1)
        else:
            check_pos = (self.hurtboxes[0].right + 1, self.hurtboxes[0].bottom + 1)
        if not tilemap.check_point(check_pos, self.hot_chunk):
            self.movement.x = -self.movement.x 
        ###                
        self.dialogue.pos = (self.hurtboxes[0].x - 30, self.hurtboxes[0].y - 18)   
        if self.dialogue.active and (not self.look_what_i_can_do):
            self.frame_movement = pg.Vector2(0, 0)
        else:
            self.frame_movement.x = self.movement.x * self.speed
        self.vel.y = 0
        

    def render(self, canvas:pg.Surface, offset):
        pos = pg.Vector2(floor(self.hurtboxes[0].x), floor(self.hurtboxes[0].y))
        canvas.blit(pg.transform.flip(self.animation.img(), self.flip, False), (pos - offset + self.anim_offset))
        if self.can_interact_flag:
            self.chevron_tick += 1
            canvas.blit(self.chevron, (pos[0] + 7 - offset[0], pos[1] - 10 - offset[1] + cos(self.chevron_tick / 15) * 3))