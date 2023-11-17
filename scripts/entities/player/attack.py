import pygame as pg

class Attack:
    def __init__(self, player):
        self.player = player
        self.unlocked = True
        self.damage = 2
        self.direction = 0 # 0,1,2,3=right,down,left,up
        self.duration = 6
        self.cooldown = 33
        self.ticks_since_input = 500
        self.ticks_since_knockback = 500
        self.knockback_duration = 7
        self.buffer = 7
        self.ticks_since_last = 500
        self.in_knockback = False
        self.active_hitboxes = 0 # could be active hitboxes
        self.active = False
        
        self.hitboxes = []
        self.hitboxes_vertical = []
        self.surfaces = []
        self.surfaces_vertical = [] # these could be in a dict with names
        self.hitboxes.append(pg.FRect(0, 0,  8, 13))
        self.hitboxes.append(pg.FRect(0, 0,  7,  9))
        self.hitboxes.append(pg.FRect(0, 0, 13,  5))
        self.hitboxes.append(pg.FRect(0, 0,  3,  3))
        self.hitboxes_vertical.append(pg.FRect(0, 0, 13,  7))
        self.hitboxes_vertical.append(pg.FRect(0, 0,  9,  7))
        self.hitboxes_vertical.append(pg.FRect(0, 0,  5, 12))
        self.hitboxes_vertical.append(pg.FRect(0, 0,  3,  3))
        self.hitbox_list = [self.hitboxes, self.hitboxes_vertical]
        for hitbox in self.hitboxes:
            self.surfaces.append(pg.Surface(hitbox.size))
            self.surfaces[-1].fill((150,50,100))
        for hitbox in self.hitboxes_vertical:
            self.surfaces_vertical.append(pg.Surface(hitbox.size))
            self.surfaces_vertical[-1].fill((150,50,100))
        
    def update(self):
        match self.direction:
            case 2: #left
                self.hitboxes[0].centery = self.player.rect.centery
                self.hitboxes[0].right = self.player.rect.centerx
                self.hitboxes[1].centery = self.player.rect.centery
                self.hitboxes[1].right = self.hitboxes[0].left
                self.hitboxes[2].centery = self.player.rect.centery
                self.hitboxes[2].right = self.hitboxes[1].left
                self.hitboxes[3].centery = self.player.rect.centery
                self.hitboxes[3].right = self.hitboxes[2].left
            case 0: #right
                self.hitboxes[0].centery = self.player.rect.centery
                self.hitboxes[0].left = self.player.rect.centerx
                self.hitboxes[1].centery = self.player.rect.centery
                self.hitboxes[1].left = self.hitboxes[0].right
                self.hitboxes[2].centery = self.player.rect.centery
                self.hitboxes[2].left = self.hitboxes[1].right
                self.hitboxes[3].centery = self.player.rect.centery
                self.hitboxes[3].left = self.hitboxes[2].right
            case 3: #up
                self.hitboxes_vertical[0].centerx = self.player.rect.centerx
                self.hitboxes_vertical[0].bottom = self.player.rect.centery
                self.hitboxes_vertical[1].centerx = self.player.rect.centerx
                self.hitboxes_vertical[1].bottom = self.hitboxes_vertical[0].top
                self.hitboxes_vertical[2].centerx = self.player.rect.centerx
                self.hitboxes_vertical[2].bottom = self.hitboxes_vertical[1].top
                self.hitboxes_vertical[3].centerx = self.player.rect.centerx
                self.hitboxes_vertical[3].bottom = self.hitboxes_vertical[2].top
            case 1: #down
                self.hitboxes_vertical[0].centerx = self.player.rect.centerx
                self.hitboxes_vertical[0].top = self.player.rect.centery
                self.hitboxes_vertical[1].centerx = self.player.rect.centerx
                self.hitboxes_vertical[1].top = self.hitboxes_vertical[0].bottom
                self.hitboxes_vertical[2].centerx = self.player.rect.centerx
                self.hitboxes_vertical[2].top = self.hitboxes_vertical[1].bottom
                self.hitboxes_vertical[3].centerx = self.player.rect.centerx
                self.hitboxes_vertical[3].top = self.hitboxes_vertical[2].bottom
    
    def check(self):
        if self.ticks_since_last > self.cooldown:
            if self.unlocked:
                if not self.player.dash.active:
                    if self.ticks_since_input > 0:
                        print('Buffered attack alert!!!', self.ticks_since_input)
                    self.start()
            
    def start(self):
        self.ticks_since_last = 0 # this is what actually causes the attack in update()
        self.ticks_since_input = 100
        if self.player.wallslide.active:
            if self.player.wallslide.direction == 1:
                self.direction = 2 #left
                self.active_hitboxes = 0
            if self.player.wallslide.direction == -1:
                self.direction = 0 #right
                self.active_hitboxes = 0
        elif (self.player.movement.movement.y == 1) and (not self.player.movement.collisions['down']):
            self.direction = 1 #down
            self.active_hitboxes = 1
        elif self.player.movement.movement.y == -1:
            self.direction = 3 #up
            self.active_hitboxes = 1
        elif self.player.animate.flip:
            self.direction = 2 #left
            self.active_hitboxes = 0
        else:
            self.direction = 0 #right
            self.active_hitboxes = 0
                
    def knockback(self):
        match self.direction:
            case 2: #left
                self.player.movement.vel.x = 1.5 # could use max here to make sure it doesn't override a bigger knockback
            case 0: #right
                self.player.movement.vel.x = -1.5
            case 3: #up
                self.player.movement.vel.y = max(1, self.player.movement.vel.y)
            case 1: #down pogo
                if self.ticks_since_knockback == 0: # to make it an impulse
                    self.player.jump.active = False
                    self.player.movement.vel.y = min(self.player.movement.vel.y, self.player.jump.double_impulse)
                    self.player.jump.can_double = True
                    self.player.dash.able = True
        self.ticks_since_knockback += 1
        if self.knockback_duration < self.ticks_since_knockback:
            self.in_knockback = False