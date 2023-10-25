import pygame as pg

from scripts.image_handler import load_image


original = load_image('small_font.png')
list_of_characters = list('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.-,:+\'!?0123456789()/_=\\[]*"<>; ') # should not be self. bc its only used in init?

height = 8
character_count = 0
current_charact_width = 0
character_images = {}
        
for x in range(original.get_width()):
    pixel_color = original.get_at((x, 0)) # y could be anything here
    if pixel_color[1] == 127: # todo: switch to full tuple (127,127,127,255)
        character_image = original.subsurface((x - current_charact_width, 0, current_charact_width, height))
        character_images[list_of_characters[character_count]] = character_image
        character_count += 1
        current_charact_width = 0
    else:
        current_charact_width += 1
                
class DialogueBox:
    def __init__(self, size, text):   
        self.text = text    
        self.size = size
        self.surf = pg.Surface(self.size).convert()
        self.character_images = character_images
        self.pos = (0, 0)
        self.height = 8
        self.kerning = 1
        self.line_spacing = 1
        self.active = False
        self.current_x = 0
        self.current_y = 0
        self.current_character = 0
        self.ticks_open = 0
        self.duration = 120
        
    def start(self):
        self.active = True
        self.current_x = 0
        self.current_y = 0
        self.current_character = 0
        self.ticks_open = 0
        self.surf = pg.Surface(self.size).convert()
        
    def update(self):
        if self.current_character != len(self.text):
            character = self.text[self.current_character]
            #check if it fits
            current_image = self.character_images[character]
            check_x = self.current_x + current_image.get_width()
            if check_x > self.size[0]:
                if character != ' ':
                    self.current_x = 0
                    self.current_y += 8
                    check_y = self.current_y + self.height + self.line_spacing
                    if check_y > self.size[1]:
                        pass
            self.surf.blit(current_image, (self.current_x, self.current_y))
            self.current_x += current_image.get_width() + self.kerning
            self.current_character += 1
        else:
            self.ticks_open += 1
            if self.ticks_open > self.duration:
                self.active = False
            
    def render(self, canvas, offset):
        canvas.blit(self.surf, (self.pos[0] - offset[0], self.pos[1] - offset[1]))
        
    def generate_line_of_text(self, text):
        text_width = 0
        for character in text:
            text_width += self.character_images[character].get_width() + self.kerning
            
        surf = pg.Surface((text_width - self.kerning, self.height)).convert()
        surf.set_colorkey((0, 0, 0))
        x_pos = 0
        for character in text:
            surf.blit(self.character_images[character], (x_pos, 0))
            x_pos += self.character_images[character].get_width() + self.kerning
        
        return surf
'''HERe is aa TEST dialogeue gbox good for testing im sure i coudlnttt come up with wnyh thing better112233'''


