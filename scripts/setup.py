import pygame as pg
# Initialize pygame and display information
pg.mixer.pre_init(44100, -16, 1, 512) # no idea how to do this in Control.__init__ like i should
pg.init()

pg.joystick.init()
print('joystick count', pg.joystick.get_count())
joysticks = [pg.joystick.Joystick(x) for x in range(pg.joystick.get_count())]
SCREEN = pg.display.set_mode((1280, 720)) # What the player sees # initializes pg.display automatically 1280,720
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
    'bird_guy/idle': Animation(load_images('entities/bird_guy/idle'), image_dur=12),
    'slug/idle': Animation(load_images('entities/slug/idle'), image_dur=12),
    'gnat/idle': Animation(load_images('entities/gnat/idle'), image_dur=12),
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

