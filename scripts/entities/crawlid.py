import pygame as pg

from scripts.entities.physics_entity import PhysicsEntity

class Crawlid(PhysicsEntity):
    def __init__(self, pos):
        self.size = (14, 10)
        super().__init__('crawlid', pos, self.size)
        self.speed = 0.2
        self.movement[0] = True
        
    def update(self):
        super().update()
        if self.collisions['right'] or self.collisions['left']:
            self.movement[0] = not self.movement[0]
            self.movement[1] = not self.movement[1]