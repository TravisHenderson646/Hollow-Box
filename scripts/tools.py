import os
import math
import random

import pygame as pg

from .entities import Enemy, Player

BASE_IMG_PATH = 'data/images/'

def load_image(path):
    img = pg.image.load(BASE_IMG_PATH + path).convert()
    img.set_colorkey((0, 0, 0))
    return img

def load_images(path):
    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)): # for file_name in a list of the dir contents
        images.append(load_image(path + '/' + img_name))
    return images

class Animation:
    def __init__(self, images, image_dur=5, loop=True):
        self.images = images
        self.loop = loop
        self.image_dur = image_dur # larger dur is slower
        
        self.done = False
        self.frame = 0
        
    # Each entity makes a copy of the animation
    def copy(self):
        return Animation(self.images, self.image_dur, self.loop)
    
    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (self.image_dur * len(self.images))
        else:
            self.frame = min(self.frame + 1, self.image_dur * len(self.images) - 1)
            if self.frame >= self.image_dur * len(self.images) - 1:
                self.done = True
    
    def img(self):
        return self.images[int(self.frame / self.image_dur)]
    
#could inherit from a dummy state class for now, or even a dummy level state which inherits from state
class Biome_1:    
    def __init__(self):
        self.movement = [False, False] # [left, right] - Tracks whether the player is inputting left or right
        
        self.display = pg.Surface((320,240), pg.SRCALPHA) # What we draw on to blit to screen
              
        self.assets = { # dict of every sprite's image or animation's set of images
            'decor' : load_images('tiles/decor'),
            'grass' : load_images('tiles/grass'),
            'large_decor' : load_images('tiles/large_decor'),
            'stone' : load_images('tiles/stone'),
            'player' : load_image('entities/player.png'),
            'background' : load_image('background.png'),
            'clouds' : load_images('clouds'),
            'enemy/idle': Animation(load_images('entities/enemy/idle'), 12),
            'enemy/run': Animation(load_images('entities/enemy/run'), 8),
            'player/idle' : Animation(load_images('entities/player/idle'), image_dur=12),
            'player/run' : Animation(load_images('entities/player/run'), image_dur=8),
            'player/jump' : Animation(load_images('entities/player/jump'), image_dur=5,),
            'player/slide' : Animation(load_images('entities/player/slide'), image_dur=5,),
            'player/wallslide' : Animation(load_images('entities/player/wallslide'), image_dur=5,),
            'particle/leaf': Animation(load_images('particles/leaf'), 20, False),
            'particle/particle': Animation(load_images('particles/particle'), 6, False),
            'gun': load_image('gun.png'),
            'projectile': load_image('projectile.png'),
        }
            
        self.sfx = { # dict of every sound effect
            'jump': pg.mixer.Sound('data/sfx/jump.wav'),
            'dash': pg.mixer.Sound('data/sfx/hit.wav'),
            'hit': pg.mixer.Sound('data/sfx/dash.wav'),
            'shoot': pg.mixer.Sound('data/sfx/shoot.wav'),
            'ambience': pg.mixer.Sound('data/sfx/ambience.wav'),
        }
  
        # manually setting individual volumes
        self.sfx['jump'].set_volume(0.2)
        self.sfx['dash'].set_volume(0.2)
        self.sfx['hit'].set_volume(0.4)
        self.sfx['shoot'].set_volume(0.3)
        self.sfx['ambience'].set_volume(0.7)
        
        self.screenshake = 0
        
        self.done = False
        self.quit = False
        self.next = None
        self.map_id = 0
        
    def cleanup(self):
        print(f'cleaning up lvl{self.map_id}!') #maybe try self.__name__()
        pg.mixer.music.stop()
    
    def entry(self):
        print('entering level1!')
        pg.mixer.music.load('data/music.wav')
        pg.mixer.music.set_volume(0.5)
        pg.mixer.music.play(-1)
        
        self.sfx['ambience'].play(-1)
        
        self.tilemap.load('data/maps/' + str(self.map_id) + '.json')
        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pg.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))
        
        self.enemies = [] 
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]): #### MUST BE OFFGRID TILES
            if spawner['variant'] == 0:
                self.player.pos = pg.Vector2(spawner['pos'])
                self.player.air_time = 0
            else:
                self.enemies.append(Enemy(self, spawner['pos'], (8, 15)))
        
                
        self.projectiles = []
        self.particles = []
        self.sparks = []
        
        # todo: camera should probably be a class
        self.scroll = pg.Vector2(-500, 200) # Initial camera position
        self.rounded_scroll = pg.Vector2(-500, 200) # Rounded fix for camera scroll rendering
        
        self.dead = 0
        self.transition = -30
    ###          
    
    def reset(self):
        self.tilemap.load('data/maps/' + str(self.map_id) + '.json')
        self.enemies = [] 
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]): #### MUST BE OFFGRID TILES
            if spawner['variant'] == 0:
                self.player.pos = pg.Vector2(spawner['pos'])
                self.player.air_time = 0
            else:
                self.enemies.append(Enemy(self, spawner['pos'], (8, 15)))
                
        self.projectiles = []
        self.particles = []
        self.sparks = []
        
        # todo: camera should probably be a class
        self.scroll = pg.Vector2(-500, 200) # Initial camera position
        self.rounded_scroll = pg.Vector2(-500, 200) # Rounded fix for camera scroll rendering
        
        self.dead = 0
        self.transition = -30
    ###          


        
    def get_event(self, event, keys):        
        ### User input
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.done = True
                self.next = 'menu'
            if event.key == pg.K_p: #for testing
                self.done = True
                self.next = 'level2'
            if event.key == pg.K_a:
                self.movement[0] = True
            if event.key == pg.K_d:
                self.movement[1] = True
            if event.key == pg.K_SPACE:
                self.player.jump()
            if event.key == pg.K_j:
                self.player.dash()
        if event.type == pg.KEYUP:
            if event.key == pg.K_a:
                self.movement[0] = False
            if event.key == pg.K_d:
                self.movement[1] = False
        ###

    
    def render(self, screen: pg.display):
        
        self.display.blit(self.assets['background'], (0, 0))
        
        self.clouds.render(self.display, offset=self.rounded_scroll)
        
        self.tilemap.render(self.display, offset=self.rounded_scroll)
        
        if not self.dead:
            self.player.render(self.display, offset=self.rounded_scroll)
        
        ### Update sparks, render
        for spark in self.sparks.copy():
            kill = spark.update()
            spark.render(self.display, offset=self.rounded_scroll)
            if kill:
                self.sparks.remove(spark)
        ###
        
        for enemy in self.enemies:
            enemy.render(self.display, offset=self.rounded_scroll)
    
    
        for particle in self.particles:
            particle.render(self.display, offset=self.rounded_scroll)
            
     #  self.display.blit(self.player.test_surf, (self.player.test_pos - self.rounded_scroll))
        
        screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)
        screen.blit(pg.transform.scale(self.display, screen.get_size()), screenshake_offset)
