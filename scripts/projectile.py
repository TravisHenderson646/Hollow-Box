from math import floor

import pygame as pg

from scripts import setup

class Projectile: # todo could inherit from entity?
    def __init__(self, pos, vel):
        self.image = setup.assets['projectile'].copy()
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.pos = pg.Vector2(pos)
        self.vel = pg.Vector2(vel)
        self.dead = False
        self.speed = 2
        self.gravity = 0.07
        self.hot_chunk = (0, 0)
        
    def update(self, tilemap):
        self.pos += self.vel
        self.vel.y += self.gravity
        self.hot_chunk = ((self.pos.x + setup.CHUNK_SIZE[0] / 2) // setup.CHUNK_SIZE[0], (self.pos.y + setup.CHUNK_SIZE[1] / 2) // setup.CHUNK_SIZE[1])
        if tilemap.check_point(self.pos, self.hot_chunk):
            self.dead = True
            
    def render(self, canvas: pg.Surface, offset):
        canvas.blit(self.image, (floor(self.pos.x - offset[0] - self.width / 2), floor(self.pos.y - offset[1] - self.height / 2)))