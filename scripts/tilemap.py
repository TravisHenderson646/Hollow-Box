'''
todo: make sepeterate editor tilemap module
'''

from math import floor
import json

import pygame as pg

from scripts import setup

NEIGHBOR_OFFSET = [(a, b) for a in [-2, -1, 0, 1, 2] for b in [-2, -1, 0, 1, 2]]
PHYSICS_TILES = {'grass', 'stone'}

class Tilemap:
    def __init__(self, tile_size=32):
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []
        
    def load(self, path):
        file = open(path, 'r')
        map_data = json.load(file)
        file.close()
        
        self.tilemap = map_data['tilemap']
        self.tile_size = map_data['tile_size']
        self.offgrid_tiles = map_data['offgrid']

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
                    
                    
                    