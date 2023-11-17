import pygame as pg

from scripts.setup import CHUNK_SIZE

class Movement:
    def __init__(self, player):
        self.player = player
        self.movement = pg.Vector2() # input movement of player
        self.speed = 1.2
        self.vel = pg.Vector2()
        
        self.collisions = {'up': False, 'down': False, 'left': False, 'right': False}
        self.frame_movement = pg.Vector2()
        self.hot_chunk = (0, 0)
        
        self.gravity = 0.11
        self.terminal_vel = 3
        self.air_time = 0
            
    def collide_with_tilemap(self, tilemap):
        self.collisions = {'up': False, 'down': False, 'left': False, 'right': False}
        
        self.player.rect.x += self.frame_movement[0]
        
        # chunk tiles
        for rect in tilemap.chunks.get(self.hot_chunk, {}):
            if self.player.rect.colliderect(rect):
                self.collide_x(rect)
        # special solid tiles
        for tile in tilemap.current_solid_tiles:
            if self.player.rect.colliderect(tile.rect):
                self.collide_x(tile.rect)
                if tile.name == 'spike':
                    self.player.combat.hit_by_spike = True
                    
        self.player.rect.y += self.frame_movement[1]
        
        # chunk tiles
        for rect in tilemap.chunks.get(self.hot_chunk, {}):
            if self.player.rect.colliderect(rect):
                self.collide_y(rect)
        # special solid tiles
        for tile in tilemap.current_solid_tiles:
            if self.player.rect.colliderect(tile.rect):
                self.collide_y(tile.rect)
                if tile.name == 'spike':
                    self.player.combat.hit_by_spike = True 
                       
    def collide_x(self, rect):
        if self.frame_movement[0] > 0:
            self.player.rect.right = rect.left
            self.collisions['right'] = True
        if self.frame_movement[0] < 0:
            self.player.rect.left = rect.right
            self.collisions['left'] = True
        
    def collide_y(self, rect):
        if self.frame_movement[1] > 0:
            self.player.rect.bottom = rect.top
            self.collisions['down'] = True
        if self.frame_movement[1] < 0:
            self.player.rect.top = rect.bottom
            self.collisions['up'] = True  
        
    def frame_start(self):
        self.vel.x = 0
        self.air_time += 1
        
        if self.movement.x == 1:
            self.player.animate.flip = False
        if self.movement.x == -1:
            self.player.animate.flip = True
            
        if self.collisions['down'] or self.collisions['up']:
            self.vel.y = 0
            
        self.vel.y = min(self.terminal_vel, self.vel.y + self.gravity)
        
        self.hot_chunk = ((self.player.rect.centerx + CHUNK_SIZE[0] / 2) // CHUNK_SIZE[0], (self.player.rect.centery + CHUNK_SIZE[1] / 2) // CHUNK_SIZE[1])

    def calculate_frame_movement(self):
        if self.vel.x:
            self.frame_movement = pg.Vector2(self.vel.x, self.vel.y)   
        else:
            self.frame_movement = pg.Vector2((self.movement.x) * self.speed, self.vel.y)  