import json

from scripts import setup


class Saves:
    def __init__(self):
        self.save_data = self.load_save()
        
    def load_save(self):
        with open('data/saves/save1.json', 'r') as file:
            try: 
                return json.load(file)['save_data']
            except FileNotFoundError:
                return {}
            
    def update_save_data(self):
        self.save_data['ticks'] += setup.GAME_TICK
            
    def save_game(self):
        print('attempting save')
        print('savedata', self.save_data)
        self.update_save_data()
        with open('data/saves/save1.json', 'w') as file:
            json.dump({'save_data': self.save_data,}, file, indent=2)
        print(f'play time: {self.calculate_play_time()}')
    
    def calculate_play_time(self):
        ticks = self.save_data['ticks']
        seconds = ticks/60
        minutes = seconds//60
        hours = minutes//60
        seconds -= minutes * 60
        minutes -= hours * 60
        return f'{int(hours)} hours, {int(minutes)} minutes, {int(seconds)} seconds'