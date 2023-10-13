import math
import random

import pygame as pg

from scripts.entities.player import Player
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.spark import Spark
from scripts import setup
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
        self.camera_buffer = 0
        self.sparks = []
        
    def cleanup(self):
        print(f'cleaning up lvl{self.map_id + 1}...')
    
    def start(self):
        print("Entering a biome_1...")
        print(f'    Entering level {self.map_id + 1}...')

        Game.music.play('music.wav')
                
        self.projectiles = []
        self.particles = []
        self.sparks = []
        self.dead = Biome_1.player.dead
        keys = pg.key.get_pressed()
        self.player.movement = [keys[pg.K_a], keys[pg.K_d], keys[pg.K_w], keys[pg.K_s]]
        
    def process_event(self, event):        
        super().process_event(event)
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.done = True
                self.next = 'menu'
            if event.key == pg.K_a:
                self.player.movement[0] = True
            if event.key == pg.K_d:
                self.player.movement[1] = True
            if event.key == pg.K_w:
                self.player.movement[2] = True
            if event.key == pg.K_s:
                self.player.movement[3] = True
            if event.key == pg.K_SPACE:
                Biome_1.player.ticks_since_jump_input = 0
            if event.key == pg.K_j:
                Biome_1.player.ticks_since_attack_input = 0
        if event.type == pg.KEYUP:
            if event.key == pg.K_a:
                self.player.movement[0] = False
            if event.key == pg.K_d:
                self.player.movement[1] = False
            if event.key == pg.K_w:
                self.player.movement[2] = False
            if event.key == pg.K_s:
                self.player.movement[3] = False
            if event.key == pg.K_SPACE:
                Biome_1.player.holding_jump = False

        
    def push_out_solid(self, entity):
        entity.collisions = {'up': False, 'down': False, 'left': False, 'right': False}
        frame_movement = ( # (x, y)
            (entity.movement[1] - entity.movement[0]) * entity.speed + entity.vel.x,
            entity.vel.y)
            #(entity.movement[3] - entity.movement[2]) * entity.speed + entity.vel.y,)
        
        entity_width = entity.rect.width
        entity_height = entity.rect.height
        center_node = (round((entity.rect.x + entity_width/2) / entity_width), round((entity.rect.y + entity_height/2) / entity_height))
        
        entity.rect.x += frame_movement[0]
        for rect in self.tilemap.chunks.get(center_node, {}):
            if entity.rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity.rect.right = rect.left
                    entity.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity.rect.left = rect.right
                    entity.collisions['left'] = True
                    
        for rect in [tile.rect for tile in self.tilemap.breakable_tiles]:
            if entity.rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity.rect.right = rect.left
                    entity.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity.rect.left = rect.right
                    entity.collisions['left'] = True
                    
        entity.rect.y += frame_movement[1]
        for rect in self.tilemap.chunks.get(center_node, {}):
            if entity.rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity.rect.bottom = rect.top
                    entity.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity.rect.top = rect.bottom
                    entity.collisions['up'] = True 
                    
        for rect in [tile.rect for tile in self.tilemap.breakable_tiles]:
            if entity.rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity.rect.bottom = rect.top
                    entity.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity.rect.top = rect.bottom
                    entity.collisions['up'] = True 
                    
        if entity.collisions['down'] or entity.collisions['up']:
            entity.vel = pg.Vector2(0, 0)
   
    def update(self): # Main loop
        self.clouds.update()
        
        Biome_1.player.vel.x = 0
        if not Biome_1.player.dead:
            Biome_1.player.update(self.particles)

        for entity in self.solid_entities:
            self.push_out_solid(entity) # (note: after solids have moved)
        
        
        if Biome_1.player.ticks_since_last_attack < Biome_1.player.attack_duration:
            sfx_flag = False # To prevent sfx stacking
            Biome_1.player.place_attack()
            for tile in self.tilemap.breakable_tiles.copy():
                if Biome_1.player.attack_hitbox_list[Biome_1.player.active_hitbox].colliderect(tile.rect):
                    self.tilemap.breakable_tiles.remove(tile)
                    self.tilemap.rendered_tiles.remove(tile)
                    Biome_1.player.ticks_since_attack_knockback = 0
                    self.sparks.append(Spark((200,250,80), tile.rect.center, 1.5 + random.random(), Biome_1.player.attack_direction * math.pi/2 + random.random() * math.pi/4 - math.pi/8))
                    sfx_flag = True
            if sfx_flag:
                setup.sfx['shoot'].play()
            
        for particle in self.particles.copy():
            kill = particle.update()
            if kill:
                self.particles.remove(particle)
            else:
                particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3    
                    
        for spark in self.sparks.copy():
            kill = spark.update()
            if kill:
                self.sparks.remove(spark)
                
    def render(self, canvas: pg.Surface):
        
        canvas.blit(setup.assets['background'], (0, 0))
        self.clouds.render(canvas, self.camera.rounded_pos)
        self.tilemap.render(canvas, self.camera.rounded_pos)
        for tile in self.tilemap.rendered_tiles:
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
     #   center_node = (round((Biome_1.player.pos.x + 7/2) / 7), round((Biome_1.player.pos.y + 13/2) / 13))
      #  for rect in self.tilemap.chunks.get(center_node, {}):
       #     canvas.fill((150,0,0),(rect.x - self.camera.rounded_pos[0], rect.y - self.camera.rounded_pos[1], rect.w, rect.h))
        
        self.camera.update(self.player.rect.center)
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