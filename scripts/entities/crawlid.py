import pygame as pg

from scripts.entities.physics_entity import PhysicsEntity

class Crawlid(PhysicsEntity):
    def __init__(self, pos):
        self.size = (14, 10)
        super().__init__('crawlid', pos, self.size)
        self.speed = 0.2
        self.movement[0] = True
        self.hp = 3
        
    def update(self, tilemap):
        super().update()
        self.invulnerable = False
        self.ticks_since_got_hit += 1
        if self.ticks_since_got_hit < 10: # this number could be lower
            self.invulnerable = True
        if self.collisions['right'] or self.collisions['left']:
            self.movement[0] = not self.movement[0]
            self.movement[1] = not self.movement[1]
        
        ### Turn around at a ledge
        if self.collisions['down']:
            if self.movement[0]:    
                check_pos = (self.rect.left - 1, self.rect.bottom + 1)
            else:
                check_pos = (self.rect.right + 1, self.rect.bottom + 1)
            if not tilemap.check_point(check_pos, self.hot_chunk):
                self.movement[0] = not self.movement[0]
                self.movement[1] = not self.movement[1] 
        ###           
        super().calculate_frame_movement()

