import pygame as pg

from scripts.tilemap import Tilemap
from .biome_1 import Biome_1


class Level_2(Biome_1):
    def __init__(self):
        super().__init__()
        self.level = 1
        self.map_id = 4
        self.tilemap = Tilemap(tile_size=32) # Create an instance of the Tilemap class
        self.tilemap.process_tilemap('data/maps/' + str(self.map_id) + '.json')
        self.enemies = []
    
    def entry(self, exit):
        super().entry()

        # todo: camera should probably be a class
        self.scroll = pg.Vector2(200, 100) # Initial camera position
        self.rounded_scroll = pg.Vector2(200, 100) # Rounded fix for camera scroll rendering
    
    def reset(self):
        super().reset()
        self.scroll = pg.Vector2(200, 100) # Initial camera position
        self.rounded_scroll = pg.Vector2(200, 100) # Rounded fix for camera scroll rendering
        
    def process_event(self, event):  
        super().process_event(event)
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_p: #for testing
                self.done = True
                self.next = 'level1'

    def update(self):
        super().update()
        
    def render(self, canvas: pg.Surface):
        canvas = super().render(canvas)      
        return canvas