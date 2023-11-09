from math import floor
import json

import pygame as pg

from scripts import setup
from scripts.entities.slug import Slug
from scripts.entities.gnat import Gnat
from scripts.entities.badguy import Badguy

NEIGHBOR_OFFSET = [(a, b) for a in [-2, -1, 0, 1, 2] for b in [-2, -1, 0, 1, 2]]
PHYSICS_TILES = {'grass', 'stone'}
    
class Tile:
    def __init__(self, set, variant, pos, image, tags, size=(8, 8)):
        self.name = ''
        self.set = set
        self.variant = variant
        self.pos = pos
        self.image = image
        self.tags = tags
        self.size = size
        self.bottom_right = (pos[0] + self.size[0], pos[1] + self.size[1])
        self.panels = ((0, 0), (0, 0)) # (top_left, bottom_right)
        self.rect = pg.Rect(0, 0, 0, 0)
        self.rendered = False
        self.solid = False
        self.breakable = False
        self.clanker = False
        self.north = False
        self.south = False
        self.east = False
        self.west = False
        self.active = False
        self.used = False
    
class Tilemap:
    def __init__(self, tile_size=32):
        self.tile_size = tile_size
        self.tilemap = {}
        self.tiles = []
        self.enemies = []
        self.npcs = []
        self.chunked_tiles = []
        self.painted_tiles = []
        self.rendered_tiles = []
        self.current_rendered_tiles = []
        self.current_attackable_tiles = []
        self.attackable_tiles = []
        self.solid_tiles = []
        self.interactable_tiles = []
        self.pickups = []
        
        self.panels = {}
        self.chunks = {}
        self.exits = []
        self.entrances = []
        self.map_width = 0
        self.map_height = 0
        
    def process_tile(self, tile):
        if tile['type'] in ['spawners', 'spawns', 'enemies', 'unlocks', 'npcs']:
            image = pg.Surface((0, 0))
            width = 0
            height = 0
        else:
            image = setup.assets[tile['type']][tile['variant']]
            width = image.get_width()
            height = image.get_height()
            
        tile['pos'] = tuple(tile['pos'])
        
        tile_instance = Tile(
            tile['type'], 
            tile['variant'],
            tile['pos'],
            image,
            tile['tags'],
            size=(width, height))
        self.tiles.append(tile_instance)
        
        if 'painted' in tile_instance.tags:
            self.painted_tiles.append(tile_instance)
        if 'chunked' in tile_instance.tags:
            self.chunked_tiles.append(tile_instance)
        if 'rendered' in tile_instance.tags:
            self.rendered_tiles.append(tile_instance)
        if 'solid' in tile_instance.tags:
            self.solid_tiles.append(tile_instance)
        if 'interactable' in tile_instance.tags:
            self.interactable_tiles.append(tile_instance) # ok so i could do like i make a function and then i say 'if 'geode' in tags: interact equals a function like give geo
        if 'npc' in tile_instance.tags:
            self.npcs.append(tile_instance)
        if 'unlock' in tile_instance.tags:
            self.pickups.append(tile_instance)
        if 'enemy' in tile_instance.tags:
            self.enemies.append(tile_instance)
        if 'entrance' in tile_instance.tags:
            self.entrances.append(tile_instance)
        if 'exit' in tile_instance.tags:
            self.exits.append(tile_instance)
        if 'north' in tile_instance.tags:
            tile_instance.north = True
        if 'south' in tile_instance.tags:
            tile_instance.south = True
        if 'east' in tile_instance.tags:
            tile_instance.east = True
        if 'west' in tile_instance.tags:
            tile_instance.west = True
        if 'spike' in tile_instance.tags:
            tile_instance.name = 'spike'
        if 'decor' in tile_instance.tags:
            tile_instance.name = 'decor'
        if 'dirt' in tile_instance.tags:
            tile_instance.name = 'dirt'
        if 'breakable' in tile_instance.tags:
            self.attackable_tiles.append(tile_instance) # this is important 
            tile_instance.breakable = True
        if 'clanker' in tile_instance.tags:
            self.attackable_tiles.append(tile_instance) # this is important
            tile_instance.clanker = True
        
    def process_tilemap(self, path):
        with open(path, 'r') as file:
            map_data = json.load(file)
        
        ongrid_data = map_data['tilemap']
        offgrid_data = map_data['offgrid']
        
        # process EVERY Tile
        for key, tile in ongrid_data.items(): # no key used should this just be a list as well?
            self.process_tile(tile)
        for tile in offgrid_data:
            self.process_tile(tile)
        
        self.calculate_map_dimensions()
        self.calculate_panels()
        self.calculate_chunks()

    def calculate_map_dimensions(self):
        max_left = min([tile.pos[0] for tile in self.painted_tiles])
        max_right = max([tile.pos[0] + tile.size[0] for tile in self.tiles])
        max_top = min([tile.pos[1] for tile in self.painted_tiles])
        max_bottom = max([tile.pos[1] + tile.size[1] for tile in self.tiles])
        self.map_width = max_right - max_left
        self.map_height = max_bottom - max_top
        
        # update ALL tile positions
        map_offset = (max_left, max_top)
        for tile in self.tiles.copy():
            tile.pos = (tile.pos[0] - map_offset[0], tile.pos[1] - map_offset[1])
            tile.rect = pg.Rect(tile.pos[0], tile.pos[1], tile.image.get_width(), tile.image.get_height())     

    def calculate_chunks(self):
        chunk_width, chunk_height = setup.CHUNK_SIZE[0], setup.CHUNK_SIZE[1]
        chunks_required = (self.map_width // chunk_width + 1 + 2, self.map_height // chunk_height + 1 + 2) # +2 for padding
        
        for y in range(chunks_required[1]):
            for x in range(chunks_required[0]):
                self.chunks[(x - 1, y - 1)] = []
                current_chunk = self.chunks.get((x - 1, y - 1), {})
                chunk_topleft = ((x - 1) * chunk_width, (y - 1) * chunk_height)
                chunk_test_rect = pg.Rect(chunk_topleft[0] - (chunk_width * 1.5), chunk_topleft[1]-(chunk_height*1.5), chunk_width * 3, chunk_height* 3) # make a test rect 3x the chunk

                for tile in self.chunked_tiles:
                    if tile.rect.colliderect(chunk_test_rect):
                        current_chunk.append(tile.rect)      
    
    def collide_x(self, entity, rect):
        if entity.frame_movement[0] > 0:
            entity.hurtboxes[0].right = rect.left
            entity.collisions['right'] = True
        if entity.frame_movement[0] < 0:
            entity.hurtboxes[0].left = rect.right
            entity.collisions['left'] = True
        
    def collide_y(self, entity, rect):
        if entity.frame_movement[1] > 0:
            entity.hurtboxes[0].bottom = rect.top
            entity.collisions['down'] = True
        if entity.frame_movement[1] < 0:
            entity.hurtboxes[0].top = rect.bottom
            entity.collisions['up'] = True 
                          
    def push_out_solid(self, entity):
        entity.collisions = {'up': False, 'down': False, 'left': False, 'right': False}
        
        entity.hurtboxes[0].x += entity.frame_movement[0]
        
        # chunk tiles
        for rect in self.chunks.get(entity.hot_chunk, {}):
            if entity.hurtboxes[0].colliderect(rect):
                self.collide_x(entity, rect)
        # special solid tiles
        for tile in self.current_solid_tiles:
            if entity.hurtboxes[0].colliderect(tile.rect):
                self.collide_x(entity, tile.rect)
                if tile.name == 'spike':
                    entity.hit_by_spike = True
                    
        entity.hurtboxes[0].y += entity.frame_movement[1]
        
        # chunk tiles
        for rect in self.chunks.get(entity.hot_chunk, {}):
            if entity.hurtboxes[0].colliderect(rect):
                self.collide_y(entity, rect)
        # special solid tiles
        for tile in self.current_solid_tiles:
            if entity.hurtboxes[0].colliderect(tile.rect):
                self.collide_y(entity, tile.rect)
                if tile.name == 'spike':
                    entity.hit_by_spike = True
                
    def check_point(self, pos, chunk):
        for rect in self.chunks.get(chunk, {}):
            if rect.collidepoint(pos[0], pos[1]):
                return True
        for rect in [tile.rect for tile in self.current_solid_tiles]:
            if rect.collidepoint(pos[0], pos[1]):
                return True
        return False    
                
    def check_wallslide(self, player):
        if player.wallslide.direction == -1:
        
            top_check = (player.hurtboxes[0].left - 3, player.hurtboxes[0].top)
            bottom_check = (player.hurtboxes[0].left - 3, player.hurtboxes[0].bottom)
        
            for rect in self.chunks.get(player.hot_chunk, {}):
                if rect.collidepoint(top_check[0], top_check[1]):
                    return True
                if rect.collidepoint(bottom_check[0], bottom_check[1]):
                    return True
            for tile in self.current_solid_tiles:
                if tile.rect.collidepoint(top_check[0], top_check[1]):
                    if tile.name == 'spike':
                        #return False
                        player.hit_by_spike = True
                    return True
                if tile.rect.collidepoint(bottom_check[0], bottom_check[1]):
                    if tile.name == 'spike':
                        #return False
                        player.hit_by_spike = True
                    return True
        if player.wallslide.direction == 1:
            top_check = (player.hurtboxes[0].right + 3, player.hurtboxes[0].top)
            bottom_check = (player.hurtboxes[0].right + 3, player.hurtboxes[0].bottom)
            for rect in self.chunks.get(player.hot_chunk, {}):
                if rect.collidepoint(top_check[0], top_check[1]):
                    return True
                if rect.collidepoint(bottom_check[0], bottom_check[1]):
                    return True
            for tile in self.current_solid_tiles:
                if tile.rect.collidepoint(top_check[0], top_check[1]):
                    if tile.name == 'spike':
                        #return False
                        player.hit_by_spike = True
                    return True
                if tile.rect.collidepoint(bottom_check[0], bottom_check[1]):
                    if tile.name == 'spike':
                        #return False
                        player.hit_by_spike = True
                    return True
        return False

    def calculate_panels(self):
        screen_width, screen_height = setup.CANVAS.get_width(), setup.CANVAS.get_height()
        panels_required = (self.map_width // screen_width + 1, self.map_height // screen_height + 1)
        for y in range(panels_required[1]):
            for x in range(panels_required[0]):
                self.panels[(x, y)] = pg.Surface((screen_width, screen_height))
                current_panel = self.panels[(x, y)]
                panel_offset = (x * screen_width, y * screen_height)
                for tile in self.painted_tiles:
                    current_panel.blit(tile.image, (tile.pos[0] - panel_offset[0], tile.pos[1] - panel_offset[1]))
                current_panel.set_colorkey((0, 0, 0))

    def render(self, canvas, offset):
        '''Takes the display surface and screen scroll and renders the relevant tilemap panels'''
        disp_width = canvas.get_width()
        disp_height = canvas.get_height()
        center_node = (round((offset[0] + disp_width/2) / disp_width), round((offset[1] + disp_height/2) / disp_height))
        hot_panels = (
            (center_node[0] - 1, center_node[1] - 1),
            (center_node[0]    , center_node[1] - 1),
            (center_node[0] - 1, center_node[1]    ),
            (center_node[0]    , center_node[1]    ),)
    #    for key, panel in [(hot_panel_pos ,self.panels[hot_panel_pos]) for hot_panel_pos in hot_panels if (hot_panel_pos[0] >= 0 and hot_panel_pos[1] >= 0)]: # the most beautiful list comprehension i have ever devised
        for panel_pos in hot_panels:
            if panel_pos[0] >= 0 and panel_pos[1] >= 0:
                panel = self.panels.get(panel_pos, pg.Surface((0, 0)))
                canvas.blit(panel, (panel_pos[0] * disp_width - offset[0], panel_pos[1] * disp_height - offset[1]))
