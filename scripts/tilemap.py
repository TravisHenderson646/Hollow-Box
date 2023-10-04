'''
todo: make sepeterate editor tilemap module
'''

from math import floor
import json

import pygame as pg

from scripts import setup

NEIGHBOR_OFFSET = [(a, b) for a in [-2, -1, 0, 1, 2] for b in [-2, -1, 0, 1, 2]]
PHYSICS_TILES = {'grass', 'stone'}
    
class Tile:
    def __init__(self, type, variant, pos, image, is_interactable, is_drawn, flag, size=(32, 32)):
        self.type = type #maybe type should be group bc python type eh idc
        self.variant = variant
        self.pos = pos
        self.image = image
        self.is_interactable = is_interactable
        self.flag = flag
        self.is_drawn = is_drawn # i want to try self.is_drawn : bool # when i know im setting it later
        self.size = size
        self.bottom_right = (pos[0] + self.size[0], pos[1] + self.size[1])
        self.panels = ((0, 0), (0, 0)) # (top_left, bottom_right)
    
class Tilemap:
    def __init__(self, tile_size=32):
        self.tile_size = tile_size
        self.tilemap = {}
        self.tiles = []
        self.interactable_tiles = []
        self.drawn_tiles = []
        self.panels = (0, 0)
        self.chunks = (0, 0)
        
    def process_tile(self, tile):
        if tile['is_drawn']:
            image = setup.assets[tile['type']][tile['variant']]
            width = image.get_width()
            height = image.get_height()
        else:
            image = None
            width = 0
            height = 0
        tile['pos'] = tuple(tile['pos'])
        tile_instance = Tile(
            tile['type'], 
            tile['variant'],
            tile['pos'],
            image,
            tile['is_interactable'],
            tile['is_drawn'],
            tile['flag'],
            size=(width, height))
        self.tiles.append(tile_instance)
        if tile_instance.is_drawn:
            self.drawn_tiles.append(tile_instance)
        if tile_instance.is_interactable:
            self.interactable_tiles.append(tile_instance)
        
    def process_tilemap(self, path):
        file = open(path, 'r')
        map_data = json.load(file)
        file.close()
        
        ongrid_data = map_data['tilemap']
        offgrid_data = map_data['offgrid']
        
        
        for key, tile in ongrid_data.items(): # no key used should this just be a list as well?
            self.process_tile(tile)
        for tile in offgrid_data:
            self.process_tile(tile)
            
        panels = self.calculate_panels()
        
    def calculate_panels(self):
        panels = {}
        screen_width, screen_height = setup.DISPLAY.get_width(), setup.DISPLAY.get_height()
        max_left = min([tile.pos[0] for tile in self.drawn_tiles])
        max_right = max([tile.pos[0] + tile.size[0] for tile in self.drawn_tiles])
        max_top = min([tile.pos[1] for tile in self.drawn_tiles])
        max_bottom = max([tile.pos[1] + tile.size[1] for tile in self.drawn_tiles])
        map_width = max_right - max_left
        map_height = max_bottom - max_top
        
        # update tile positions
        map_offset = (max_left, max_top)
        for tile in self.tiles:
            tile.pos = (tile.pos[0] - map_offset[0], tile.pos[1] - map_offset[1])
            self.find_a_tiles_panels(tile)

        panels_required = (map_width // screen_width + 1, map_height // screen_height + 1)
        for y in range(panels_required[1]):
            for x in range(panels_required[0]):
                panels[(x, y)] = pg.Surface((screen_width, screen_height))
                current_panel = panels[(x, y)]
                panel_offset = (x * screen_width, y * screen_height)
                for tile in self.drawn_tiles:
                    current_panel.blit(tile.image, (tile.pos[0] - panel_offset[0], tile.pos[1] - panel_offset[1]))


    def find_a_tiles_panels(self, tile):
        screen_width, screen_height = setup.DISPLAY.get_width(), setup.DISPLAY.get_height()
        tl = (tile.pos[0] // screen_width, tile.pos[1] // screen_height)
        br = ((tile.bottom_right[0] // screen_width, tile.bottom_right[1] // screen_height))
        tile.panels = (tl, br)
    
    
    
    def extract(self, id_pairs, keep=False): #change name to give tiles
        matches = []
        for tile in self.offgrid_tiles.copy():
            if (tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                if not keep:
                    self.offgrid_tiles.remove(tile)
        # on grid tiles
        for loc in self.tilemap.copy():
            tile = self.tilemap[loc]
            if (tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                matches[-1]['pos'] = matches[-1]['pos'].copy()
                matches[-1]['pos'][0] *= self.tile_size
                matches[-1]['pos'][1] *= self.tile_size
                if not keep:
                    del self.tilemap[loc]
        return matches

    def tiles_near(self, pos):
        '''Takes a game position and returns a list of any adjacent tiles(dicts)'''
        tiles = []
        tile_loc = pg.Vector2((pos.x / self.tile_size), (pos.y / self.tile_size))
        for offset in NEIGHBOR_OFFSET: #offset really?
            check_loc = (str(floor(tile_loc.x + offset[0])) + ';' +  str(floor(tile_loc.y + offset[1])))
            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])
        return tiles
    
    def solid_check(self, pos):
        tile_loc = str(int(pos[0] // self.tile_size)) + ';' + str(int(pos[1] // self.tile_size))
        if tile_loc in self.tilemap:
            if self.tilemap[tile_loc]['type'] in PHYSICS_TILES:
                return self.tilemap[tile_loc]
    
    def physics_rects_near(self, pos):
        '''Takes a game position and returns a list of any adjacent tiles(Rects) in the physics tiles list'''
        rects = []
        for tile in self.tiles_near(pos):
            if tile['type'] in PHYSICS_TILES:
                rects.append((pg.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size), False))
            if tile['type'] == 'loading_zones':
                rects.append((pg.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size), 'loading_zones')) 

        return rects

    def render(self, surf, offset):
        '''Takes the display surface and screen scroll and renders the tilemap section'''
        #have to optimize offgrid tiles at some point probably once i have enough
        for tile in self.offgrid_tiles: #todo: dafluffy says this order but maybe its cooler to have offgrin in front THINK ABOUT IT
            surf.blit(setup.assets[tile['type']][tile['variant']], (floor(tile['pos'][0] - offset[0]), floor(tile['pos'][1] - offset[1])))

        for x in range(floor(offset[0] // self.tile_size), floor((offset[0] + surf.get_width()) // self.tile_size + 1)):
            for y in range(floor(offset[1] // self.tile_size), floor((offset[1] + surf.get_height()) // self.tile_size + 1)):
                loc = str(x) +';' + str(y)
                if loc in self.tilemap:
                    tile = self.tilemap[loc]
                    if True:#tile['type'] != 'loading_zones':
                        surf.blit(setup.assets[tile['type']][tile['variant']], (floor(tile['pos'][0]) * self.tile_size - offset[0], floor(tile['pos'][1]) * self.tile_size - offset[1]))
                    else:
                        pass          
                