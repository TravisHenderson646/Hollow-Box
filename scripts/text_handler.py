import pygame as pg

from scripts.image_handler import load_image

from scripts.debugger import debugger


original = load_image('small_font.png')
list_of_characters = list('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.-,:+\'!?0123456789()/_=\\[]*"<>; ') # should not be self. bc its only used in init?

height = 8
character_count = 0
current_character_width = 0
character_images = {}
        
for x in range(original.get_width()):
    pixel_color = original.get_at((x, 0)) # y could be anything here
    if pixel_color[1] == 127: # todo: switch to full tuple (127,127,127,255)
        character_image = original.subsurface((x - current_character_width, 0, current_character_width, height))
        character_images[list_of_characters[character_count]] = character_image
        character_count += 1
        current_character_width = 0
    else:
        current_character_width += 1
                
class DialogueBox:
    def __init__(self, size, script):   
        self.script = script
        self.batch = 0
        self.message = 0
        self.text = self.script[self.batch][self.message]
        self.remaining_text = self.text
        self.size = size
        self.surf = pg.Surface(self.size).convert()
        self.character_images = character_images
        self.pos = (0, 0)
        self.height = 8
        self.kerning = 1
        self.line_spacing = 1
        self.active = False
        self.still_talking = False
        self.message_completed = False
        self.current_x = 0
        self.current_y = 0
        self.current_character_index = 0
        self.ticks_open = 0
        self.tick = 0
        self.speed = 2
        self.duration = 150 / self.speed
        
    def start(self):
        if not self.active:
            if self.message_completed:
                self.message += 1
            self.remaining_text = self.script[self.batch][min(self.message, len(self.script[self.batch]) - 1)]
            self.active = True
            self.still_talking = True
            self.message_completed = False
            self.current_x = 0
            self.current_y = 0
            self.current_character_index = 0
            self.ticks_open = 0
            self.surf = pg.Surface(self.size).convert()
        elif self.still_talking:
            self.player_skip_chat()
        elif self.message_completed:
            self.active = False
        else: # if active and theres more message but you're not talking
            self.still_talking = True            
            self.current_x = 0
            self.current_y = 0
            self.current_character_index = 0
            self.ticks_open = 0
            self.surf = pg.Surface(self.size).convert()
        
    def update(self):
        print('active')
        self.tick += 1
        if self.tick % self.speed == 0:
            if self.still_talking:
                character = self.remaining_text[self.current_character_index]
                current_image = self.character_images[character]
                #check if word fits
                i = 0
                test_character = character
                check_x = self.current_x
                test_image = current_image
                while (test_character != ' ') and (self.current_character_index + i != len(self.remaining_text)):
                    test_character = self.remaining_text[self.current_character_index + i]
                    test_image = self.character_images[test_character]
                    check_x += test_image.get_width() + self.kerning
                    i += 1

                if check_x > self.size[0]:
                    check_y = self.current_y + self.height * 2 + self.line_spacing
                    if check_y > self.size[1]:
                        self.still_talking = False
                        self.remaining_text = self.remaining_text[self.current_character_index:]
                    else:
                        self.current_x = 0
                        self.current_y += 8
                if self.still_talking:
                    self.surf.blit(current_image, (self.current_x, self.current_y))
                    self.current_x += current_image.get_width() + self.kerning
                    self.current_character_index += 1
                    if self.current_character_index == len(self.remaining_text):
                        self.still_talking = False
                        self.message_completed = True
            else:
                self.ticks_open += 1
                if self.ticks_open > self.duration:
                    self.start()
                
    def player_skip_chat(self):  
        for character in self.remaining_text[self.current_character_index:]:
            current_image = self.character_images[character]                
            #check if word fits
            i = 0
            test_character = character
            check_x = self.current_x
            test_image = current_image
            while (test_character != ' ') and (self.current_character_index + i != len(self.remaining_text)):
                test_character = self.remaining_text[self.current_character_index + i]
                test_image = self.character_images[test_character]
                check_x += test_image.get_width() + self.kerning
                i += 1
            if check_x > self.size[0]:
                check_y = self.current_y + self.height * 2 + self.line_spacing
                if check_y > self.size[1]:
                    self.remaining_text = self.remaining_text[self.current_character_index:]
                    self.still_talking = False
                    break
                else:
                    self.current_x = 0
                    self.current_y += 8
            self.surf.blit(current_image, (self.current_x, self.current_y))
            self.current_x += current_image.get_width() + self.kerning
            self.current_character_index += 1
            if self.current_character_index == len(self.remaining_text):
                self.still_talking = False
                self.message_completed = True
                break

            
    def render(self, canvas, offset):
        canvas.blit(self.surf, (self.pos[0] - offset[0], self.pos[1] - offset[1]))
        # if active but not still_talking, blit a little dot on the bottom right to say see more
        
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


