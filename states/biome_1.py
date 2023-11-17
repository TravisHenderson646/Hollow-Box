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
        
            #### todo todo todo todo todo todo todo todo todo todo
            # i could do something like simply, ....
            # wait
            # ok im thinking that actually there should be 3 or 4 lists like one is all the enemies
            # one is enemies that spawn on room entry one is enemies that spawn on bench sit
            # i can just make a copy of what's left of the room entry list here 
            # then refill the room entry list on bench sit
        for tile in self.tilemap.enemies:
            if 'badguy' in tile.tags:
                self.enemies.append(Badguy(tile.rect.topleft))
            if 'slug' in tile.tags:
                self.enemies.append(Slug(tile.rect.topleft))
            if 'gnat' in tile.tags:
                self.enemies.append(Gnat(tile.rect.topleft))
        
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
                    
        Biome_1.player.update(self)
                            
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
        hot_chunk = ((Biome_1.player.rect.centerx + 30) // 60, (Biome_1.player.rect.centery + 30) // 60)
        for rect in self.tilemap.chunks.get((hot_chunk), {}):
            canvas.fill((150,0,0),(rect.x - self.camera.rounded_pos[0], rect.y - self.camera.rounded_pos[1], rect.w, rect.h))
        
# THIS IS HOW TO GET THE PLAYER NOT TO VIBRATE FROM CAMERA GLITCH IF AN EVEN OR ODD # OF PIXELS WIDE
#        canvas.fill((78,78,78),((math.floor(Biome_1.player.rect.centerx + 0.5) - self.camera.rounded_pos[0],math.floor(Biome_1.player.rect.centery + 0.5) - self.camera.rounded_pos[1],Biome_1.player.rect.width,Biome_1.player.rect.height)))
   #     canvas.fill((78,78,78),((Biome_1.player.rect.x - self.camera.rounded_pos[0],Biome_1.player.rect.y + 0.5 - self.camera.rounded_pos[1],Biome_1.player.rect.width,Biome_1.player.rect.height)))
        
        return canvas

