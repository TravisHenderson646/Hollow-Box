import math
import random

import pygame as pg

from scripts.debugger import debugger
from scripts import setup
from scripts.entities.player import Player
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.spark import Spark
from scripts.entities.crawlid import Crawlid
from scripts.camera import Camera
from states.game import Game

class Biome_1(Game):            
    # The ONLY player instance
    player = Player((200, 350), (setup.PLAYER_COLLISION_SIZE[0], setup.PLAYER_COLLISION_SIZE[1]))

    def __init__(self):
        super().__init__()
        self.camera = Camera()
        self.biome = "Biome_1"
        self.clouds = Clouds(setup.assets['clouds'], count=16)
        self.tilemap:Tilemap
        self.solid_entities = [Biome_1.player] 
        self.previous = 'menu'
        self.map_id = 0
        self.enemies = 0
        self.sparks = []
        
    def cleanup(self):
        print(f'cleaning up lvl{self.map_id + 1}...')
    
    def start(self):
        print("Entering a biome_1...")
        print(f'    Entering level {self.map_id + 1}...')

        Game.music.play('music.wav')
        keys = pg.key.get_pressed()
        self.player.movement = [keys[pg.K_a], keys[pg.K_d], keys[pg.K_w], keys[pg.K_s]]
        self.enemies = []
        self.projectiles = []
        self.particles = []
        self.sparks = []
        
        # todo maybe i could call these just self.breakable_tiles and put it in the level not tilemap
        self.tilemap.current_breakable_tiles = self.tilemap.breakable_tiles.copy()
        self.tilemap.current_rendered_tiles = self.tilemap.rendered_tiles.copy()
        
        for tile in self.tilemap.enemies:
            if 'crawlid' in tile.tags:
                self.enemies.append(Crawlid(tile.rect.topleft))
        self.enemies.append(Crawlid((100, -50)))
        for enemy in self.enemies:
            self.solid_entities.append(enemy)
        
    def process_action(self, action):        
        super().process_action(action)
        if action == 'quit':
            self.quit = True
        elif action == 'start':
            self.done = True
            self.next = 'menu'
        elif action == 'left':
            self.player.movement[0] = True
        elif action == 'right':
            self.player.movement[1] = True
        elif action == 'up':
            self.player.movement[2] = True
        elif action == 'down':
            self.player.movement[3] = True
        elif action == 'rt':
            Biome_1.player.dash.ticks_since_input = 0
        elif action == 'lt':
            self.player.lt = True
        elif action == 'a':
            Biome_1.player.jump.ticks_since_input = 0
            Biome_1.player.jump.held = True
        elif action == 'x':
            Biome_1.player.attack.ticks_since_input = 0
        elif action == 'unleft':
            self.player.movement[0] = False
        elif action == 'unright':
            self.player.movement[1] = False
        elif action == 'unup':
            self.player.movement[2] = False
        elif action == 'undown':
            self.player.movement[3] = False
        elif action == 'unrt':
            pass
        elif action == 'unlt':
            self.player.lt = False
        elif action == 'una':
            Biome_1.player.jump.held = False
        elif action == 'stop':
            self.player.movement[0] = False
            self.player.movement[1] = False
        elif action == 'neutral':
            self.player.movement[2] = False
            self.player.movement[3] = False        

            
    def attack_collision(self):
        sfx_flag_break = False # To prevent sfx stacking
        Biome_1.player.attack.update()
        for tile in self.tilemap.current_breakable_tiles.copy():
            if Biome_1.player.attack.hitbox_list[Biome_1.player.attack.active_hitbox].colliderect(tile.rect):
                self.tilemap.current_breakable_tiles.remove(tile)
                self.tilemap.current_rendered_tiles.remove(tile)
                Biome_1.player.attack.ticks_since_knockback = 0
                self.sparks.append(Spark((200,250,80), tile.rect.center, 1.5 + random.random(), Biome_1.player.attack.direction * math.pi/2 + random.random() * math.pi/4 - math.pi/8))
                sfx_flag_break = True
        if sfx_flag_break:
            setup.sfx['shoot'].play()
        for enemy in self.enemies.copy():
            if Biome_1.player.attack.hitbox_list[Biome_1.player.attack.active_hitbox].colliderect(enemy.rect):
                if not enemy.invulnerable:
                    Biome_1.player.attack.ticks_since_knockback = 0
                    enemy.hp -= self.player.attack.damage
                    enemy.ticks_since_got_hit = 0 # multi hit prevention from 1 attack
                    enemy.got_hit_direction = Biome_1.player.attack.direction
                    #self.enemies.remove(enemy)
                    #self.sparks.append(Spark((200,250,80), enemy.rect.center, 1.5 + random.random(), Biome_1.player.attack.direction * math.pi/2 + random.random() * math.pi/4 - math.pi/8))
                    setup.sfx['dash'].play()
            
    def got_hit_collision(self):
        for enemy in self.enemies:
            if Biome_1.player.rect.colliderect(enemy.rect):
                Biome_1.player.got_hit(enemy)
        
    def update(self): # Main loop
        Biome_1.player.update(self.tilemap)
            
        for enemy in self.enemies:
            if not enemy.dead:
                enemy.update(self.tilemap)
            else:
                self.enemies.remove(enemy)
                setup.sfx['hit'].play()
                self.sparks.append(Spark((200,250,80), enemy.rect.center, 1.5 + random.random(), Biome_1.player.attack.direction * math.pi/2 + random.random() * math.pi/4 - math.pi/8))


        for entity in self.solid_entities:
            self.tilemap.push_out_solid(entity) # (note: after solids have moved)
        
        if Biome_1.player.attack.ticks_since_last < Biome_1.player.attack.duration:
            self.attack_collision()

        if not Biome_1.player.invulnerable:
            self.got_hit_collision()
            
        for particle in self.particles.copy():
            kill = particle.update()
            if kill:
                self.particles.remove(particle)
            else: # this just makes the leaves move wavy southwest idk its bad
                particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3    
                    
        for spark in self.sparks.copy():
            kill = spark.update()
            if kill:
                self.sparks.remove(spark)
                
        self.clouds.update()
                
    def render(self, canvas: pg.Surface):
        self.camera.update((round(self.player.rect.centerx), round(self.player.rect.centery)))
        canvas.blit(setup.assets['background'], (0, 0))
        self.clouds.render(canvas, self.camera.rounded_pos)
        self.tilemap.render(canvas, self.camera.rounded_pos)
        for tile in self.tilemap.current_rendered_tiles:
            canvas.blit(tile.image, (tile.pos[0] - self.camera.rounded_pos[0], tile.pos[1] - self.camera.rounded_pos[1]))
        
        for projectile in self.projectiles.copy():
            img = setup.assets['projectile']
            canvas.blit(img, (projectile[0][0] - img.get_width() / 2 - self.camera.rounded_pos[0], projectile[0][1] - img.get_height() / 2 - self.camera.rounded_pos[1])) 
        
        if not Biome_1.player.dead > 25:
            Biome_1.player.render(canvas, self.camera.rounded_pos)
        
        for enemy in self.enemies:
            enemy.render(canvas, self.camera.rounded_pos)
    
        for particle in self.particles:
            particle.render(canvas, self.camera.rounded_pos)   
              
        for spark in self.sparks:
            spark.render(canvas, self.camera.rounded_pos)   
        
        # TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST 
 #       hot_chunk = (round((Biome_1.player.rect.x + 60/2) / 60), round((Biome_1.player.rect.y + 60/2) / 60))
  #      for rect in self.tilemap.chunks.get(hot_chunk, {}):
   #         canvas.fill((150,0,0),(rect.x - self.camera.rounded_pos[0], rect.y - self.camera.rounded_pos[1], rect.w, rect.h))
        
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