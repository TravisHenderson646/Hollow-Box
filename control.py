
import os
import sys

import pygame as pg
import game

class Control():
    def __init__(self, size=(960, 720)):
        pg.mixer.pre_init(44100, -16, 1, 512)
        pg.init()
        pg.display.set_caption("Hollow Box")
        self.screensize = (int(size[0]), int(size[1]))
        self.screen = pg.display.set_mode((960, 720)) # What the player sees
        self.display = pg.Surface((320,240), pg.SRCALPHA) # What we draw on to blit to screen
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.fps = 60
        self.keys = pg.key.get_pressed() #?
        self.done = False
        self.state_dict = {
            'game': game.Game(),
        }
        self.state_name = 'game'
        self.state = self.state_dict[self.state_name]
        

    def event_loop(self):
        for event in pg.event.get():
            if event.type in (pg.KEYDOWN,pg.KEYUP):
                self.keys = pg.key.get_pressed()
            self.state.get_event(event, self.keys)

    def change_state(self):
        if self.state.done:
            self.state.cleanup()
            self.state_name = self.state.next
            self.state.done = False
            self.state.quit = False
            self.state = self.state_dict[self.state_name]
            self.state.entry()
        if self.state.quit:
            self.state.cleanup()
            

    def run(self):
        while not self.done:
            if self.state.quit or self.state.done:
                self.done = True
            now = pg.time.get_ticks() #?
            self.event_loop()
            print(self.state.done)
            self.change_state()
            print(self.state.done)
            self.state.update(now, self.keys)
            self.state.render(self.screen)
            pg.display.update()
            self.clock.tick(self.fps)

control = Control()
control.run()

pg.quit()
sys.exit()