from math import cos, floor

import pygame as pg

from scripts.text_handler import DialogueBox
from scripts.setup import assets
from scripts.story import dash_unlock_text

class DashUnlock:
    def __init__(self, pos):
        self.name = 'dash'
        self.pos = pos
        self.image = assets['dash'].copy()
        self.rect = pg.FRect(*pos, self.image.get_width(), self.image.get_height())
        self.tick = 0
        self.text = DialogueBox((50, 9), dash_unlock_text)
        self.dead = False
        
    def picked_up(self, player):
        self.text.pos = (self.pos[0] - 5, self.pos[1] - 10)
        player.dash.unlocked = True
        self.text.start()
        
    def update(self, tilemap, player):
        self.tick += 1
        self.rect.y = self.pos[1] + cos(self.tick / 15) * 3.5
        
    def render(self, canvas, offset):
        canvas.blit(self.image, (self.rect.x - offset[0], self.rect.y - offset[1]))
        