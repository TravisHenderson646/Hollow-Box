import pygame as pg

from scripts import setup
from scripts.tilemap import Tilemap
from scripts.entities.npcs.signpost import Signpost
from scripts.entities.npcs.frog import Frog
from scripts.story import signpost1_text, signpost2_text
from states.biome_1 import Biome_1
from scripts.jump_unlock import JumpUnlock
from scripts.double_jump_unlock import DoubleJumpUnlock
from scripts.dash_unlock import DashUnlock 
from scripts.attack_unlock import AttackUnlock
from scripts.wallslide_unlock import WallslideUnlock


class Level_1(Biome_1):
    def __init__(self):
        super().__init__()        
        self.level = 0 # Set starting level to 0
        self.map_id = 0
        self.tilemap = Tilemap(tile_size=8) # Create an instance of the Tilemap class
        self.tilemap.process_tilemap('data/maps/' + str(self.map_id) + '.json')
        self.enemies = []
        for tile in self.tilemap.npcs:
            if 'frog' in tile.tags:
                self.npcs.append(Frog(tile.rect.topleft))
            if 'signpost' in tile.tags:
                self.npcs.append(Signpost(tile.rect.topleft, signpost1_text))
            if 'signpost2' in tile.tags:
                self.npcs.append(Signpost(tile.rect.topleft, signpost2_text))
        for tile in self.tilemap.pickups:
            if 'jump' in tile.tags:
                self.pickups.append(JumpUnlock(tile.rect.topleft))
            if 'double_jump' in tile.tags:
                self.pickups.append(DoubleJumpUnlock(tile.rect.topleft))
            if 'dash' in tile.tags:
                self.pickups.append(DashUnlock(tile.rect.topleft))
            if 'attack' in tile.tags:
                self.pickups.append(AttackUnlock(tile.rect.topleft))
            if 'wallslide' in tile.tags:
                self.pickups.append(WallslideUnlock(tile.rect.topleft))
        for npc in self.npcs:
            self.dialogue_boxes.append(npc.dialogue)
        for pickup in self.pickups:
            self.dialogue_boxes.append(pickup.text)
    
    def start(self):
        super().start()
        if self.previous == 'menu': 
            for tile in self.tilemap.entrances:
                if 'start' in tile.tags: # todo this should be start
                    Biome_1.player.hurtboxes[0].topleft = tile.rect.topleft
        if self.previous == 'level2': # if you came from level 2
            for tile in self.tilemap.entrances:
                if 'east' in tile.tags: # find the tile for level 2
                    Biome_1.player.hurtboxes[0].topleft = tile.rect.topleft

        
    def process_action(self, action):
        super().process_action(action)
        if action == 'p':
                self.done = True
                self.next = 'level2'

    def update(self):
        super().update()
        for tile in self.tilemap.exits:
            if tile.rect.colliderect(Biome_1.player.hurtboxes[0]):
                if 'east' in tile.tags:
                    self.done = True
                    self.next = 'level2'
        
    def render(self, canvas: pg.Surface):
        canvas = super().render(canvas)
   #     canvas.fill((200, 120, 170), pg.Rect(Biome_1.player.pos.x - self.camera.rounded_pos[0], Biome_1.player.pos.y - self.camera.rounded_pos[1], 7,13))
    
        return canvas