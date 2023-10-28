import pygame as pg

from scripts import setup
from scripts.tilemap import Tilemap
from states.biome_1 import Biome_1
from scripts.entities.bird_guy import BirdGuy
from scripts.entities.bee_guy import BeeGuy


class Level_2(Biome_1):
    def __init__(self):
        super().__init__()
        self.level = 1
        self.map_id = 1
        self.tilemap = Tilemap(tile_size=32) # Create an instance of the Tilemap class
        self.tilemap.process_tilemap('data/maps/' + str(self.map_id) + '.json')
        self.enemies = []
        for tile in self.tilemap.npcs:
            if 'bird_guy' in tile.tags:
                self.npcs.append(BirdGuy(tile.rect.topleft))
            if 'bee_guy' in tile.tags:
                self.npcs.append(BeeGuy(tile.rect.topleft))
        for npc in self.npcs:
            self.dialogue_boxes = npc.dialogue
            self.solid_entities.append(npc)
    
    def start(self):
        super().start()
        
        if self.previous == 'level1': # if you came from level 1
            for tile in self.tilemap.entrances:
                if 'west' in tile.tags: # find the entrance for level 1
                    Biome_1.player.rect.topleft = tile.rect.topleft
        if self.previous == 'level3':
            for tile in self.tilemap.entrances:
                if 'east' in tile.tags:
                    Biome_1.player.rect.topleft = tile.rect.topleft
                    
    def process_action(self, action):  
        super().process_action(action)
        if action == 'p':
            self.done = True
            self.next = 'level1'

    def update(self):
        super().update()
        for tile in self.tilemap.exits:
            if tile.rect.colliderect(Biome_1.player.rect):
                if 'west' in tile.tags:
                    self.done = True
                    self.next = 'level1'
        for tile in self.tilemap.exits:
            if tile.rect.colliderect(Biome_1.player.rect):
                if 'east' in tile.tags:
                    self.done = True
                    self.next = 'level3'
        
    def render(self, canvas: pg.Surface):
        canvas = super().render(canvas)      
        return canvas