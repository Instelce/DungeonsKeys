import pygame

from settings import *
from tiles import Tile
from player import Player
from camera import Camera


class Level:
    def __init__(self, level_data, surface):
        self.display_surface = surface
        self.setup_level(level_data)

        total_level_width = len(level_map[0]) * tile_size
        total_level_height = len(level_map) * tile_size
        self.camera = Camera(self.complex_camera, total_level_width, total_level_height)

    def setup_level(self, layout):
        self.tiles = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle()

        for row_index, row in enumerate(layout):
            for col_index, cell in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size
                if cell == 'X':
                    tile = Tile((x, y), tile_size, 'purple')
                    self.tiles.add(tile)
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
        # Camera
        self.camera.update(self.player.sprite)

        # Tiles
        for tile in self.tiles:
            self.display_surface.blit(tile.image, self.camera.apply(tile))

        # PLayer
        self.player.update()
        self.horizontal_movement_collision()
        self.vertical_movement_collision()
        for player_sprite in self.player:
            self.display_surface.blit(player_sprite.image, self.camera.apply(player_sprite))






