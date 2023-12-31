import os

import pygame as pg

BASE_IMG_PATH = 'data/images/'

def load_image(path):
    img = pg.image.load(BASE_IMG_PATH + path).convert()
    img.set_colorkey((0, 0, 0))
    return img

def load_images(path):
    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)): # for file_name in a list of the dir contents
        images.append(load_image(path + '/' + img_name))
    return images

class Animation:
    def __init__(self, images, image_dur=5, loop=True):
        self.images = images
        self.loop = loop
        self.image_dur = image_dur # larger dur is slower
        
        self.done = False
        self.frame = 0
        
    # Each entity makes a copy of the animation
    def copy(self):
        return Animation(self.images, self.image_dur, self.loop)
    
    def tick(self):
        if self.loop:
            self.frame = (self.frame + 1) % (self.image_dur * len(self.images))
        else:
            self.frame = min(self.frame + 1, self.image_dur * len(self.images) - 1)
            if self.frame >= self.image_dur * len(self.images) - 1:
                self.done = True
    
    def img(self):
        return self.images[int(self.frame / self.image_dur)]