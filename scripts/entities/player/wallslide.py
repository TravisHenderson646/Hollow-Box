from scripts.setup import sfx

class WallSlide:
    def __init__(self, player):
        self.player = player
        self.unlocked = True
        self.active = False
        self.speed = 0.8
        self.detach_buffer = 3
        self.ticks_detaching = 500
        self.direction = 1 # 1 or -1
        
    def start(self, direction):
        if self.unlocked:
            self.active = True
            self.player.jump.active = False
            self.player.jump.can_double = True
            self.player.dash.able = True
            self.ticks_detaching = 0
            self.direction = direction
        
    def update(self, tilemap):
        self.player.movement.vel.y = min(self.player.movement.vel.y, self.speed)
        self.player.animate.set_animation('wallslide')
        if self.direction == -1:
            self.player.animate.flip = True
            self.active = tilemap.check_wallslide(self.player)
            if self.player.movement.movement.x == 1:
                self.ticks_detaching += 1
                if self.ticks_detaching > self.detach_buffer:
                    self.active = False
            else:
                self.ticks_detaching = 0
        if self.direction == 1:
            self.player.animate.flip = False
            self.active = tilemap.check_wallslide(self.player)
            if self.player.movement.movement.x == -1:
                self.ticks_detaching += 1
                if self.ticks_detaching > self.detach_buffer:
                    self.active = False
            else:
                self.ticks_detaching = 0 