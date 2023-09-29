import os
import sys
import math
import random

import pygame as pg

from scripts.entities import Player, Enemy
from scripts.tools import load_image, load_images, Animation
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle
from scripts.spark import Spark


class Game:
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

        self.clouds = Clouds(self.assets['clouds'], count=16) # Create an instance of the Clouds class
        
        self.player = Player(self, (50, 50), (32, 27)) # Create an instance of the Player class
        
        self.tilemap = Tilemap(self, tile_size=16) # Create an instance of the Tilemap class
        
        self.level = 0 # Set starting level to 0
        self.load_level(self.level) # Load starting level
        
        self.screenshake = 0
        
        ### Make this a state
        self.done = False
        self.quit = False
        self.next = None # will have to export the levels to other classes for this transitiion i think

        
    def get_event(self, event, keys):        
        ### User input
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.done = True
                self.next = 'menu'  
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
        
    def cleanup(self):
        print('cleaning up!')
        pg.mixer.music.stop()
    
    def entry(self):
        print('entering!')
        pg.mixer.music.load('data/music.wav')
        pg.mixer.music.set_volume(0.5)
        pg.mixer.music.play(-1)
        
        self.sfx['ambience'].play(-1)
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

    def update(self, now, keys): # Main game loop
        self.screenshake = max(0, self.screenshake - 1)
        

        
        ### If you're dead increment a timer and reload the level eventually
        if self.dead > 0:
            self.dead += 1 #timer
            if self.dead <= 50:
                self.transition = min(30, self.transition + 1) #hack soln to screen transition
            if self.dead > 80:
                self.load_level(self.level)
        ###
        
        ### Update camera position
        self.scroll.x += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll.x) / 60
        self.scroll.y += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll.y) / 60
        self.rounded_scroll.x = math.floor(self.scroll.x)
        self.rounded_scroll.y = math.floor(self.scroll.y)
        ###
        
        ### Maybe spawn leafs
        for rect in self.leaf_spawners:
            if random.random() * 49999 < rect.width * rect.height: # this is a ridiculous control
                pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                self.particles.append(Particle(self, 'leaf', pos, vel=[-0.1, 0.3], frame=random.randint(0, 20)))
        ###
                
        self.clouds.update()
        
        ### Update enemies
        for enemy in self.enemies.copy():
            kill = enemy.update(self.tilemap, (0, 0))
            if kill:
                self.enemies.remove(enemy)
        ### Update player
        if not self.dead:
            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
        ###
        
        ####### projectile logic needs encapsulated so render is not tied in to update logic
        ### Update enemy projectiles, render
        for projectile in self.projectiles.copy():  # [[x, y], direction, despawn timer] SHOULD PROBABLY BE A CLASS
            projectile[2] += 1
            projectile[0][0] += projectile[1]
            img = self.assets['projectile']
            self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - self.rounded_scroll[0], projectile[0][1] - img.get_height() / 2 - self.rounded_scroll[1])) # blitting here is crazy
            if self.tilemap.solid_check(projectile[0]):
                self.projectiles.remove(projectile)
                for i in range(4):
                    self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random()))
            elif projectile[2] > 300: # projectile times out for cleanup
                self.projectiles.remove(projectile)
            elif abs(self.player.dashing) < 50: # hit player if not invincible from dashing (player should have invincible attribute)
                if self.player.rect().collidepoint(projectile[0]):
                    self.dead += 1
                    self.sfx['hit'].play()
                    self.screenshake = max(45, self.screenshake) # max so this line wont overwrite a larger screen shake
                    self.projectiles.remove(projectile)
                    for i in range(30):
                        angle = random.random() * math.pi * 2
                        speed = random.random() * 5
                        self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                        self.particles.append(Particle(self, 'particle', self.player.rect().center, vel=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
        ###
        

        ### Update particles, render
        for particle in self.particles.copy():
            kill = particle.update()
            if kill:
                self.particles.remove(particle)
            else:
                particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
        ###

    
    def load_level(self, map_id):
        self.tilemap.load('data/maps/' + str(map_id) + '.json')
        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pg.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))
        
        self.enemies = [] 
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
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