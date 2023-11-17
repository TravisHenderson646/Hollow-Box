from math import floor

import pygame as pg

from scripts import setup

class Animate:
    def __init__(self, player):
        self.player = player
        self.flip = False
        self.animation = '' # this ends up as a class not a string so why ''
        self.anim_offset = pg.Vector2()
        self.set_animation('idle')
        
    def set_animation(self, animation):
        if animation !=self.animation:
            self.animation = animation
            self.animation = setup.assets[self.player.name + '/' + self.animation].copy() # game from tools instead maybe... maybe call this set animation and update it from a layer above like entities.updateanimation()

    def render(self, canvas:pg.Surface, offset):
        pos = pg.Vector2(floor(self.player.rect.x + self.anim_offset.x), floor(self.player.rect.y + self.anim_offset.y))
        canvas.blit(pg.transform.flip(self.animation.img(), self.flip, False), (pos - offset))