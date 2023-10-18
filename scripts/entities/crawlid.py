import pygame as pg

from scripts.entities.physics_entity import PhysicsEntity

class Crawlid(PhysicsEntity):
    def __init__(self, pos):
        self.size = (14, 10)
        super().__init__('crawlid', pos, self.size)
        self.speed = 0.2
        self.movement[0] = True
        
    def update(self, tilemap):
        super().update()
        if self.collisions['right'] or self.collisions['left']:
            self.movement[0] = not self.movement[0]
            self.movement[1] = not self.movement[1]
        
        ### Turn at a ledge
        if self.collisions['down']:
            at_ledge = True
            if self.movement[0]:    
                pos = (self.rect.left - 1, self.rect.bottom + 5)
            else:
                pos = (self.rect.right + 1, self.rect.bottom + 5)
            for rect in tilemap.chunks.get(self.hot_chunk, {}):
                if rect.collidepoint(pos[0], pos[1]):
                    at_ledge = False
            for rect in [tile.rect for tile in tilemap.current_breakable_tiles]:
                if rect.collidepoint(pos[0], pos[1]):
                    at_ledge = False
            if at_ledge:
                self.movement[0] = not self.movement[0]
                self.movement[1] = not self.movement[1] 
        ###
                       
        self.frame_movement = ( # (x, y)
            (self.movement[1] - self.movement[0]) * self.speed + self.vel.x,
             self.vel.y)     