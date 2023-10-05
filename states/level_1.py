import os
import sys
import math
import random

import pygame as pg

from scripts.entities.physics_entity import PhysicsEntity
from scripts.entities.enemy import Enemy
from scripts.entities.player import Player
from scripts.tools import load_image, load_images, Animation
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle
from scripts.spark import Spark
from scripts import setup
from .biome_1 import Biome_1


class Level_1(Biome_1):
    def __init__(self):
        super().__init__()        
        self.level = 0 # Set starting level to 0
        self.map_id = 0            
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
        for rect, type in self.tilemap.physics_rects_near(self.player.pos): # rework probably gonna have to do collision in the level now
            if type == 'loading_zones':
                if self.player.rect().colliderect(rect):
                    self.done = True
                    self.next = 'level2'
                    self.exit = type
        
    def render(self, screen: pg.display):
        super().render(screen)