'''
can send any random thing through the event queue apparently 
from anywhere in pygame. so idk how to use that
maybe for player losing hp or idk

screenshake would be a really good example i think!!
####
Next
####
how to connect pathways like a hollow knight map (with robust naming scheme and loading, not just 0.json, as well as a nested state machine like each room inherits from the biome which inherits from base 'room' which inherits (just like menu) from state
consider a better name for each object

maybe rework file system to be more than just 0.png 1.png

Test maps for sandboxing abilities or monsters

save file
(maybe cool to have a 'total play time' that just goes up constantly when i play and
saves when i close it)
###
IMPORTANT TIDYING
###
make sure nothing is positioned between the low res tiles in its final position, the player can't see between those pixels so there could be half pixel inconsistancies
share player = Player() via abc, do not make self.player = Player() in each lvl
the chunks should probably be based on the largest enemy in the level?
    the chunks could also crop the colidable rects 
i think collision box detection should happen and update positions, then hitbox/hurtbox detection happens
####
Must be nice
####
arbitrary amount of collisionboxes on player. big one for interacting, smaller for physics, smallerer hurtbox

particles should be like little sparks (not his sparks) when you jump or land or wallslide (brown pallette sparkler app LOL)
Maybe it spits one out every half second instead of like a sprinkler

fix the naming of screen and display. display needs a better name. canvas? canvas!

frame advance
screenshots from anywhere

camera max and min distance each level

solids could have decor hanging off them, vines hanging from platforms

place camera scroll on player better between levels

probably want to use a 'touched the ground' cleanup cycle so i can make it so
walljumps give back the double jump and or (not) dash

middled middle tile of tileset (or any one really) could have random alterations that
occur at controlled random frequencies
####
Things to keep an eye on
####
once i have some levels, maybe i should zoom it out
'''
import sys

import pygame as pg 

from scripts import setup # pg.init right away!

from states import level_1, level_2, level_3, menu #### pg.init first!


class Control():
    def __init__(self, size=(1280, 720)):
        pg.display.set_caption("Hollow Box")
        self.screen = setup.SCREEN # What the player sees
        self.screen_rect = self.screen.get_rect()
        self.canvas = setup.CANVAS # What we draw on to blit to screen
        self.clock = pg.time.Clock()
        self.fps = 60
        self.keys = pg.key.get_pressed() #?
        self.done = False
        self.state_dict = {
            'level1': level_1.Level_1(),
            'level2': level_2.Level_2(),
            'level3': level_3.Level_3(),
            'menu': menu.Menu(),
        }
        self.state_name = 'menu'
        self.state = self.state_dict[self.state_name]
        
    def cleanup(self):
        print('cleaning up before closing the game...')
        
    def pass_event(self):
        for event in pg.event.get():
            self.state.process_event(event)

    def change_state(self):
        if self.state.done:
            self.done = False
            self.state.cleanup()
            previous, self.state_name = self.state_name, self.state.next
            self.state.done = False
            self.state.quit = False
            self.state = self.state_dict[self.state_name]
            self.state.previous = previous
            self.state.start()
        elif self.state.quit:
            self.state.cleanup()
            self.state.quicksave()
            
    def run(self):
        self.state.start() # 'enter' first state (for consistancy)
        while not self.done:
            if self.state.quit or self.state.done:
                self.done = True
            self.change_state()
            self.pass_event()
            self.state.update()
            self.canvas = self.state.render(self.canvas)
            
            pg.transform.scale(self.canvas, self.screen_rect.size, self.screen)
            pg.display.update()
            self.clock.tick(self.fps)
            setup.GAME_TICK += 1
        self.cleanup()
        

control = Control()
control.run()

pg.quit()
sys.exit()
