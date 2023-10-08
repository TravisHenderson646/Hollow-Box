import pygame as pg

from states.state import State


class Menu(State):
    def __init__(self):
        super().__init__()
        self.next = 'level1'
        self.previous : str
        
    def cleanup(self):
        print('cleaning up Menu state stuff...')
        
    def start(self):
        print('starting Menu state stuff...')
        State.music.play('music2.ogg')
        
    def process_event(self, event):
        if event.type == pg.QUIT:
            self.quit = True
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.quit = True
            else:
                self.done = True
                
    def update(self):
        pass
    
    def render(self, canvas):
        canvas.fill((150,60,90))
        return canvas
  