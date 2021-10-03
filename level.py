import pygame
import time

from settings import *
from tiles import *
from player import Player
from camera import Camera
from game_data import levels


class Level:
    def __init__(self, current_level, surface, create_overworld):
        self.display_surface = surface

        self.current_level = current_level
        level_data = levels[current_level]
        level_content = level_data['content']
        self.new_max_level = level_data['unlock']
        self.create_overworld = create_overworld

        self.setup_level(level_data['level_map'])

        # Level display
        self.font = pygame.font.Font(None, 40)
        self.text_surf = self.font.render(level_content, True, 'white')
        self.text_rect = self.text_surf.get_rect(center=(screen_width/2, screen_height/2))

        # Setup camera
        total_level_width = len(level_map[0]) * tile_size
        total_level_height = len(level_map) * tile_size
        self.camera = Camera(self.complex_camera, total_level_width, total_level_height)

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_o]:
            self.create_overworld(self.current_level, self.new_max_level)
        elif keys[pygame.K_p]:
            self.create_overworld(self.current_level, 0)

    def setup_level(self, layout):
        self.tiles = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.spikes = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle()

        for row_index, row in enumerate(layout):
            for col_index, cell in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size
                if cell == 'X':
                    tile = Tile(tile_size, x, y)
                    self.tiles.add(tile)
                elif cell == 'C':
                    coin = Coin(tile_size, x, y)
                    self.coins.add(coin)
                elif cell == 'S':
                    spike = Spike(tile_size, x, y)
                    self.spikes.add(spike)
                elif cell == 'P':
                    player_sprite = Player((x, y))
                    self.player.add(player_sprite)

    def horizontal_movement_collision(self):
        player = self.player.sprite
        player.rect.x += player.direction.x * player.speed

        for sprite in self.tiles.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.x < 0:
                    player.rect.left = sprite.rect.right
                elif player.direction.x > 0:
                    player.rect.right = sprite.rect.left

    def vertical_movement_collision(self):
        player = self.player.sprite
        player.apply_gravity()

        for sprite in self.tiles.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.y > 0:
                    player.rect.bottom = sprite.rect.top
                    player.direction.y = 0
                elif player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom
                    player.direction.y = 0

    def complex_camera(self, camera, target_rect):
        # we want to center target_rect
        x = -target_rect.center[0] + screen_width / 2
        y = -target_rect.center[1] + screen_height / 2
        # move the camera. Let's use some vectors so we can easily substract/multiply
        camera.topleft += (pygame.Vector2((x, y)) - pygame.Vector2(
            camera.topleft)) * 0.06  # add some smoothness coolnes
        # set max/min x/y so we don't see stuff outside the world
        camera.x = max(-(camera.width - screen_width), min(0, camera.x))
        camera.y = max(-(camera.height - screen_height), min(0, camera.y))

        return camera

    def run(self):
        self.input()

        # Camera
        self.camera.update(self.player.sprite)

        # Tiles
        for tile in self.tiles:
            self.display_surface.blit(tile.image, self.camera.apply(tile))
        for coin in self.coins:
            self.display_surface.blit(coin.image, self.camera.apply(coin))
        for spike in self.spikes:
            self.display_surface.blit(spike.image, self.camera.apply(spike))

        # PLayer
        self.player.update()
        self.horizontal_movement_collision()
        self.vertical_movement_collision()
        for player_sprite in self.player:
            self.display_surface.blit(player_sprite.image, self.camera.apply(player_sprite))

        # self.display_surface.blit(self.text_surf, self.text_rect)


