from scripts.music import Music
from scripts.saves import Saves
from scripts.text_handler import DialogueBox

class Game:
    music = Music()
    saves = Saves()
   # text = DialogueBox((1,1), '1')
    
    def __init__(self):
        self.done = False
        self.quit = False
        self.next : str
        self.previous : str
        
    def quicksave(self):
        Game.saves.save_game()
        
    def cleanup(self):
        pass
    
    def start(self):
        pass
    
    def process_action(self, action):
        pass
    
    def update(self):
        pass
    
    def render(self, canvas):
        pass