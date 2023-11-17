from scripts.setup import sfx

class Dash:
    def __init__(self, player):
        self.player = player
        self.unlocked = True
        self.able = False
        self.buffer = 7
        self.active = False
        self.ticks_since_input = 500
        self.ticks_since_last = 500
        self.cooldown = 33
        self.direction = 1 # -1 or 1 (L or R)
        self.duration = 9
        self.speed = 2.5
        
    def check(self):
        if self.able:
            if self.unlocked:
                self.start()
                if self.ticks_since_input > 0:
                    print('Buffered dash alert!!!')
                self.ticks_since_input = 100
            
    def start(self):
        if self.ticks_since_last > self.cooldown:
            sfx['jump'].play()
            self.player.jump.active = False
            self.active = True
            self.ticks_since_last = 0
            self.able = False
            if self.player.wallslide.active:
                self.direction = -self.player.wallslide.direction
            elif self.player.movement.movement.x:
                self.direction = self.player.movement.movement.x
            else:
                if self.player.animate.flip:
                    self.direction = -1
                else:
                    self.direction = 1

    def update(self):
        if self.ticks_since_last < self.duration:
            self.player.movement.vel.y = 0
            self.player.movement.vel.x = self.player.movement.speed * self.speed * self.direction
        else:
            self.active = False