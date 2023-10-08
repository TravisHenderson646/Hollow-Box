import pygame as pg

from scripts.tilemap import Tilemap
from .biome_1 import Biome_1


class Level_1(Biome_1):
    def __init__(self):
        super().__init__()        
        self.level = 0 # Set starting level to 0
        self.map_id = 0
        self.tilemap = Tilemap(tile_size=32) # Create an instance of the Tilemap class
        self.tilemap.process_tilemap('data/maps/' + str(self.map_id) + '.json')
        self.enemies = []
    
    def entry(self):
        super().entry()

        # todo: camera should probably be a class
        self.scroll = pg.Vector2(100, 200) # Initial camera position
        self.rounded_scroll = pg.Vector2(100, 200) # Rounded fix for camera scroll rendering       
    
    def reset(self):
        super().reset()
        # todo: camera should probably be a class
        self.scroll = pg.Vector2(100, 200) # Initial camera position
        self.rounded_scroll = pg.Vector2(100, 200) # Rounded fix for camera scroll rendering
        
    def process_event(self, event):
        super().process_event(event)
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_p: #for testing
                self.done = True
                self.next = 'level2'

    def update(self):
        super().update()
        for tile in self.tilemap.flagged_tiles:
            if tile.rect.colliderect(self.player.rect()):
                if tile.flag == 'west_exit':
                    self.done = True
                    self.next = 'level2'
        
    def render(self, canvas: pg.Surface):
        canvas = super().render(canvas)
        canvas.fill((200, 120, 170), pg.Rect(self.player.pos.x - self.rounded_scroll[0], self.player.pos.y - self.rounded_scroll[1], 24,25))
    
        return canvas