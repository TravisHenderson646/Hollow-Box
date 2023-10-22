import pygame as pg

from scripts.entities.physics_entity import PhysicsEntity

class Slug(PhysicsEntity):
    def __init__(self, pos):
        self.size = (14, 10)
        super().__init__('slug', pos, self.size)
        self.speed = 0.3
        self.movement.x = -1
        self.hp = 3
        
    def update(self, tilemap, player):
        super().update()
        self.invulnerable = False
        if self.ticks_since_got_hit < 14: # this number could be lower
            self.ticks_since_got_hit += 1
            self.invulnerable = True
            match self.got_hit_direction:
                case 2: #left
                    self.vel.x -= 1.5
                case 0: #right
                    self.vel.x += 1.5
                case 3: #up
                    self.vel.y = -1
                    
        if (self.collisions['right'] and (self.movement.x == 1)) or (self.collisions['left'] and (self.movement.x == -1)):
            self.movement.x = -self.movement.x
        
        ### Turn around at a ledge
        if self.collisions['down']:
            if self.movement.x == -1:    
                check_pos = (self.rect.left - 1, self.rect.bottom + 1)
            else:
                check_pos = (self.rect.right + 1, self.rect.bottom + 1)
            if not tilemap.check_point(check_pos, self.hot_chunk):
                self.movement.x = -self.movement.x 
        ###           
        
        
        
        super().calculate_frame_movement()

