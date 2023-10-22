import pygame as pg

from scripts.entities.physics_entity import PhysicsEntity
from scripts.debugger import debugger

class Gnat(PhysicsEntity):
    def __init__(self, pos):
        self.size = (4, 4)
        super().__init__('gnat', pos, self.size)
        self.speed = 0.8
        self.hp = 3
        self.idle_radius = 80
        self.active_radius = 300
        self.active = False
        
    def update(self, tilemap, player):
        super().update()
                    
        self.vel.x = 0
        self.vel.y = 0

        if pg.Vector2(self.rect.x, self.rect.y).distance_to((player.rect.x, player.rect.y)) < self.active_radius:
            self.active = False
        if pg.Vector2(self.rect.x, self.rect.y).distance_to((player.rect.x, player.rect.y)) < self.idle_radius:
            self.active = True
            
        if self.active:
         #enemy_position += (player_position - enemy_position).normal() * enemy_speed 
            self.vel = pg.Vector2(pg.Vector2(player.rect.center) - pg.Vector2(self.rect.center)).normalize() * self.speed
        self.invulnerable = False
        if self.ticks_since_got_hit < 14: # this number could be lower
            self.ticks_since_got_hit += 1
            self.invulnerable = True
            match self.got_hit_direction:
                case 2: #left
                    self.vel.x = 1.5
                case 0: #right
                    self.vel.x = 1.5
                case 3: #up
                    self.vel.y = -1
        
        
        
        super().calculate_frame_movement()

