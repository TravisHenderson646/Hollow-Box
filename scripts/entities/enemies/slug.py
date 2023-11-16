import random
import math

import pygame as pg

from scripts.entities.components.combat import Combat
from scripts.entities.components.movement import Movement
from scripts.entities.components.animate import Animate
from scripts.spark import Spark
from scripts.entities.geo import Geo
from scripts import setup # could reduce todo

class Slug:
    def __init__(self, pos):
        self.name = 'slug'
        self.size = (14, 10)
        self.rect = pg.FRect(*pos, *self.size)
        self.movement = Movement(self)
        self.movement.movement.x = -1
        self.movement.speed = 0.3
        self.animate = Animate(self)
        self.combat = Combat(self)
        
    def die(self, player, geo_list, enemies_list, sparks_list):
        if self.combat.frames_dead == 0:
            self.combat.death_angle = player.attack.direction * math.pi/2 + random.random() * math.pi/4 - math.pi/8
            setup.sfx['hit'].play()
            sparks_list.append(Spark((200,70,120), self.rect.center, 1.5 + random.random(), player.attack.direction * math.pi/2 + random.random() * math.pi/4 - math.pi/8))
        if self.combat.frames_dead >= self.combat.death_duration:
            enemies_list.remove(self)
        else:
            if self.combat.geo > 0:
                if not self.combat.frames_dead % 5:
                    self.combat.geo -= 1
                    geo_list.append(Geo(self.rect.center, -1 if player.flip else 1))
            else:    
                self.rect.x += math.cos(self.combat.death_angle) * self.combat.death_speed
                self.rect.y += math.sin(self.combat.death_angle) * self.combat.death_speed
            self.combat.frames_dead += 1
                
        
    def update(self, tilemap, player):
        self.combat.frame_start()
        self.movement.frame_start()
        
        self.combat.hit_by_player(player)
        self.combat.hit_player(player)
        
        self.movement.turn_around_at_ledge(tilemap)
        self.movement.bonk()
        
        self.movement.calculate_frame_movement()
        self.movement.collide_with_tilemap(tilemap)

        self.animate.animation.tick() 
        
    def render(self, canvas:pg.Surface, offset):
        self.animate.render(canvas, offset)