import pygame as pg
# Initialize pygame and display information
pg.mixer.pre_init(44100, -16, 1, 512) # no idea how to do this in Control.__init__ like i should
pg.init()

pg.joystick.init()
print('joystick count', pg.joystick.get_count())
joysticks = [pg.joystick.Joystick(x) for x in range(pg.joystick.get_count())]


SCREEN = pg.display.set_mode((1280, 720)) # What the player sees # initializes pg.display automatically
SCREEN_SIZE = SCREEN.get_size()
CANVAS = pg.Surface((320, 180)) # What the player sees
CANVAS_SIZE = CANVAS.get_size()
PLAYER_COLLISION_SIZE = (7, 13)
CHUNK_SIZE = (60, 60)
GAME_TICK = 0

from scripts.image_handler import load_image, load_images, Animation

assets = { # dict of every sprite's image or animation's set of images
    'decor': load_images('tiles/decor'),
    'grass': load_images('tiles/grass'),
    'special': load_images('tiles/special'),
    'large_decor': load_images('tiles/large_decor'),
    'stone': load_images('tiles/stone'),
    'player': load_image('entities/player.png'),
    'background': load_image('background.png'),
    'clouds' : load_images('clouds'),
    'enemy/idle': Animation(load_images('entities/enemy/idle'), 12), # could be 'player.idle' as the key instead
    'enemy/run': Animation(load_images('entities/enemy/run'), 8),
    'player/idle': Animation(load_images('entities/player/idle'), image_dur=12),
    'player/run': Animation(load_images('entities/player/run'), image_dur=8),
    'player/jump': Animation(load_images('entities/player/jump'), image_dur=5,),
    'player/slide': Animation(load_images('entities/player/slide'), image_dur=5,),
    'player/wallslide': Animation(load_images('entities/player/wallslide'), image_dur=5,),
    'particle/leaf': Animation(load_images('particles/leaf'), 20, False),
    'particle/particle': Animation(load_images('particles/particle'), 6, False),
    'slug/idle': Animation(load_images('entities/slug/idle'), image_dur=12),
    'gun': load_image('gun.png'),
    'projectile': load_image('projectile.png'),
    'entrances': load_images('tiles/entrances'),
    'exits': load_images('tiles/exits'),
} # todo way later on this should probably be split up so theyre not all loaded at the same time

sfx = { # dict of every sound effect
    'jump': pg.mixer.Sound('data/sfx/jump.wav'),
    'dash': pg.mixer.Sound('data/sfx/hit.wav'),
    'hit': pg.mixer.Sound('data/sfx/dash.wav'),
    'shoot': pg.mixer.Sound('data/sfx/shoot.wav'),
    'ambience': pg.mixer.Sound('data/sfx/ambience.wav'),
}

# manually setting individual volumes
sfx['jump'].set_volume(0.2)
sfx['dash'].set_volume(0.2)
sfx['hit'].set_volume(0.12)
sfx['shoot'].set_volume(0.2)
sfx['ambience'].set_volume(0.7)

class _EventProcessor:
    def __init__(self):
        self.lt_value = 0
        self.rt_value = 0
        
    def process_event(self, event):
        action = ''
        if event.type == pg.QUIT:
            action = 'quit'
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                action = 'start'
            if event.key == pg.K_a:
                action = 'left'
            if event.key == pg.K_d:
                action = 'right'
            if event.key == pg.K_w:
                action = 'up'
            if event.key == pg.K_s:
                action = 'down'
            if event.key == pg.K_SPACE:
                action = 'a'
            if event.key == pg.K_j:
                action = 'x'
            if event.key == pg.K_i:
                action = 'rt'
            if event.key == pg.K_k:
                action = 'lt'
            if event.key == pg.K_p:
                action = 'p'
        elif event.type == pg.KEYUP:
            if event.key == pg.K_a:
                action = 'unleft'
            if event.key == pg.K_d:
                action = 'unright'
            if event.key == pg.K_w:
                action = 'unup'
            if event.key == pg.K_s:
                action = 'undown'
            if event.key == pg.K_SPACE:
                action = 'una'
            if event.key == pg.K_i:
                action = 'unrt'
            if event.key == pg.K_k:
                action = 'unlt'
        elif event.type == pg.JOYBUTTONDOWN:
            if event.button == 7:
                action = 'start'
            if event.button == 0:
                action = 'a'
            if event.button == 2:
                action = 'x'
        elif event.type == pg.JOYBUTTONUP:
            if event.button == 0:
                action = 'una'
        elif event.type == pg.JOYAXISMOTION:
            if event.axis == 0:
                if event.value < -0.3:
                    action = 'left'
                if event.value > 0.3:
                    action = 'right'
                if -0.3 < event.value < 0.3:
                    action = 'stop'
            if event.axis == 1:
                if event.value < -0.3:
                    action = 'up'
                if event.value > 0.3:
                    action = 'down'
                if -0.3 < event.value < 0.3:
                    action = 'neutral'
            if event.axis == 4:
                if event.value > 0.8 and self.lt_value <= 0.8:
                    action = 'lt'
                if event.value < 0.8 and self.lt_value >= 0.8:
                    action = 'unlt'
                self.lt_value = event.value
            if event.axis == 5:
                if event.value > 0.8 and self.rt_value <= 0.8:
                    action = 'rt'
                if event.value < 0.8 and self.rt_value >= 0.8:
                    action = 'unrt'
                self.rt_value = event.value    
        return action

_event_processor = _EventProcessor()
process_event = _event_processor.process_event