from scripts import setup

class Particle:
    def __init__(self, particle_type, pos, vel=[0, 0], frame=0):
        self.name = particle_type
        self.pos = list(pos)
        self.vel = list(vel)
        self.animation = setup.assets['particle/' + self.name].copy()
        self.animation.frame = frame
        
    def update(self):
        kill = False
        if self.animation.done:
            kill = True
        
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        
        self.animation.tick()
        
        return kill
    
    def render(self, canvas, offset):
        image = self.animation.img()
        canvas.blit(image, (self.pos[0] - offset[0] - image.get_width() // 2, self.pos[1] - offset[1] - image.get_height() // 2))