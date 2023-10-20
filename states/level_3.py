import pygame as pg

from scripts import setup
from scripts.tilemap import Tilemap
from states.biome_1 import Biome_1


class Level_3(Biome_1):
    def __init__(self):
        super().__init__()        
        self.level = 2
        self.map_id = 2
        self.tilemap = Tilemap(tile_size=8) # Create an instance of the Tilemap class
        self.tilemap.process_tilemap('data/maps/' + str(self.map_id) + '.json')
        self.enemies = []
    
    def start(self):
        super().start()
        if self.previous == 'level2': # if you came from level 2
            for tile in self.tilemap.entrances:
                if 'north' in tile.tags: # find the tile for level 2
                    Biome_1.player.rect.topleft = tile.rect.topleft
                    
    def process_event(self, event):
        super().process_event(event)

    def update(self):
        super().update()
        for tile in self.tilemap.exits:
            if tile.rect.colliderect(Biome_1.player.rect):
                if 'north' in tile.tags:
                    self.done = True
                    self.next = 'level2'
        
    def render(self, canvas: pg.Surface):
        canvas = super().render(canvas)
        return canvas