import pygame as pg



class Entity:
    def __init__(self, name, pos, size):
        self.name = name
        self.rect = pg.FRect(*pos, *size)
        