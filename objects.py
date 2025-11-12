import pygame
import os
from os.path import join

# my own files
import load_sprite_sheets
from load_sprite_sheets import load_sprite_sheets
from vector import *


# still, flip
def get_block(name):
    path = join("platformer_assets", "terrain", name + '.png')
    image = pygame.image.load(path).convert_alpha()
    return image


def load_images(path):
    images = []
    for img_name in sorted(os.listdir('platformer_assets/' + path)):
        images.append(pygame.image.load('platformer_assets/' + path + '/' + img_name).convert_alpha())
    return images


def load_music(path):
    music = []
    for sound in sorted(os.listdir('platformer_assets/' + path)):
        music.append(pygame.mixer.Sound('platformer_assets/' + path + '/' + sound))
    return music


# still, scale
def get_function(name, scale):
    path = join("platformer_assets", "menu", "buttons", name + ".png")
    image = pygame.image.load(path).convert_alpha()
    if name == "Back" or name == "Close":
        width, height = 15, 16
    elif name == "Heart":
        width, height = 200, 200
    else:
        width, height = 21, 22
    surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
    rect = pygame.Rect(0, 0, width, height)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale(surface, (scale * width, scale * height))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name, scale, flip):
        super().__init__()
        self.rect = pygame.Rect(x, y, width * scale, height * scale)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name
        self.scale = scale
        self.flip = flip

    def draw(self, window, offset=(0, 0)):
        window.blit(self.image, (self.rect.x - offset[0], self.rect.y - offset[1]))


# still, flip, moving, collision
class Block(Object):
    def __init__(self, x, y, name):
        super().__init__(x, y, 48, 48, name, 1, False)
        block = get_block(name)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


# still, scale, fixed
class Function(Object):
    def __init__(self, x, y, name, scale):
        super().__init__(x, y, scale * 22, scale * 22, name, scale, False)
        function = get_function(name, scale)
        self.scale = scale
        self.image.blit(function, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


# dynamic, flip, moving, collision
class Traps(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height, name, scale, flip):
        super().__init__(x, y, width, height, name, scale, flip)
        self.rect.x = x
        self.rect.y = y
        self.pos = Vector(x, y)
        self.name = name
        self.scale = scale
        self.trap = load_sprite_sheets("traps", self.name, width, height, self.scale, True)
        self.image = self.trap["on_right_upright"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        if flip:
            self.gravity = "upsidedown"
        else:
            self.gravity = "upright"
        self.animation_name = "on_right" + "_" + self.gravity
        self.speed = 1
        self.next_pos_index = 1

    def loop(self):
        sprites = self.trap[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.pos.x, self.pos.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

    def moving(self, pos_list, vector):
        vector.normalise()
        next_pos_index = self.next_pos_index
        dis_vector = Vector.from_points((0, 0), pos_list[self.next_pos_index]) - self.pos

        if dis_vector.get_magnitude() < self.speed:
            self.pos.x, self.pos.y = pos_list[self.next_pos_index]
            self.next_pos_index = (next_pos_index + 1) % len(pos_list)
        else:
            vector = Vector.from_points((self.pos.x, self.pos.y), pos_list[self.next_pos_index])
            vector.normalise()
            self.pos += vector * self.speed

# dynamic, moving, functional
class Start(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "galleon", 1, False)
        self.start = load_sprite_sheets("items", "stages", width, height, 2)
        self.image = self.start["start"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "start"

    def reset(self):
        self.animation_name = 'start'

    def loop(self):
        sprites = self.start[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


# dynamic, moving, functional, collectable
class Bonus(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height, name):
        super().__init__(x, y, width, height, "bonus", 1, False)
        self.fruit = load_sprite_sheets("items", "bonus", width, height, 2)
        self.name = name
        self.state = self.name
        self.image = self.fruit[self.state][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animating = True

    def reset(self):
        self.animating = True
        self.state = self.name

    def loop(self):
        sprites = self.fruit[self.state]

        if self.animating:
            sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
            self.image = sprites[sprite_index]
            self.animation_count += 1
        else:
            self.image = sprites[-1]

        if self.state == "Collected" and (self.animation_count // self.ANIMATION_DELAY) % len(sprites) >= len(sprites) - 1:
            self.animating = False

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)


# dynamic, moving, functional, collectable
class CheckPoint(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "checkpoint", 1, False)
        self.checkpoint = load_sprite_sheets("items", "stages", width, height, 2)
        self.animation_count = 0
        self.state = "none"
        self.image = self.checkpoint[f"CP({self.state})"][0]
        self.mask = pygame.mask.from_surface(self.image)

    def reset(self):
        self.state = "none"

    def loop(self):
        sprites = self.checkpoint[f"CP({self.state})"]

        if self.state == "none":
            self.animation_count = 0
            self.image = sprites[0]
        else:
            sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
            self.image = sprites[sprite_index]
            self.animation_count += 1

        if self.state == "out" and self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.state = "flag"
            self.animation_count = 0

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)


# dynamic, flip, moving
class Arrow(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height, flip):
        super().__init__(x, y, width, height, "arrow", 2, flip)
        self.arrow = load_sprite_sheets("traps", "arrow", 18, 18,
                                        3, True)
        self.image = self.arrow["Idle_right_upright"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        if flip:
            self.gravity = "upsidedown"
        else:
            self.gravity = "upright"
        self.animation_name = "Idle_right" + "_" + self.gravity

    def loop(self):
        sprites = self.arrow[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


class Button:
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, window):
        window.blit(self.image, (self.rect.x, self.rect.y))

    def pressed(self):
        action = False
        mouse_pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked is False:
                self.clicked = True
                action = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        return action
