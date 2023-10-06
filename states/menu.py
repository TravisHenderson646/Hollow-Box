import pygame as pg



class Menu():
    def __init__(self):
        self.done = False
        self.quit = False
        self.exit = None
        self.next = 'level1'
    def cleanup(self):
        print('cleaning up Menu state stuff...')
    def entry(self, test): #could be called cleanup
        print('starting Menu state stuff...')
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
  