import pygame as pg


class Menu():
    def __init__(self):
        self.done = False
        self.quit = False
        self.exit = None
        self.next = 'level1'
    def cleanup(self):
        print('cleaning up Menu state stuff')
    def entry(self): #could be called cleanup
        print('starting Menu state stuff')
    def get_event(self, event, keys):
        if event.type == pg.QUIT:
            self.quit = True
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.quit = True
            else:
                self.done = True
    def update(self, now, keys):
        pass
    def render(self, screen):
        screen.fill((150,60,90))
  