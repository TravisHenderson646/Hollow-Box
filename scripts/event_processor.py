import pygame as pg

class _EventProcessor:
    def __init__(self):
        self.lt_value = 0
        self.rt_value = 0
        self.ls_valuex = 0
        self.ls_valuey = 0
        
    def _process_event(self, event):
        action = ''
        if event.type == pg.QUIT:
            action = 'quit'
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                action = 'start'
            if event.key == pg.K_a:
                action = 'left'
            if event.key == pg.K_d:
                action = 'right'
            if event.key == pg.K_w:
                action = 'up'
            if event.key == pg.K_s:
                action = 'down'
            if event.key == pg.K_SPACE:
                action = 'a'
            if event.key == pg.K_j:
                action = 'x'
            if event.key == pg.K_i:
                action = 'lt'
            if event.key == pg.K_k:
                action = 'rt'
            if event.key == pg.K_r: # for testing, rouyt
                action = 'r'
            if event.key == pg.K_u: # for testing, rouyt
                action = 'u'
            if event.key == pg.K_o: # for testing, rouyt
                action = 'o'
            if event.key == pg.K_t: # for testing, rouyt
                action = 't'
            if event.key == pg.K_y: # for testing, rouyt
                action = 'y'
        elif event.type == pg.KEYUP:
            if event.key == pg.K_a:
                action = 'unleft'
            if event.key == pg.K_d:
                action = 'unright'
            if event.key == pg.K_w:
                action = 'unup'
            if event.key == pg.K_s:
                action = 'undown'
            if event.key == pg.K_SPACE:
                action = 'una'
            if event.key == pg.K_i:
                action = 'unlt'
            if event.key == pg.K_k:
                action = 'unrt'
        elif event.type == pg.JOYBUTTONDOWN:
            if event.button == 7:
                action = 'start'
            if event.button == 0:
                action = 'a'
            if event.button == 2:
                action = 'x'
        elif event.type == pg.JOYBUTTONUP:
            if event.button == 0:
                action = 'una'
        elif event.type == pg.JOYAXISMOTION:
            if event.axis == 0:
                if event.value < -0.3 and self.ls_valuex >= -0.3:
                    action = 'left'
                if event.value > 0.3 and self.ls_valuex <= 0.3:
                    action = 'right'
                if -0.3 < event.value < 0.3 and ((self.ls_valuex <= -0.3) or (self.ls_valuex >= 0.3)):
                    action = 'stop'
                self.ls_valuex = event.value
            if event.axis == 1:
                if event.value < -0.3 and self.ls_valuey >= -0.3:
                    action = 'up'
                if event.value > 0.3 and self.ls_valuey <= 0.3:
                    action = 'down'
                if -0.3 < event.value < 0.3 and ((self.ls_valuey <= -0.3) or (self.ls_valuey >= 0.3)):
                    action = 'neutral'
                self.ls_valuey = event.value
            if event.axis == 4:
                if event.value > 0.8 and self.lt_value <= 0.8:
                    action = 'lt'
                if event.value < 0.8 and self.lt_value >= 0.8:
                    action = 'unlt'
                self.lt_value = event.value
            if event.axis == 5:
                if event.value > 0.8 and self.rt_value <= 0.8:
                    action = 'rt'
                if event.value < 0.8 and self.rt_value >= 0.8:
                    action = 'unrt'
                self.rt_value = event.value    
        return action

_event_processor = _EventProcessor()
process_event = _event_processor._process_event