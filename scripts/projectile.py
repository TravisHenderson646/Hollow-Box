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
        self.terminal_velocity = 3
        
    
        
    def update(self, tilemap, player):
        self.pos += self.vel
        self.vel.y += self.gravity
        self.vel.y = min(self.vel.y, self.terminal_velocity)
        self.hot_chunk = ((self.pos.x + setup.CHUNK_SIZE[0] / 2) // setup.CHUNK_SIZE[0], (self.pos.y + setup.CHUNK_SIZE[1] / 2) // setup.CHUNK_SIZE[1])
        if tilemap.check_point(self.pos, self.hot_chunk):
            self.dead = True
        elif not player.combat.invulnerable:
            if player.rect.collidepoint(self.pos):
                player.got_hit_by_projectile(self.pos) # todo i should put this in this projectile class, take it out of player class
            
    def render(self, canvas: pg.Surface, offset):
        canvas.blit(self.image, (floor(self.pos.x - offset[0] - self.width / 2), floor(self.pos.y - offset[1] - self.height / 2)))