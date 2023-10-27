from math import cos, floor

import pygame as pg

from scripts.text_handler import DialogueBox
from scripts.setup import assets
from scripts.story import jump_unlock_text

class JumpUnlock:
    def __init__(self, pos):
        self.name = 'jump'
        self.pos = pos
        self.image = assets['jump'].copy()
        self.rect = pg.FRect(*pos, self.image.get_width(), self.image.get_height())
        self.tick = 0
        self.text = DialogueBox((50, 9), jump_unlock_text)
        
    def picked_up(self, player):
        self.text.pos = (self.pos[0] - 5, self.pos[1] - 10)
        player.jump.unlocked = True
        self.text.start()
        
    def update(self):
        self.tick += 1
        self.rect.y = self.pos[1] + cos(self.tick / 15) * 3.5
        
    def render(self, canvas, offset):
        canvas.blit(self.image, (self.rect.x - offset[0], self.rect.y - offset[1]))
        