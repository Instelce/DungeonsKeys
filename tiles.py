import pygame

from settings import *


class Tile(pygame.sprite.Sprite):
    def __init__(self, size, x, y):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill('purple')
        self.rect = self.image.get_rect(topleft=(x, y))


class Coin(Tile):
    def __init__(self, size, x, y):
        super().__init__(size, x, y)
        center_x = x + int(size / 2)
        center_y = y + int(size / 2)
        self.image.fill('yellow')
        self.rect = self.image.get_rect(center=(center_x, center_y))


class Spike(Tile):
    def __init__(self, size, x, y):
        super().__init__(size, x, y)
        self.image.fill('gray')
        self.rect = self.image.get_rect(topleft=(x, y))


