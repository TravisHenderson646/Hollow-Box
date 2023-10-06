import pygame as pg

from scripts.tilemap import Tilemap
from .biome_1 import Biome_1


class Level_1(Biome_1):
    def __init__(self):
        super().__init__()        
        self.level = 0 # Set starting level to 0
        self.map_id = 4           
        self.tilemap = Tilemap(tile_size=32) # Create an instance of the Tilemap class
        self.tilemap.process_tilemap('data/maps/' + str(self.map_id) + '.json')
        self.enemies = []
    
    def entry(self, exit):
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
        
    def render(self, canvas: pg.Surface):
        canvas = super().render(canvas)
        canvas.fill((0, 230, 170), pg.Rect(self.player.pos.x - self.rounded_scroll[0], self.player.pos.y - self.rounded_scroll[1], 24,25))
        for tile in self.tilemap.interactable_tiles:
        #     print(tile.rect)
            canvas.fill((230, 25, 170), pg.Rect(tile.rect.x - self.rounded_scroll[0], tile.rect.y - self.rounded_scroll[1], tile.rect.w,tile.rect.h))
       # canvas.fill((50,150,150), (tester[0] * screen.get_width - self.rounded_scroll[0]+25, tester[1] * disp_width - self.rounded_scroll[1], setup.PLAYER_COLLISION_SIZE[0], setup.PLAYER_COLLISION_SIZE[1]))
       
        return canvas