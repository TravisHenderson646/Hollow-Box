import pygame as pg

from scripts.entities.physics_entity import PhysicsEntity

class Crawlid(PhysicsEntity):
    def __init__(self, pos, size):
        super().__init__('crawlid', pos, size)