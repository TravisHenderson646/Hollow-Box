import pygame as pg

from scripts.entities.physics_entity import PhysicsEntity
from scripts.text_handler import DialogueBox
from scripts.debugger import debugger
from scripts.story import bird_guy_lines

class BirdGuy(PhysicsEntity):
    def __init__(self, pos):
        self.size = (25, 25) # todo: could probably automate size generation from image but i guess most enemies will have a defined hitbox
        super().__init__('bird_guy', pos, self.size)
        self.speed = 0.1
        self.hp = 0
        self.dead = True
        self.movement.x = -1
        self.dialogue = DialogueBox((80,40), bird_guy_lines)
        
    def update(self, tilemap):
        super().update()
        
        if (self.collisions['right'] and (self.movement.x == 1)) or (self.collisions['left'] and (self.movement.x == -1)):
            self.movement.x = -self.movement.x
        
        ### Turn around at a ledge
        if self.movement.x == -1:    
            check_pos = (self.rect.left - 1, self.rect.bottom + 1)
        else:
            check_pos = (self.rect.right + 1, self.rect.bottom + 1)
        if not tilemap.check_point(check_pos, self.hot_chunk):
            self.movement.x = -self.movement.x 
        ###                   
        if self.dialogue.active:
            self.dialogue.pos = (self.rect.x - 60, self.rect.y - 60)
            self.dialogue.update()
            self.vel.x = 0
        self.vel.y = 0
        
        super().calculate_frame_movement()

        