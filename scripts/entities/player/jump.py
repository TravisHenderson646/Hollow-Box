from scripts.setup import sfx

class Jump:
    def __init__(self, player):
        self.player = player
        self.unlocked = True
        self.double_unlocked = True
        self.able = False
        self.coyote_time = 7
        self.buffer = 7
        self.held = False
        self.active = False
        self.ticks_since_input = 500
        self.can_double = False
        self.ticks_since_walljump = 500
        self.walljump_active = False
        self.walljump_duration = 4
        self.walljump_speed = 2
        self.walljump_direction = 1 # -1 left or 1 right
        self.impulse = -2.2
        self.double_impulse = self.impulse * 0.75
        self.walljump_impulse = self.double_impulse
        
    def check(self):
        if self.able:
            if self.unlocked:
                if self.ticks_since_input > 0:
                    print('Buffered jump alert!!!')
                self.start()
        else:
            if self.can_double:
                if self.double_unlocked:
                    if self.ticks_since_input > 0:
                        print('Buffered double jump alert!!!')
                    self.start_double()
                
    def start_double(self):
        self.ticks_since_input = 100
        print('Double jump!!!')
        self.active = True
        self.can_double = False
        self.player.movement.vel.y = min(self.player.movement.vel.y, self.double_impulse)
        
    def start_walljump(self):
        print('Wall jump!!!')
        self.player.wallslide.active = False
        self.ticks_since_walljump = 0
        self.active = True
        self.player.movement.vel.y = self.walljump_impulse
        self.ticks_since_input = 100
        self.walljump_direction = -self.player.wallslide.direction
            
    def start(self):
        self.ticks_since_input = 100
        if not self.player.movement.collisions['down']:
            print('Coyote jump alert !!!')
        self.able = False
        self.active = True
        self.player.movement.vel.y = self.impulse
        sfx['jump'].play()  
        
    def update(self):
        if self.held:
            self.player.movement.vel.y -= self.player.movement.gravity * 0.2
            self.player.animate.set_animation('jump')
            if self.player.movement.vel.y > 0:
                self.active = False
        else:
            self.player.movement.vel.y = 0.1
            self.active = False
   #     if self.player.vel.y == 0:
 #           self.active = False
        if self.ticks_since_walljump < self.walljump_duration:
            self.player.movement.vel.x = self.walljump_speed * self.walljump_direction
            self.walljump_active = True