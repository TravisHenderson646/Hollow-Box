from math import cos, floor

import pygame as pg

from scripts.text_handler import DialogueBox
from scripts.setup import assets
from scripts.story import double_jump_unlock_text

class DoubleJumpUnlock:
    def __init__(self, pos):
        self.name = 'double_jump'
        self.pos = pos
        self.image = assets['double_jump'].copy()
        self.rect = pg.FRect(*pos, self.image.get_width(), self.image.get_height())
        self.tick = 0
        self.text = DialogueBox((70, 9), double_jump_unlock_text)
        self.dead = False
        
    def picked_up(self, player):
        self.text.pos = (self.pos[0] - 5, self.pos[1] - 10)
        player.jump.double_unlocked = True
        self.text.start()
        
        
    def update(self, tilemap, player):
        self.tick += 1
        self.rect.y = self.pos[1] + cos(self.tick / 15) * 3.5
      
        if self.rect.colliderect(player.rect):
            self.picked_up(player)
            self.dead = True
        
    def render(self, canvas, offset):
        canvas.blit(self.image, (self.rect.x - offset[0], self.rect.y - offset[1]))
        