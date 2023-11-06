import random

class Cloud:
    def __init__(self, pos, img, speed, depth):
        self.pos = list(pos)
        self.img = img
        self.speed = speed
        self.depth = depth
        
    def update(self):
        self.pos[0] += self.speed
        
    def render(self, canvas, offset):
        render_pos = (self.pos[0] - offset[0] * self.depth, self.pos[1] - offset[1] * self.depth)
        canvas.blit(self.img, (render_pos[0] % (canvas.get_width() + self.img.get_width()) - self.img.get_width(), render_pos[1] % (canvas.get_height() + self.img.get_height()) - self.img.get_height()))
        
        
        
class Clouds:
    def __init__(self, cloud_images, count=16):
        self.clouds = []
        
        for i in range(count):
            self.clouds.append(Cloud((random.random() * 999, random.random() * 999), random.choice(cloud_images), random.random() * 0.1 + 0.05, random.random() * 0.5 + 0.05))
            
            
        self.clouds.sort(key=lambda x: -x.depth)
        
    def update(self):
        for cloud in self.clouds:
            cloud.update()
        
    def render(self, canvas, offset):
        for cloud in self.clouds:
            cloud.render(canvas, offset)