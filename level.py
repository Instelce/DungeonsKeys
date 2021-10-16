import pygame
import time

from settings import *
from tiles import *
from player import Player
from camera import Camera
from game_data import levels
from support import import_csv_layout, import_cut_graphics
from spike import Spike


class Level:
    def __init__(self, current_level, surface, create_overworld, change_coins, change_health, change_key, key_find):
        # General setup
        self.display_surface = surface
        self.current_x = 0

        # Overworld connection
        self.current_level = current_level
        level_data = levels[self.current_level]
        self.new_max_level = level_data['unlock']
        self.create_overworld = create_overworld

        # PLayer
        player_layout = import_csv_layout(level_data['player'])
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()

        # Terrain
        terrain_layout = import_csv_layout(level_data['terrain'])
        self.terrain_sprites = self.create_tile_group(terrain_layout, 'terrain')

        # Coins
        coin_layout = import_csv_layout(level_data['coins'])
        self.coin_sprites = self.create_tile_group(coin_layout, 'coins')

        # Keys
        key_layout = import_csv_layout(level_data['keys'])
        self.key_sprites = self.create_tile_group(key_layout, 'keys')

        # Spikes
        spike_layout = import_csv_layout(level_data['spikes'])
        self.spike_sprites = self.create_tile_group(spike_layout, 'spikes')

        # Constraint
        constraint_layout = import_csv_layout(level_data['constraints'])
        self.constraint_sprites = self.create_tile_group(constraint_layout, 'constraints')

        # User interface
        self.change_coins = change_coins
        self.change_key = change_key
        self.change_health = change_health
        self.key_find = key_find

        # Setup camera
        total_level_width = len(terrain_layout[0]) * tile_size
        total_level_height = len(terrain_layout) * tile_size
        self.camera = Camera(self.complex_camera, total_level_width, total_level_height)

        self.player_setup(player_layout, change_health)

        

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_o]:
            self.create_overworld(self.current_level, self.new_max_level)
        elif keys[pygame.K_p]:
            self.create_overworld(self.current_level, 0)

    def create_tile_group(self, layout, type):
        sprite_group = pygame.sprite.Group()

        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                if val != '-1':
                    x = col_index * tile_size
                    y = row_index * tile_size

                    if type == 'terrain':
                        terrain_tile_list = import_cut_graphics('graphics/terrain/terrain_tiles.png')
                        tile_surface = terrain_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)
                    if type == 'coins':
                        sprite = Coin(tile_size, x, y, 'graphics/coins')
                    if type == 'keys':
                        sprite = Key(tile_size, x, y, 'graphics/key/move')
                    if type == 'spikes':
                        if val == '0': sprite = Spike(tile_size, x, y, 'vertical')
                        elif val == '1': sprite = Spike(tile_size, x, y, 'horizontal')
                    if type == 'constraints':
                        sprite = Tile(tile_size, x, y)
                        
                    sprite_group.add(sprite)

        return sprite_group

    def player_setup(self, layout, change_health):
        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size
                if val == '0':
                    sprite = Player((x, y), self.display_surface, change_health)
                    self.player.add(sprite)
                if val == '1':
                    chess_surface = pygame.image.load('graphics/chess/chess__0.png').convert_alpha()
                    sprite = StaticTile(tile_size, x, y, chess_surface)
                    self.goal.add(sprite)

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
        if pygame.sprite.spritecollide(self.player.sprite, self.goal, False) and self.key_find():
            self.create_overworld(self.current_level, self.new_max_level)

    def check_key_collision(self):
        collided_key = pygame.sprite.spritecollide(self.player.sprite, self.key_sprites, True)
        if collided_key:
            self.change_key(1)
    
    def check_coin_collision(self):
        collided_coins = pygame.sprite.spritecollide(self.player.sprite, self.coin_sprites, True)
        if collided_coins:
            for coin in collided_coins:
                self.change_coins(1)

    def check_spike_collision(self):
        spike_collisions = pygame.sprite.spritecollide(self.player.sprite, self.spike_sprites, False)
        player = self.player.sprite

        if spike_collisions:
            for sprite in self.spike_sprites.sprites():
                if sprite.rect.colliderect(player.rect):
                    if player.direction.x < 0:
                        player.rect.left = sprite.rect.right
                        player.on_left = True
                        self.current_x = player.rect.left
                    elif player.direction.x > 0:
                        player.rect.right = sprite.rect.left
                        player.on_right = True
                        self.current_x = player.rect.right
            for sprite in self.spike_sprites.sprites():
                if sprite.rect.colliderect(player.rect):
                    if player.direction.y > 0:
                        player.rect.bottom = sprite.rect.top
                        player.direction.y = 0
                        player.on_ground = True
                    elif player.direction.y < 0:
                        player.rect.top = sprite.rect.bottom
                        player.direction.y = 0
                        player.on_ceiling = True
            player.get_damage()


    def spike_collision_reverse(self):
        for spike in self.spike_sprites.sprites():
            if pygame.sprite.spritecollide(spike, self.constraint_sprites, False):
                spike.reverse()

    def run(self):
        self.input()

        # Camera
        self.camera.update(self.player.sprite)

        # Terrain
        for tile in self.terrain_sprites:
            self.display_surface.blit(tile.image, self.camera.apply(tile))

        # PLayer
        self.player.update()
        self.player_horizontal_collision(self.terrain_sprites)
        self.player_vertical_collision(self.terrain_sprites)
        for tile in self.goal:
            self.display_surface.blit(tile.image, self.camera.apply(tile))
        for player_sprite in self.player:
            self.display_surface.blit(player_sprite.image, self.camera.apply(player_sprite))
        for pixel in self.player:
            self.display_surface.blit(player_sprite.image, self.camera.apply(player_sprite))

        # Check collision
        self.check_win()
        self.check_coin_collision() 
        self.check_key_collision()
        self.check_spike_collision()

        # Coins
        self.coin_sprites.update()
        for tile in self.coin_sprites:
            self.display_surface.blit(tile.image, self.camera.apply(tile))

        # Keys
        self.key_sprites.update() 
        for tile in self.key_sprites:
            self.display_surface.blit(tile.image, self.camera.apply(tile))

        # Spike and constraint
        self.spike_sprites.update()
        self.constraint_sprites.update()
        self.spike_collision_reverse()
        for tile in self.spike_sprites:
            self.display_surface.blit(tile.image, self.camera.apply(tile))

