import pygame as pg

from scripts.entities.components.combat import Combat
from scripts.entities.components.movement import Movement
from scripts.entities.components.animate import Animate
from scripts import setup

class Slug:
    def __init__(self, pos):
        self.name = 'slug'
        self.size = (14, 10)
        self.rect = pg.FRect(*pos, *self.size)
        self.movement = Movement(self)
        self.movement.movement.x = -1
        self.movement.speed = 0.3
        self.animate = Animate(self)
        self.combat = Combat(self)
        
    def update(self, tilemap, player):
        self.combat.frame_start()
        self.movement.frame_start()
        
        self.combat.hit_by_player(player)
        self.combat.hit_player(player)
        
        self.movement.turn_around_at_ledge(tilemap)
        self.movement.bonk()
        
        self.movement.calculate_frame_movement()
        self.movement.collide_with_tilemap(tilemap)

        self.animate.animation.tick() 