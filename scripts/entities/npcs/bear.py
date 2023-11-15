from math import floor, cos

import pygame as pg

from scripts.entities.components.movement import Movement
from scripts.entities.components.animate import Animate
from scripts.text_handler import DialogueBox
from scripts.story import bird_guy_lines
from scripts.setup import assets

class Bear:
    def __init__(self, pos):
        self.name = 'bear'
        self.size = (6, 8)
        self.rect = pg.FRect(*pos, *self.size)
        self.interact_rect = self.rect
        self.movement = Movement(self)
        self.movement.movement.x = 1
        self.movement.speed = 0.1
        self.animate = Animate(self)
        self.dialogue = DialogueBox((90,17), bird_guy_lines)
        self.dialogue.pos = (self.rect.x - 30, self.rect.y - 18)
        self.chevron = assets['chevron'].copy()
        self.chevron_width = self.chevron.get_width()
        self.chevron_tick = 0
        
    def update(self, tilemap, player):
        self.movement.frame_start()
        self.movement.turn_around_at_ledge(tilemap)
        self.movement.bonk()
        if self.dialogue.active:
            self.dialogue.pos = (self.rect.x - 30, self.rect.y - 18)
        else:
            self.movement.calculate_frame_movement()
            self.movement.collide_with_tilemap(tilemap)

        self.animate.animation.tick() 
        
        self.can_interact_flag = False
        if self.interact_rect.colliderect(player.hurtboxes[0]):
            self.can_interact_flag = True
            if player.try_interact_flag == True:
                self.dialogue.start()
                
    def render(self, canvas:pg.Surface, offset):
        pos = pg.Vector2(floor(self.rect.x), floor(self.rect.y)) # todo i dont need to calc this pos anymore or maybe it should be pass into render
        self.animate.render(canvas, offset)
        if self.can_interact_flag:
            self.chevron_tick += 1
            canvas.blit(self.chevron, (pos[0] - offset[0], pos[1] - 10 - offset[1] + cos(self.chevron_tick / 15) * 3))