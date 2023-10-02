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


class Level_2(Biome_1):
    def __init__(self):
        super().__init__()
        self.level = 1

        self.map_id = 0
    
    def entry(self, test):
        super().entry()

        # todo: camera should probably be a class
        self.scroll = pg.Vector2(200, 100) # Initial camera position
        self.rounded_scroll = pg.Vector2(200, 100) # Rounded fix for camera scroll rendering
    
    def reset(self):
        super().reset()
        self.scroll = pg.Vector2(200, 100) # Initial camera position
        self.rounded_scroll = pg.Vector2(200, 100) # Rounded fix for camera scroll rendering
        
    def get_event(self, event, keys):  
        super().get_event(event, keys)
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_p: #for testing
                self.done = True
                self.next = 'level1'

    def update(self, now, keys):
        super().update(now, keys)
        
    def render(self, screen: pg.display):
        super().render(screen)