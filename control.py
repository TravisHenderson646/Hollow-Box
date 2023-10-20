'''
####
IDEAS
####
its fun for now but i dont think im going to want the pogo to reset everything, its too centralizing late game
peach float
landing could reset attack cooldown
wall climb like celest w button cling but can attack
maybe a crouch? crouch also grabs walls? crouch jump is a roll
floating hurtboxes to pogo

slime jumping enemy

can send any random thing through the event queue apparently 
from anywhere in pygame. so idk how to use that
screenshake would be a really good example i think!!

you have to fight a bouncing boss to get the jump? like 2nd room?

if the player attacks an enemy the player loses any invulerability frames
###
FIRST LEVEL
###
first room you enter with sword put breakable blocks that you need to get up an immediate ledge, if they break them they can reset asap and learn that mechanic
###
IMPORTANT TIDYING
###
make sure nothing is positioned between the low res tiles in its final position, the player can't see between those pixels so there could be half pixel inconsistancies
the chunks should probably be based on the largest enemy in the level?
    the chunks could also crop the colidable rects 
i think collision box detection should happen and updatedddda dwd as, then hitbox/hurtbox detection happens
####
Must be nice
####
arbitrary amount of collisionboxes on player. big one for interacting, smaller for physics, smallerer hurtbox
    bonus: extrabig keep_talking box to let player keep movement while talking

npc to talk to
first make readable signpost
    
particles should be like little sparks (not his sparks) when you jump or land or wallslide (brown pallette sparkler app LOL)
Maybe it spits one out every half second instead of like a sprinkler

frame advance

camera max and min distance each level

solids could have decor hanging off them, vines hanging from platforms

place camera scroll on player better between levels

probably want to use a 'touched the ground' cleanup cycle so i can make it so
walljumps give back the double jump and or (not) dash
####
Things to keep an eye on
####
Could have 3 chunk dicts for each map, one for small, big, boss size collisions (rn i just have bigish)

if the parallax background looks wack (when you make one) try making sure the depths are 1/2, 1/4, 1/8 etc so that they shift at the same time

it wouldn't be that hard to implement chunking for sword attack collisions. This would enable making every piece of scenery breakable
'''
import sys

import pygame as pg 

from scripts import setup # pg.init right away!

from states import level_1, level_2, level_3, menu #### pg.init first!
from scripts.debugger import debugger


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
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_m:
                    setup.joysticks = False
            if event.type == pg.KEYUP:
                if event.key == 1073741894: # print screen button, triggers both on release idk why
                    pg.image.save(self.canvas, 'art/screenshots/screenshot.png')
            action = setup.process_event(event)
            self.state.process_action(action)

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
            debugger.render()
            pg.display.update()
            self.clock.tick(self.fps)
            setup.GAME_TICK += 1
        self.cleanup()
        

control = Control()
control.run()

pg.quit()
sys.exit()
