from math import floor, cos

import pygame as pg

from scripts.text_handler import DialogueBox
from scripts.debugger import debugger
from scripts.setup import assets

class Signpost:
    def __init__(self, pos, text):
        self.name = 'slug'
        self.size = (7, 10)
        self.rect = pg.FRect(*pos, *self.size)
        self.image = assets['signpost']
        self.interact_rect = pg.FRect(self.rect.x - 30, self.rect.y - 30, 70, 70)
        self.can_interact_flag = False
        self.dialogue = DialogueBox((80,9), text)
        self.dialogue.pos = (self.rect.x - 30, self.rect.y - 18)
        self.chevron = assets['chevron'].copy()
        self.chevron_width = self.chevron.get_width()
        self.chevron_tick = 0
        
    def update(self, tilemap, player):
        self.can_interact_flag = False
        if self.interact_rect.colliderect(player.rect):
            self.can_interact_flag = True
            if player.try_interact_flag == True:
                self.dialogue.start()
                
    def render(self, canvas:pg.Surface, offset):
        pos = pg.Vector2(floor(self.rect.x), floor(self.rect.y))
        canvas.blit(self.image, (pos - offset))
        if self.can_interact_flag:
            self.chevron_tick += 1
            canvas.blit(self.chevron, (pos[0] - offset[0], pos[1] - 10 - offset[1] + cos(self.chevron_tick / 15) * 3))