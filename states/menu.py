import pygame as pg

from states.game import Game

class Menu(Game):
    def __init__(self):
        super().__init__()
        self.next = 'level1'
        self.previous : str
        self.screen_name_position = (20, 20)
   #     self.menu_textbox = Game.text.generate_line_of_text('This is the flippin menu!!! Man it\'s starting to look GOOOOOD l0O0l')
        
        
    def cleanup(self):
        print('cleaning up Menu state stuff...')
        
    def start(self):
        print('starting Menu state stuff...')
        Game.music.play('music2.ogg')
        
    def process_action(self, action):
        super().process_action(action)
        if action == 'start':
            self.quit = True
        elif action:
            self.done = True
                
    def update(self):
        pass
    
    def render(self, canvas):
        canvas.fill((150,60,150))
 #       canvas.blit(self.menu_textbox, self.screen_name_position)
        return canvas
  