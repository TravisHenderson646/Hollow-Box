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


#could inherit from a dummy state class for now, or even a dummy level state which inherits from state
# a biome instance should never be created (abstract base class)
class Biome_1:    
    def __init__(self):
        self.movement = [False, False] # [left, right] - Tracks whether the player is inputting left or right
        
        self.display = setup.DISPLAY # What we draw on to blit to screen

        self.clouds = Clouds(setup.assets['clouds'], count=16) # Create an instance of the Clouds class
        self.player = Player((50, 50), (setup.PLAYER_COLLISION_SIZE[0], setup.PLAYER_COLLISION_SIZE[1])) # Create an instance of the Player class. Perhaps this should be a class attribute so that it isn't a new player instance for each level
        self.tilemap : Tilemap
        self.movement = [False, False, False, False] # [left, right] - Tracks whether the player is inputting left or right 
        self.solid_entities = [self.player] # start a list of the solid entities in the level
        
        self.screenshake = 0
        # todo: camera should probably be a class
        self.scroll = pg.Vector2(0, 0) # Initial camera position
        self.rounded_scroll = pg.Vector2(0, 0) # Rounded fix for camera scroll rendering
        
        self.done = False
        self.quit = False
        self.next = None
        self.exit = None # exit shouldn't be done! instead have every entrance be its own class
        self.map_id = 0
        
    def cleanup(self):
        print(f'cleaning up lvl{self.map_id + 1}...')
        self.movement = [False, False, False, False]
        pg.mixer.music.stop()
    
    def entry(self):
        print("Entering a biome_1...")
        print(f'    Entering level {self.map_id + 1}...')
        pg.mixer.music.load('data/music.wav')
        pg.mixer.music.set_volume(0.5)
        pg.mixer.music.play(-1)     
            
   #     self.leaf_spawners = []
    #    for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
     #       self.leaf_spawners.append(pg.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))
        
  #      self.enemies = [] 
   #     for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]): #### MUST BE OFFGRID TILES
    #        if spawner['variant'] == 0:
     #           self.player.pos = pg.Vector2(spawner['pos'])
      #          self.player.air_time = 0
       #     else:
        #        self.enemies.append(Enemy(spawner['pos'], (8, 15)))
                
        self.projectiles = []
        self.particles = []
        self.sparks = []
        self.dead = self.player.dead
        self.transition = -30
    ###          
    
    def reset(self):
                
        self.projectiles = []
        self.particles = []
        self.sparks = []
        
        self.player.dead = 0
        self.transition = -30 


        
    def process_event(self, event):        
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
            if event.key == pg.K_w:
                self.movement[2] = True
            if event.key == pg.K_s:
                self.movement[3] = True
            if event.key == pg.K_SPACE:
                self.player.jump()
            if event.key == pg.K_j:
                self.player.dash()
        if event.type == pg.KEYUP:
            if event.key == pg.K_a:
                self.movement[0] = False
            if event.key == pg.K_d:
                self.movement[1] = False
            if event.key == pg.K_w:
                self.movement[2] = False
            if event.key == pg.K_s:
                self.movement[3] = False
        ###
   
    def update(self): # Main loop
        self.screenshake = max(0, self.screenshake - 1)
        
        ### If you're dead increment a timer and reload the level eventually
        if self.player.dead > 0:
            self.player.dead += 1 #timer
            if self.player.dead <= 50:
                self.transition = min(30, self.transition + 1) #hack soln to screen transition
            if self.player.dead > 80:
                self.reset()
        ###
        
        ### Update camera position
        self.scroll.x += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll.x) / 60
        self.scroll.y += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll.y) / 60
        self.rounded_scroll.x = math.floor(self.scroll.x)
        self.rounded_scroll.y = math.floor(self.scroll.y)
        ###
        
        ### Maybe spawn leafs
    #    for rect in self.leaf_spawners:
     #       if random.random() * 49999 < rect.width * rect.height: # this is a ridiculous control
      #          pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
       #         self.particles.append(Particle('leaf', pos, vel=[-0.1, 0.3], frame=random.randint(0, 20)))
        ###
                
        self.clouds.update()
        
        ### Update enemies
 #       for enemy in self.enemies.copy():
  #          kill = enemy.update(self.tilemap, self.player.rect(), self.player.dashing, self.projectiles, self.sparks, self.particles, movement=(0, 0))
   #         if kill:
    #            self.enemies.remove(enemy)
        ###
    
        ### Update player
        if not self.player.dead:
            self.player.update(None, (self.movement[1] - self.movement[0], self.movement[3] - self.movement[2]))
        ###
        
        ### Solids collide with map (note: after solids have moved)
        for entity in self.solid_entities:
            self.tilemap.push_out_solids(entity)

        
        ### Update enemy projectiles
        for projectile in self.projectiles.copy():  # [[x, y], direction, despawn timer] SHOULD PROBABLY BE A CLASS
            projectile[2] += 1
            projectile[0][0] += projectile[1]
            if self.tilemap.solid_check(projectile[0]):
                self.projectiles.remove(projectile)
                for i in range(4):
                    self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random()))
            elif projectile[2] > 300: # projectile times out for cleanup
                self.projectiles.remove(projectile)
            elif abs(self.player.dashing) < 50: # hit player if not invincible from dashing (player should have invincible attribute)
                if self.player.rect().collidepoint(projectile[0]):
                    self.player.dead += 1 # should def just have a is dead variable idk todo
                    setup.sfx['hit'].play()
                    self.screenshake = max(45, self.screenshake) # max so this line wont overwrite a larger screen shake
                    self.projectiles.remove(projectile)
                    for i in range(30):
                        angle = random.random() * math.pi * 2
                        speed = random.random() * 5
                        self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                        self.particles.append(Particle('particle', self.player.rect().center, vel=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
        ###
        
        ### Update particles
        for particle in self.particles.copy():
            kill = particle.update()
            if kill:
                self.particles.remove(particle)
            else:
                particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
        ###
    
    def render(self, screen: pg.display):
        self.display.blit(setup.assets['background'], (0, 0))
        
        self.clouds.render(self.display, offset=self.rounded_scroll)
        
        self.tilemap.render(self.display, self.rounded_scroll, self.player.rect())
        
        for projectile in self.projectiles.copy():
            img = setup.assets['projectile']
            self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - self.rounded_scroll[0], projectile[0][1] - img.get_height() / 2 - self.rounded_scroll[1])) 
        
        if not self.player.dead > 25:
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