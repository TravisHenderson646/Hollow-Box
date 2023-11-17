import math
import random

import pygame as pg

from scripts.debugger import debugger
from scripts import setup
from scripts.entities.player.player import Player
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.spark import Spark
from scripts.entities.geo import Geo
from scripts.entities.enemies.slug import Slug
from scripts.entities.gnat import Gnat
from scripts.entities.badguy import Badguy
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
        self.dialogue_boxes = []
        self.npcs = []
        self.pickups = []
        self.geo = []
        self.projectiles = []
            
        
    def cleanup(self):
        print(f'cleaning up lvl{self.map_id + 1}...')
        for npc in self.npcs:
            npc.dialogue.message = 0
            npc.dialogue.still_talking = False
            npc.dialogue.active = False
            npc.dialogue.message_completed = False
    
    def start(self):
        print("Entering a biome_1...")
        print(f'    Entering level {self.map_id + 1}...')

        Game.music.play('music.wav')
        self.enemies = []
        self.projectiles = []
        self.particles = []
        self.sparks = []
        self.geo = []
        
        self.tilemap.current_solid_tiles = self.tilemap.solid_tiles.copy()
        self.tilemap.current_attackable_tiles = self.tilemap.attackable_tiles.copy()
        self.tilemap.current_rendered_tiles = self.tilemap.rendered_tiles.copy()
        
        for tile in self.tilemap.enemies:
            #### todo todo todo todo todo todo todo todo todo todo
            # i could do something like simply, ....
            # wait
            # ok im thinking that actually there should be 3 or 4 lists like one is all the enemies
            # one is enemies that spawn on room entry one is enemies that spawn on bench sit
            # i can just make a copy of what's left of the room entry list here 
            # then refill the room entry list on bench sit
            if 'badguy' in tile.tags:
                self.enemies.append(Badguy(tile.rect.topleft))
            if 'slug' in tile.tags:
                self.enemies.append(Slug(tile.rect.topleft))
            if 'gnat' in tile.tags:
                self.enemies.append(Gnat(tile.rect.topleft))
        for enemy in self.enemies:
            pass
#            self.solid_entitiestest.append(enemy)
        
    def process_action(self, action):        
        super().process_action(action)
        if action == 'quit':
            self.quit = True
        elif action == 'start':
            self.done = True
            self.next = 'menu'
        elif action == 'rt':
            Biome_1.player.dash.ticks_since_input = 0
        elif action == 'a':
            Biome_1.player.jump.ticks_since_input = 0
            Biome_1.player.jump.held = True
        elif action == 'x':
            Biome_1.player.combat.attack.ticks_since_input = 0
        elif action == 'unrt':
            pass
        elif action == 'una':
            Biome_1.player.jump.held = False
        elif action == 'up':
            Biome_1.player.try_interact_flag = True
        elif action == 'r':
            Biome_1.player.jump.unlocked = not Biome_1.player.jump.unlocked
        elif action == 't':
            Biome_1.player.jump.double_unlocked = not Biome_1.player.jump.double_unlocked
        elif action == 'o':
            Biome_1.player.combat.attack.unlocked = not Biome_1.player.combat.attack.unlocked
        elif action == 'u':
            Biome_1.player.dash.unlocked = not Biome_1.player.dash.unlocked
        elif action == 'y':
            Biome_1.player.wallslide.unlocked = not Biome_1.player.wallslide.unlocked

    def player_attack_tiles(self):
        
        sfx_flag_spike = False
        sfx_flag_break = False # To prevent sfx stacking
        for tile in self.tilemap.current_attackable_tiles.copy():
            if tile.rect.collidelist(Biome_1.player.combat.attack.hitbox_list[Biome_1.player.combat.attack.active_hitboxes]) + 1:
                if tile.clanker:
                    Biome_1.player.combat.attack.ticks_since_knockback = 0
                    Biome_1.player.combat.attack.in_knockback = True
                if tile.breakable:
                    self.tilemap.current_attackable_tiles.remove(tile)
                    if tile in self.tilemap.current_solid_tiles:
                        self.tilemap.current_solid_tiles.remove(tile)
                    if tile in self.tilemap.current_rendered_tiles:
                        self.tilemap.current_rendered_tiles.remove(tile)
                    self.sparks.append(Spark((200,250,80), tile.rect.center, 1.5 + random.random(), Biome_1.player.combat.attack.direction * math.pi/2 + random.random() * math.pi/4 - math.pi/8))
                    #if tile.name == 'decor': sfx flag.... etc
        if sfx_flag_break: # todo: fix sfx flags
            setup.sfx['shoot'].play()
        if sfx_flag_spike:
            setup.sfx['dash'].play()

        
    def update(self): # Main loop
        for npc in self.npcs:
            npc.update(self.tilemap, Biome_1.player)
        Biome_1.player.try_interact_flag = False
        
        for enemy in self.enemies:
            if enemy.combat.dead:
                enemy.die( Biome_1.player, self.geo, self.enemies, self.sparks)
            else:
                enemy.update(self.tilemap, Biome_1.player)
             #   self.projectiles.extend(enemy.projectiles)
              #  enemy.projectiles = []
                    
        Biome_1.player.update(self.tilemap)

      #  self.tilemap.push_out_solid(Biome_1.player) # (note: after solids have moved)
        
        if Biome_1.player.combat.attack.active:
            self.player_attack_tiles()
                            
        for pickup in self.pickups:
            if pickup.dead:
                self.pickups.remove(pickup)
            else:
                pickup.update(self.tilemap, Biome_1.player)
                            
        for geo in self.geo:
            if geo.dead:
                self.geo.remove(geo)
            else:
                geo.update(self.tilemap, Biome_1.player)
            
        for projectile in self.projectiles:
            if projectile.dead:
                self.projectiles.remove(projectile)
            else:    
                projectile.update(self.tilemap)
            
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
                
        for dialogue_box in self.dialogue_boxes:
            if dialogue_box.active:
                dialogue_box.update()
                
        self.clouds.update()
                
    def render(self, canvas: pg.Surface):
        self.camera.update((round(Biome_1.player.rect.centerx), round(Biome_1.player.rect.centery)))
        canvas.fill((19, 178, 242))
        canvas.blit(setup.assets['background'], (0, 0))
        self.clouds.render(canvas, self.camera.rounded_pos)
        self.tilemap.render(canvas, self.camera.rounded_pos)
        for tile in self.tilemap.current_rendered_tiles:
            canvas.blit(tile.image, (tile.pos[0] - self.camera.rounded_pos[0], tile.pos[1] - self.camera.rounded_pos[1]))
        
        if not Biome_1.player.combat.dead > 25:
            Biome_1.player.render(canvas, self.camera.rounded_pos)
        
        for enemy in self.enemies:
            enemy.animate.render(canvas, self.camera.rounded_pos) # todo: should just give the enemy a render function that merely calls enemy.animate.render() just for consistancy
            
        for npc in self.npcs:
            npc.render(canvas, self.camera.rounded_pos)
        
        for projectile in self.projectiles:
            projectile.render(canvas, self.camera.rounded_pos)
    
        for particle in self.particles:
            particle.render(canvas, self.camera.rounded_pos)   
              
        for spark in self.sparks:
            spark.render(canvas, self.camera.rounded_pos) 
            
        for pickup in self.pickups:
            pickup.render(canvas, self.camera.rounded_pos)
        for geo in self.geo:
            geo.render(canvas, self.camera.rounded_pos)
            
        for dialogue_box in self.dialogue_boxes:
            if dialogue_box.active:
                dialogue_box.render(canvas, self.camera.rounded_pos) 
        
        # TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST 
  #      hot_chunk = ((Biome_1.player.rect.centerx + 30) // 60, (Biome_1.player.rect.centery + 30) // 60)
   #     for rect in self.tilemap.chunks.get((hot_chunk), {}):
     #       canvas.fill((150,0,0),(rect.x - self.camera.rounded_pos[0], rect.y - self.camera.rounded_pos[1], rect.w, rect.h))
        
# THIS IS HOW TO GET THE PLAYER NOT TO VIBRATE FROM CAMERA GLITCH IF AN EVEN OR ODD # OF PIXELS WIDE
#        canvas.fill((78,78,78),((math.floor(Biome_1.player.rect.centerx + 0.5) - self.camera.rounded_pos[0],math.floor(Biome_1.player.rect.centery + 0.5) - self.camera.rounded_pos[1],Biome_1.player.rect.width,Biome_1.player.rect.height)))
   #     canvas.fill((78,78,78),((Biome_1.player.rect.x - self.camera.rounded_pos[0],Biome_1.player.rect.y + 0.5 - self.camera.rounded_pos[1],Biome_1.player.rect.width,Biome_1.player.rect.height)))
        
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
