import pygame as pg

from scripts import setup
from scripts.tilemap import Tilemap
from states.biome_1 import Biome_1


class Level_3(Biome_1):
    def __init__(self):
        super().__init__()        
        self.level = 2 # Set starting level to 0
        self.map_id = 2
        self.tilemap = Tilemap(tile_size=32) # Create an instance of the Tilemap class
        self.tilemap.process_tilemap('data/maps/' + str(self.map_id) + '.json')
        self.enemies = []
    
    def start(self):
        super().start()

        # todo: camera should probably be a class 
                
        if self.previous == 'level1':
            for tile in self.tilemap.entrances:
                if 'west' in tile.tags:
                    Biome_1.player.pos = pg.Vector2(tile.pos)
                    self.camera.pos = pg.Vector2(tile.pos[0] - setup.CANVAS_SIZE[0]/2, tile.pos[1] - setup.CANVAS_SIZE[1]/2) # Initial camera position
   
    
    def reset(self):
        super().reset()
        
    def process_event(self, event):
        super().process_event(event)

    def update(self):
        super().update()
        for tile in self.tilemap.exits:
            if tile.rect.colliderect(Biome_1.player.rect()):
                if 'west' in tile.tags:
                    self.done = True
                    self.next = 'level1'
        
    def render(self, canvas: pg.Surface):
        canvas = super().render(canvas)
        canvas.fill((200, 120, 170), pg.Rect(Biome_1.player.pos.x - self.camera.rounded_pos[0], Biome_1.player.pos.y - self.camera.rounded_pos[1], 24,25))
    
        return canvas