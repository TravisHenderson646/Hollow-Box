import math
import random

import pygame as pg

from scripts.entities.player.attack import Attack
from scripts.spark import Spark
from scripts.setup import sfx

class Combat:
    def __init__(self, player):
        self.player = player
        self.hurtboxes = [player.rect]
        self.attack = Attack(player)
        self.dead = False
        self.frames_dead = 0
        self.death_duration = 120
        self.hit_by_spike = False
        self.ticks_since_got_hit = 500
        self.number_of_invuln_frames = 8 # should be 1 + (however long the player's attack is)
        self.got_hit_direction = 0 # 0right 1down 2left 3up
        self.invulnerable = False # todo this attr might be useless
        self.hp = 5
        self.damage = 1
        self.knockback_speed = 3
        self.knockback_direction = 1# left is -1
        self.got_hit_knockback_duration = 10
        self.in_got_hit = False
        self.got_hit_impulse = -1.6
        self.invulnerable_duration = 120
        
    def frame_start(self):
        if self.hp <= 0:
            self.dead = True
        self.invulnerable = False
        self.attack.active = False
        self.attack.ticks_since_last += 1
        self.ticks_since_got_hit += 1
        
    def attack_tiles(self, level):
        for tile in level.tilemap.current_attackable_tiles.copy():
            if tile.rect.collidelist(self.attack.hitbox_list[self.attack.active_hitboxes]) + 1:
                if tile.clanker:
                    self.attack.ticks_since_knockback = 0
                    self.attack.in_knockback = True
                if tile.breakable:
                    level.tilemap.current_attackable_tiles.remove(tile)
                    if tile in level.tilemap.current_solid_tiles:
                        level.tilemap.current_solid_tiles.remove(tile)
                    if tile in level.tilemap.current_rendered_tiles:
                        level.tilemap.current_rendered_tiles.remove(tile)
                    level.sparks.append(Spark((200,250,80), tile.rect.center, 1.5 + random.random(), self.attack.direction * math.pi/2 + random.random() * math.pi/4 - math.pi/8))
                    #if tile.name == 'decor': sfx flag.... etc
                    
    def attack_enemies(self, level):
        if self.attack.ticks_since_last < self.attack.duration:
            for enemy in level.enemies:
                if not enemy.combat.invulnerable:
                    for hurtbox in enemy.combat.hurtboxes:
                        if hurtbox.collidelist(self.attack.hitbox_list[self.attack.active_hitboxes]) + 1:
                            self.attack.ticks_since_knockback = 0
                            self.attack.in_knockback = True
                            self.invulnerable = False
                            enemy.combat.hp -= self.attack.damage
                            enemy.combat.ticks_since_got_hit = 0 # multi hit prevention from 1 attack
                            enemy.combat.got_hit_direction = self.attack.direction
                            enemy.combat.invulnerable = True
                            sfx['dash'].play()
    
    def enemies_attack(self, level):
        if not self.invulnerable:
            for enemy in level.enemies:
                for hitbox in enemy.combat.hitboxes:
                    if self.player.rect.colliderect(hitbox):
                        self.invulnerable = True
                        sfx['hit'].play()
                        self.player.jump.active = False
                        self.player.wallslide.active = False
                        self.player.dash.active = False
                        self.player.movement.collisions['down'] = False
                        self.hp -= enemy.combat.damage
                        self.player.movement.vel.y = self.got_hit_impulse
                        self.player.movement.air_time = self.player.jump.coyote_time + 1
                        self.ticks_since_got_hit = 0
                        if enemy.rect.centerx > self.player.rect.centerx:
                            self.knockback_direction = -1
                        else:
                            self.knockback_direction = 1  
        