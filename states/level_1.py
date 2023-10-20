import pygame as pg

from scripts import setup
from scripts.tilemap import Tilemap
from states.biome_1 import Biome_1


class Level_1(Biome_1):
    def __init__(self):
        super().__init__()        
        self.level = 0 # Set starting level to 0
        self.map_id = 0
        self.tilemap = Tilemap(tile_size=8) # Create an instance of the Tilemap class
        self.tilemap.process_tilemap('data/maps/' + str(self.map_id) + '.json')
        self.enemies = []
    
    def start(self):
        super().start()
        
        if self.previous == 'menu': # if you came from level 2
            for tile in self.tilemap.entrances:
                if 'west' in tile.tags: # find the tile for level 2
                    Biome_1.player.rect.topleft = tile.pos
        if self.previous == 'level2': # if you came from level 2
            for tile in self.tilemap.entrances:
                if 'west' in tile.tags: # find the tile for level 2
                    Biome_1.player.rect.topleft = tile.pos
        if self.previous == 'level3':
            for tile in self.tilemap.entrances:
                if 'east' in tile.tags:
                    Biome_1.player.rect.topleft = tile.pos
        
    def process_action(self, action):
        super().process_action(action)
        if action == 'p':
                self.done = True
                self.next = 'level2'

    def update(self):
        super().update()
        for tile in self.tilemap.exits:
            if tile.rect.colliderect(Biome_1.player.rect):
                if 'west' in tile.tags:
                    self.done = True
                    self.next = 'level2'
                if 'east' in tile.tags:
                    self.done = True
                    self.next = 'level3'
        
    def render(self, canvas: pg.Surface):
        canvas = super().render(canvas)
   #     canvas.fill((200, 120, 170), pg.Rect(Biome_1.player.pos.x - self.camera.rounded_pos[0], Biome_1.player.pos.y - self.camera.rounded_pos[1], 7,13))
    
        return canvas