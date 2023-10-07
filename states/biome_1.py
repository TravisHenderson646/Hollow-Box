import math
import random

import pygame as pg

from scripts.entities.player import Player
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle
from scripts.spark import Spark
from scripts import setup


#could inherit from a dummy state class for now, or even a dummy level state which inherits from state
# a biome instance should never be created (abstract base class)
class Biome_1:    
    def __init__(self):
        self.movement = [False, False, False, False] # [left, right] - Tracks whether the player is inputting left or right
        self.clouds = Clouds(setup.assets['clouds'], count=16) # Create an instance of the Clouds class
        self.player = Player((0, -50), (setup.PLAYER_COLLISION_SIZE[0], setup.PLAYER_COLLISION_SIZE[1])) # Create an instance of the Player class. Perhaps this should be a class attribute so that it isn't a new player instance for each level
        self.tilemap : Tilemap
        self.movement = [False, False, False, False] # [left, right] - Tracks whether the player is inputting left or right 
        self.solid_entities = [self.player] # start a list of the solid entities in the level

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
        ### Update camera position
        self.scroll.x += (self.player.rect().centerx - setup.CANVAS_SIZE[0] / 2 - self.scroll.x) / 60
        self.scroll.y += (self.player.rect().centery - setup.CANVAS_SIZE[1]  / 2 - self.scroll.y) / 60
        self.rounded_scroll.x = math.floor(self.scroll.x)
        self.rounded_scroll.y = math.floor(self.scroll.y)
        ###
        
        self.clouds.update()

        ### Update player
        if not self.player.dead:
            self.player.update(None, (self.movement[1] - self.movement[0], self.movement[3] - self.movement[2]))
        ###

        ### Solids collide with map (note: after solids have moved)
        for entity in self.solid_entities:
            self.push_out_solids(entity)

        ### Update particles
        for particle in self.particles.copy():
            kill = particle.update()
            if kill:
                self.particles.remove(particle)
            else:
                particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
        ###

        
    def push_out_solids(self, entity):
        entity.collisions = {'up': False, 'down': False, 'left': False, 'right': False}
 #       frame_movement = pg.Vector2(entity.movement[0] + entity.vel.x, entity.movement[1] + entity.vel.x)
        frame_movement = ( # (x, y)
            (self.movement[1] - self.movement[0]) + entity.vel.x,
            (self.movement[3] - self.movement[2]) + entity.vel.y,)
        
        entity_width = entity.rect().width
        entity_height = entity.rect().height
        center_node = (round((entity.pos.x + entity_width/2) / entity_width), round((entity.pos.y + entity_height/2) / entity_height))
      #  center_node = (round((self.player.pos.x + 24/2) / 24), round((self.player.pos.y + 25/2) / 25))

        hot_chunks = (
            (center_node[0] - 1, center_node[1] - 1),
            (center_node[0]    , center_node[1] - 1),
            (center_node[0] - 1, center_node[1]    ),
            (center_node[0]    , center_node[1]    ),)
        
        entity.pos.x += frame_movement[0]
        entity_rect = entity.rect()
        print('-----------------------------------------------------')
        for rect in self.tilemap.chunks.get(center_node, {}):
            print(rect)
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    entity.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    entity.collisions['left'] = True
                entity.pos.x = entity_rect.x
                    
        entity.pos.y += frame_movement[1]
        entity_rect = entity.rect()
        for rect in self.tilemap.chunks.get(center_node, {}):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    entity.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    entity.collisions['up'] = True
                    print('collided up')
                entity.pos.y = entity_rect.y                
        if entity.collisions['down'] or entity.collisions['up']:
            entity.vel = pg.Vector2()

    
    def render(self, canvas: pg.Surface):
        canvas.blit(setup.assets['background'], (0, 0))
        
        self.clouds.render(canvas, self.rounded_scroll)
        
        self.tilemap.render(canvas, self.rounded_scroll, self.player.rect())
        
        for projectile in self.projectiles.copy():
            img = setup.assets['projectile']
            canvas.blit(img, (projectile[0][0] - img.get_width() / 2 - self.rounded_scroll[0], projectile[0][1] - img.get_height() / 2 - self.rounded_scroll[1])) 
        
        if not self.player.dead > 25:
            self.player.render(canvas, self.rounded_scroll)
        
        ### Update sparks, render
        for spark in self.sparks.copy():
            kill = spark.update()
            spark.render(canvas, self.rounded_scroll)
            if kill:
                self.sparks.remove(spark)
        ###
        
        for enemy in self.enemies:
            enemy.render(canvas, self.rounded_scroll)
    
    
        for particle in self.particles:
            particle.render(canvas, self.rounded_scroll)        
    
    
        center_node = (round((self.player.pos.x + 24/2) / 24), round((self.player.pos.y + 25/2) / 25))
    #    canvas.fill((150,0,0),(center_node[0],center_node[1],10,10))
        for rect in self.tilemap.chunks.get(center_node, {}):
            canvas.fill((150,0,0),(rect.x - self.rounded_scroll[0], rect.y - self.rounded_scroll[1], rect.w, rect.h))
        hot_chunks = (
            (center_node[0] - 1, center_node[1] - 1),
            (center_node[0]    , center_node[1] - 1),
            (center_node[0] - 1, center_node[1]    ),
            (center_node[0]    , center_node[1]    ),)
        
        for chunkpos in hot_chunks:
            chunk = self.tilemap.chunks.get(chunkpos, {})
            for rect in chunk:
                canvas.fill((150,50,50), (rect.x * canvas.get_width() - self.rounded_scroll[0], rect.y * canvas.get_height() - self.rounded_scroll[1], rect.w, rect.h))
            
        
        return canvas
    
    
    
'''    CODE GRAVEYARD
            
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
                    self.projectiles.remove(projectile)
                    for i in range(30):
                        angle = random.random() * math.pi * 2
                        speed = random.random() * 5
                        self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                        self.particles.append(Particle('particle', self.player.rect().center, vel=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
        ###
        ### Update enemies
 #       for enemy in self.enemies.copy():
  #          kill = enemy.update(self.tilemap, self.player.rect(), self.player.dashing, self.projectiles, self.sparks, self.particles, movement=(0, 0))
   #         if kill:
    #            self.enemies.remove(enemy)
        ###
        ### Maybe spawn leafs
    #    for rect in self.leaf_spawners:
     #       if random.random() * 49999 < rect.width * rect.height: # this is a ridiculous control
      #          pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
       #         self.particles.append(Particle('leaf', pos, vel=[-0.1, 0.3], frame=random.randint(0, 20)))
        ###
              
        ### If you're dead increment a timer and reload the level eventually
        if self.player.dead > 0:
            self.player.dead += 1 #timer
            if self.player.dead <= 50:
                self.transition = min(30, self.transition + 1) #hack soln to screen transition
            if self.player.dead > 80:
                self.reset()
        ###
'''