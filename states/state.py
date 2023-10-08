from scripts.music import Music

class State:
    music = Music()
    
    def __init__(self):
        self.done = False
        self.quit = False
        self.next : str
        self.previous : str
        
    def cleanup(self):
        pass
    
    def start(self):
        pass
    
    def process_event(self, event):
        pass
    
    def update(self):
        pass
    
    def render(self, canvas):
        pass