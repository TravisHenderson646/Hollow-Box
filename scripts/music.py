import pygame as pg

class Music:    
    def __init__(self):
        self.current_song = ''
        self.path = 'data/music/'
        self.set_volume_dict = {
            'music.wav': 0.5,
            'music2.ogg': 0.05,
        }
        
    def play(self, next_song):
        if next_song != self.current_song: # if the song changed
            self.current_song = next_song
            print('New song starting...')
            pg.mixer.music.load(f'data/music/{next_song}')
            pg.mixer.music.set_volume(self.set_volume_dict[next_song])
            pg.mixer.music.play(-1)  
