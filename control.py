'''
####
IDEAS
#### 
could have 3 TODO lists.
    1 things to code for when im focused
    2 things to create for when im energized
    3 things that r biolerplate for wen im ded
    
decor should be called clutter

i think it would be cool if each enemy only dropped geo once, then there could be a 100% geo amount!

attack is like a upward jab with a stinger

The game goes dingdong like in graveyard keeper when they drop off a body but it's like 3 minutes after you kill a boss except it's pretending like it happened organically
d
its fun for now but i dont think im going to want the pogo to reset everything, its too centralizing late game
peach float
landing could reset attack cooldown
wall climb like celest w cling but can attack
maybe a crouch? crouch also grabs walls? crouch jump is a roll
floating hurtboxes to pogo

can send any random thing through the event queue apparently 
from anywhere in pygame. so idk how to use that
screenshake would be a really good example i think!!

camera: any level could have multiple idle cameras that replace the main camera temporarily when a cutscene starts

if the player damages an enemy the player loses any invulerability frames

breakables take more than 1 hit

attacks clank other attacks
attacks redirect projectiles

heavy slow big flying enemy that has momentum and bounces 

player should face someone theyre talking to, within a range maybe

dream nail could be reduced to a badge where enemies say a chat when pwned

enemies get hurt on spikes
you dont collect geo you break it open, ie lore so that geo gets auto picked up on lava/ spikes instead of it being unreachable

checkpoint that locks in hp so you can choose to retraverse and try to get there with more hp or not

boss tosses out 3 holes, they land randomly like hornet 2's spikes, then a wyrm goes between them a la ESA

theres a button that does a unique thing in each biome. in the graveyard it puts down a lantern

vehicles could create different playable characters like gato roboto

moving platforms, (could stop moving down if something bonks from below so they dont glitch up through)

ng+ is remixed ng++ is randomizer
####
ENEMIES
####
jumping slime
jazzball just bouncing around
####
FIRST LEVEL
####
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! first room ACTUALLY 
sword to the left breakable wall to the right, you can't jump.

first room you enter with sword put breakable blocks that you need to get up an immediate ledge, if they break them they can reset asap and learn that mechanic
####
IMPORTANT TIDYING
####
make sure nothing is positioned between the low res tiles in its final position, the player can't see between those pixels so there could be half pixel inconsistancies
the chunks should probably be based on the largest enemy in the level?
    the chunks could also crop the colidable rects 
i think collision box detection should happen and update, then hitbox/hurtbox detection happens
####
Must be nice
####
sfx:player hurt, spike clank, dirt clank, enemy hit, weapon swoosh, flower slashed

arbitrary amount of collisionboxes on player. big one for interacting, smaller for physics, smallerer hurtbox
    bonus: extrabig keep_talking box to let player keep movement while talking
    
particles should be like little sparks (not his sparks) when you jump or land or wallslide (brown pallette sparkler app LOL)
Maybe it spits one out every half second instead of like a sprinkler

geo could be different colors slightly maybe have to use pallets

frame advance

camera max and min distance each level

solids could have decor hanging off them, vines hanging from platforms

textbox in foreground so it moves parralax
####
Things to keep an eye on
####
Could have 3 chunk dicts for each map, one for small, big, boss size collisions (rn i just have bigish)

if the parallax background looks wack (when you make one) try making sure the depths are 1/2, 1/4, 1/8 etc so that they shift at the same time

each enemy checks whether the player is attacking instead of checking once
###
CHORES todo
###
Rename levels

probably should use an animation queue so stuff can like eg turn around then walk

parse out physics entities, player, npc, enemy. the inheritance is messy
determine what traits each has before implementation

should got_hit be in each enemy class. (its trash now w/ gothitspike and gothitprojectile)

change surfs to canvass where it makes sense

single time pickups and stuff like geo should be seperate

file structure

spikes pogo you > once per attack
'''
import sys

import pygame as pg 

from scripts import setup # pg.init right away!
from states import level_1, level_2, level_3, menu #### pg.init first!
from scripts.debugger import debugger
from scripts.event_processor import process_event

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
            action = process_event(event)
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
