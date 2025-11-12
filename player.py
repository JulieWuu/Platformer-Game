import pygame

from load_sprite_sheets import load_sprite_sheets


def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object.append(obj)
            break

    player.move(-dx, 0)
    player.update()
    return collided_object


# dynamic, flip, collision, moving, functional
class Player(pygame.sprite.Sprite):
    GRAVITY = 1
    SPRITES = load_sprite_sheets("character", "virtual guy", 32, 32,
                                 1.8, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.vel = [0, 0]
        self.mask = None
        self.direction = "right"
        self.gravity = "upright"
        self.animation_count = 0    # frame inside each animation
        self.fall_count = 0     # frame after falling
        self.jump_count = 0     # jumping state to mark available jumps
        self.count = 0  # frame after jumping
        self.sprite = None
        self.hit = False
        self.hit_count = 0  # frame after hit
        self.wall_slide_left = False
        self.wall_slide_right = False
        self.sprite_sheet = "idle"
        self.gravity_count = 0  # frame after gravity change

    def normal_grav(self):
        self.GRAVITY = 1
        if self.gravity != "upright":
            self.gravity = "upright"

    def anti_grav(self):
        self.GRAVITY = -1
        if self.gravity != "upsidedown":
            self.gravity = "upsidedown"

    def first_jump(self):
        self.vel[1] = -self.GRAVITY * 4
        self.animation_count = 0
        self.fall_count = 0
        self.count = 0
        self.jump_count = 1

    def second_jump(self):
        self.vel[1] = -self.GRAVITY * 5
        self.animation_count = 0
        self.fall_count = 0
        self.count = 0
        self.jump_count = 2

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        if self.vel[0] > 0:
            if self.direction != "right":
                self.direction = "right"
                self.animation_count = 0

        elif self.vel[0] < 0:
            if self.direction != "left":
                self.direction = "left"
                self.animation_count = 0

    def loop(self, fps, game):
        if self.gravity == "upright":
            self.vel[1] += min(2, (self.fall_count / fps) * self.GRAVITY)
        else:
            self.vel[1] += max(-2, (self.fall_count / fps) * self.GRAVITY)

        self.move(0, self.vel[1])

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 1.5:
            self.hit = False
            self.hit_count = 0

        keys = pygame.key.get_pressed()
        if keys[game.keys["right"]]:
            if self.vel[0] <= 0:
                self.vel[0] = 0
            self.vel[0] = min(self.vel[0] + 0.5, 5)
        elif keys[game.keys["left"]]:
            if self.vel[0] >= 0:
                self.vel[0] = 0
            self.vel[0] = max(self.vel[0] - 0.5, -5)

        elif self.vel[0] > 0:
            self.vel[0] = max(self.vel[0] - 0.5, 0)
        elif self.vel[0] < 0:
            self.vel[0] = min(self.vel[0] + 0.5, 0)

        self.fall_count += 1
        self.count += 1
        self.gravity_count += 1
        self.update_sprite(game)

    def landed(self):
        self.fall_count = 0
        self.count = 0
        self.vel[1] = 0
        self.jump_count = 0

    def hit_head(self):
        self.vel[1] = 0

    def update_sprite(self, game):
        keys = pygame.key.get_pressed()

        if self.hit:
            self.sprite_sheet = "hit"
        elif self.vel[1] < 0 if self.GRAVITY == 1 else self.vel[1] > 0:
            if self.jump_count == 1:
                self.sprite_sheet = "jump"
            elif self.jump_count == 2:
                self.sprite_sheet = "double_jump"
        elif self.vel[1] > 2 if self.GRAVITY == 1 else self.vel[1] < -2:
            self.sprite_sheet = "fall"
        elif self.vel[0] != 0 or (self.vel[0] == 0 and (keys[game.keys["left"]] or keys[game.keys["right"]])):
            self.sprite_sheet = "run"
        else:
            self.sprite_sheet = "idle"

        sprite_sheet_name = self.sprite_sheet + "_" + self.direction + "_" + self.gravity
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def reset(self):
        self.rect.x = 200
        self.rect.y = 300
        self.vel = [0, 0]
        self.GRAVITY = 2
        self.direction = "right"
        self.gravity = "upright"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.count = 0
        self.hit = False
        self.hit_count = 0
        self.sprite_sheet = "idle"

    def draw(self, window, offset=(0, 0)):
        window.blit(self.sprite, (self.rect.x - offset[0], self.rect.y - offset[1]))
