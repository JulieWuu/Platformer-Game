import pygame
from os import listdir
from os.path import isfile, join

pygame.init()
pygame.display.set_mode((1200, 576))


def get_background(game, window, sequence):
    image = game.assets['background'][sequence]
    width = image.get_width()
    height = image.get_height()

    tiles = []
    for i in range(game.width // width + 1):
        for j in range(game.height // height + 1):
            pos = [i * width, j * height]
            tiles.append(pos)

    for tile in tiles:
        window.blit(image, tile)


def flip_horizontal(sprites):
    return[pygame.transform.flip(spr, True, False) for spr in sprites]


def flip_vertical(sprites):
    return[pygame.transform.flip(spr, False, True) for spr in sprites]


def flip_both(sprites):
    return[pygame.transform.flip(spr, True, True) for spr in sprites]


# dynamic, flip
def load_sprite_sheets(dir1, dir2, width, height, scale, direction_gravity=False):
    path = join("platformer_assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale(surface, (scale * width, scale * height)))

        if direction_gravity:
            all_sprites[image.replace(".png", "") + "_right_upright"] = sprites
            all_sprites[image.replace(".png", "") + "_left_upright"] = flip_horizontal(sprites)
            all_sprites[image.replace(".png", "") + "_right_upsidedown"] = flip_vertical(sprites)
            all_sprites[image.replace(".png", "") + "_left_upsidedown"] = flip_both(sprites)

        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites
