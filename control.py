'''
####
Critical
####
FIRST STEPS:
write code schematic for each 'section' of the code insofar as you can reduce the logic to sensible sections
Make the hitboxes playable with debugging

***rewrite the code so that it has exactly the "Perfect game loop" from pygame tidbits repo on github
it is perfect

RESTRUCTURE ALL OF CODE LIKE THE PONG EXAMPLE ON MY GITHUB????

####
Next
####
how to connect pathways like a hollow knight map (with robust naming scheme and loading, not just 0.json, as well as a nested state machine like each room inherits from the biome which inherits from base 'room' which inherits (just like menu) from state
consider a better name for each object
remake tileset. make it simpler like a neon line that connects around the outside

Test maps for sandboxing abilities or monsters
####
Must be nice
####
camera: add a minimum speed

each tile should be Tile class?
entities rects to frects

particles should be like little sparks (not his sparks) when you jump or land or wallslide (brown pallette sparkler app LOL)
Maybe it spits one out every half second instead of like a sprinkler

frame advance
screenshots from anywhere
closing the game should do some cleanup

probably want to use a 'touched the ground' cleanup cycle so i can make it so
walljumps give back the double jump and or (not) dash

implement delta time if movement or animations get choppy? idk
use set_timer and custom USER_EVENTS for every cooldown in the game?

maybe tools should be a folder

could have like GAME = 'game' instead of having state['game'] show up
'''
import os
import sys

import pygame as pg 

from scripts import setup # pg.init right away!

from states import level1, level2, menu #### pg.init first!


class Control():
    def __init__(self, size=(960, 720)):
        pg.display.set_caption("Hollow Box")
        self.screensize = (int(size[0]), int(size[1]))
        self.screen = setup.SCREEN # What the player sees
        self.display = pg.Surface((320,240), pg.SRCALPHA) # What we draw on to blit to screen
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.fps = 60
        self.keys = pg.key.get_pressed() #?
        self.done = False
        self.state_dict = {
            'level1': level1.Level_1(),
            'level2': level2.Level_2(),
            'menu': menu.Menu(),
        }
        self.state_name = 'menu'
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
        elif self.state.quit:
            self.done = True
            self.state.cleanup()
            
    def run(self):
        while not self.done:
            if self.state.quit or self.state.done:
                self.done = True
            now = pg.time.get_ticks()
            self.event_loop()
            self.change_state()
            self.state.update(now, self.keys)
            self.state.render(self.screen)
            pg.display.update()
            self.clock.tick(self.fps)

control = Control()
control.run()

pg.quit()
sys.exit()