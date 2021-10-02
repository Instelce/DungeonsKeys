import pygame

from settings import *


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, size, color):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=pos)

