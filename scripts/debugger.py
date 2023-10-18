import pygame as pg

from scripts import setup

class _Debugger:
    def __init__(self):
        self.screen = setup.SCREEN
        self.infos = {}
        
        self.debugger_panel_offset = (5, setup.SCREEN_SIZE[1] // 2 - 40)
        self.font = pg.font.SysFont('Ariel', 20)
        
    def debug(self, key, info):
        self.infos[key] = self.font.render(str(info), True, (200, 200, 200),(0, 0, 0))
    
    def render(self):
        for i, info in enumerate(self.infos.values()):
            self.screen.blit(info, (self.debugger_panel_offset[0], self.debugger_panel_offset[1] + i * 30))
            
debugger = _Debugger()