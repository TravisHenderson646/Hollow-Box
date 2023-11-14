import pygame as pg

from scripts.entities.components.combat import Combat
from scripts.entities.components.movement import Movement
from scripts.entities.components.animate import Animate
from scripts import setup

class Slug:
    def __init__(self, pos, size):
        self.name = 'slug'
        self.rect = pg.FRect(*pos, *size)
        self.movement = Movement(self)
        self.animate = Animate(self)
        self.combat = Combat(self)
        
    def update(self, tilemap, player):
        self.combat.frame_start()
        self.movement.frame_start()
        
        self.combat.recovery_frames()
        self.movement.turn_around_at_ledge(tilemap)
        self.movement.bonk()
        
        self.movement.calculate_frame_movement()

        self.animate.animation.tick()
        
        