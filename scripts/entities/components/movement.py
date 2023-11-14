import pygame as pg

from scripts.setup import CHUNK_SIZE



class Movement:
    def __init__(self, entity):
        self.entity = entity
        self.movement = pg.Vector2() # input movement of entity
        self.speed = 1
        self.vel = pg.Vector2()
        
        self.collisions = {'up': False, 'down': False, 'left': False, 'right': False}
        self.frame_movement = pg.Vector2()
        self.hot_chunk = (0, 0)
        
        self.gravity = 0.11
        self.terminal_vel = 3
            
    def collide_with_tilemap(self, tilemap):
        self.collisions = {'up': False, 'down': False, 'left': False, 'right': False}
        
        self.entity.rect.x += self.frame_movement[0]
        
        # chunk tiles
        for rect in tilemap.chunks.get(self.hot_chunk, {}):
            if self.entity.rect.colliderect(rect):
                self.collide_x(rect)
        # special solid tiles
        for tile in tilemap.current_solid_tiles:
            if self.entity.rect.colliderect(tile.rect):
                self.collide_x(tile.rect)
                if tile.name == 'spike':
                    self.entity.combat.hit_by_spike = True
                    
        self.entity.rect.y += self.frame_movement[1]
        
        # chunk tiles
        for rect in tilemap.chunks.get(self.hot_chunk, {}):
            if self.entity.rect.colliderect(rect):
                self.collide_y(rect)
        # special solid tiles
        for tile in tilemap.current_solid_tiles:
            if self.entity.rect.colliderect(tile.rect):
                self.collide_y(tile.rect)
                if tile.name == 'spike':
                    self.entity.combat.hit_by_spike = True 
                       
    def collide_x(self, rect):
        if self.frame_movement[0] > 0:
            self.entity.rect.right = rect.left
            self.collisions['right'] = True
        if self.frame_movement[0] < 0:
            self.entity.rect.left = rect.right
            self.collisions['left'] = True
        
    def collide_y(self, rect):
        if self.frame_movement[1] > 0:
            self.entity.rect.bottom = rect.top
            self.collisions['down'] = True
        if self.frame_movement[1] < 0:
            self.entity.rect.top = rect.bottom
            self.collisions['up'] = True  
        
    def frame_start(self):
        self.vel.x = 0
        
        if self.movement.x == 1:
            self.entity.animate.flip = False
        if self.movement.x == -1:
            self.entity.animate.flip = True
            
        if self.collisions['down'] or self.collisions['up']:
            self.vel.y = 0
            
        self.vel.y = min(self.terminal_vel, self.vel.y + self.gravity)
        
        self.hot_chunk = ((self.entity.rect.centerx + CHUNK_SIZE[0] / 2) // CHUNK_SIZE[0], (self.entity.rect.centery + CHUNK_SIZE[1] / 2) // CHUNK_SIZE[1])
      
    def turn_around_at_ledge(self, tilemap):
        if self.collisions['down']:
            if self.movement.x == -1:    
                check_pos = (self.entity.rect.left - 1, self.entity.rect.bottom + 1)
            else:
                check_pos = (self.entity.rect.right + 1, self.entity.rect.bottom + 1)
            if not tilemap.check_point(check_pos, self.hot_chunk):
                self.movement.x = -self.movement.x 
        
    def bonk(self):
        if (self.collisions['right'] and (self.movement.x == 1)) or (self.collisions['left'] and (self.movement.x == -1)):
            self.movement.x = -self.movement.x

    def calculate_frame_movement(self):
        if self.vel.x:
            self.frame_movement = pg.Vector2(self.vel.x, self.vel.y)   
        else:
            self.frame_movement = pg.Vector2((self.movement.x) * self.speed, self.vel.y)  