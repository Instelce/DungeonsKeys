import pygame, sys

from settings import *
from level import Level
from overworld import Overworld


class Game:
    def __init__(self):

        # Game attributes
        self.max_level = 1
        self.max_health = 100
        self.current_health = 100
        self.coins_count = 0

        # Overworld creation
        # self.overworld = Overworld(0, self.max_level, screen, self.create_level)
        self.level = Level(0, screen, self.create_overworld)
        self.status = 'level'

    def create_level(self, current_level):
        self.level = Level(current_level, screen, self.create_overworld)
        self.status = 'level'

    def create_overworld(self, current_level, new_max_level):
        if new_max_level > self.max_level:
            self.max_level = new_max_level
        self.overworld = Overworld(current_level, self.max_level, screen, self.create_level)
        self.status = 'overworld'

    def run(self):
        if self.status == 'overworld':
            self.overworld.run()
        else:
            self.level.run()


pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
game = Game()

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill('black')
    game.run()

    pygame.display.update()
    clock.tick(60)
