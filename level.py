import pygame
import time

from settings import *
from tiles import *
from player import Player
from camera import Camera
from game_data import levels


class Level:
    def __init__(self, current_level, surface, create_overworld, change_coins, change_health, change_key, key_find):
        # General setup
        self.display_surface = surface
        self.current_x = 0

        # Overworld connection
        self.current_level = current_level
        level_data = levels[current_level]
        level_name = level_data['name']
        self.new_max_level = level_data['unlock']
        self.create_overworld = create_overworld

        self.setup_level(level_data['level_map'], change_health)

        # User interface
        self.change_coins = change_coins
        self.change_key = change_key
        self.key_find = key_find

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

    def setup_level(self, layout, change_health):
        self.tiles = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.spikes = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()
        self.key = pygame.sprite.GroupSingle()

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
                    player_sprite = Player((x, y), self.display_surface, change_health)
                    self.player.add(player_sprite)
                elif cell == 'G':
                    goal_sprite = Goal(tile_size, x, y)
                    self.goal.add(goal_sprite)
                elif cell == 'K':
                    key_sprite = Key(tile_size, x, y)
                    self.key.add(key_sprite)

    def player_horizontal_collision(self, tiles):
        player = self.player.sprite
        player.rect.x += player.direction.x * player.speed

        for sprite in tiles.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.x < 0:
                    player.rect.left = sprite.rect.right
                    player.on_left = True
                    self.current_x = player.rect.left
                elif player.direction.x > 0:
                    player.rect.right = sprite.rect.left
                    player.on_right = True
                    self.current_x = player.rect.right

        if player.on_left and (player.rect.left < self.current_x or player.direction.x >= 0):
            player.on_left = False
        elif player.on_right and (player.rect.right > self.current_x or player.direction.x <= 0):
            player.on_right = False

    def player_vertical_collision(self, tiles):
        player = self.player.sprite
        player.apply_gravity()

        for sprite in tiles.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.y > 0:
                    player.rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True
                elif player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom
                    player.direction.y = 0
                    player.on_ceiling = True

        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False
        if player.on_ceiling and player.direction.y > 0:
            player.on_ceiling = False

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

    def check_win(self):
        if pygame.sprite.spritecollide(self.player.sprite, self.goal, False) and self.key_find:
            self.create_overworld(self.current_level, self.new_max_level)

    def check_key_collision(self):
        collided_key = pygame.sprite.spritecollide(self.player.sprite, self.key, True)
        if collided_key:
            self.change_key(1)
    
    def check_coin_collision(self):
        collided_coins = pygame.sprite.spritecollide(self.player.sprite, self.coins, True)
        if collided_coins:
            for coin in collided_coins:
                self.change_coins(1)

    def check_spike_collision(self):
        spike_collisions = pygame.sprite.spritecollide(self.player.sprite, self.spikes, False)
        player = self.player.sprite

        if spike_collisions:
            self.player_horizontal_collision(self.spikes)
            self.player_vertical_collision(self.spikes)
            player.get_damage()
            # for spike in spike_collisions:
            #     if spike.rect.colliderect(player):
            #         player.get_damage()
            #         if player.direction.x < 0:
            #             player.rect.left = spike.rect.right
            #         elif player.direction.x > 0:
            #             player.rect.right = spike.rect.left
            # for spike in spike_collisions:
            #     if spike.rect.colliderect(player):
            #         player.get_damage()
            #         if player.direction.y > 0:
            #             player.rect.bottom = spike.rect.top
            #             player.direction.y = 0
            #         elif player.direction.y < 0:
            #             player.rect.top = spike.rect.bottom
            #             player.direction.y = 0

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
        for goal in self.goal:
            self.display_surface.blit(goal.image, self.camera.apply(goal))
        for key in self.key:
            self.display_surface.blit(key.image, self.camera.apply(key))

        # PLayer
        self.player.update()
        self.player_horizontal_collision(self.tiles)
        self.player_vertical_collision(self.tiles)
        for player_sprite in self.player:
            self.display_surface.blit(player_sprite.image, self.camera.apply(player_sprite))

        self.check_key_collision()
        self.check_win()
        self.check_coin_collision()
        self.check_spike_collision()

