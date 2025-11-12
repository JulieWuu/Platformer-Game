import pygame

from player import collide


def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy < 0 and (player.jump_count == 0 or player.count >= 5):
                player.rect.top = obj.rect.bottom
                player.hit_head()

            else:
                player.rect.bottom = obj.rect.top
                player.landed()

            collided_objects.append(obj)

    return collided_objects


def handle_move(player, objects, game):
    keys = pygame.key.get_pressed()

    collide_left = collide(player, objects, -10)
    collide_right = collide(player, objects, 10)
    horizontal_check = [*collide_left, *collide_right]
    vertical_collide = handle_vertical_collision(player, objects, player.vel[1])
    vertical_check = [*vertical_collide]

    if keys[game.keys["left"]] and not collide_left and not keys[game.keys["right"]]:
        player.move(player.vel[0] * 0.8, 0)
    if keys[game.keys["right"]] and not collide_right and not keys[game.keys["left"]]:
        player.move(player.vel[0] * 0.8, 0)

    for obj in vertical_check:
        if obj and (obj.name == "spike" or obj.name == "saw") and player.hit_count == 0:
            player.hit = True
            if not game.invincible:
                game.lives -= 1
            game.score -= 1
            game.assets['music'][2].play()
            break

    for obj in horizontal_check:
        if obj and obj.name == "block":
            player.vel[1] = 0


def rev_handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0 and (player.jump_count == 0 or player.count >= 5):
                player.rect.bottom = obj.rect.top
                player.hit_head()
            else:
                player.rect.top = obj.rect.bottom
                player.landed()

            collided_objects.append(obj)

    return collided_objects


def rev_handle_move(player, objects, game):
    keys = pygame.key.get_pressed()

    collide_left = collide(player, objects, -10)
    collide_right = collide(player, objects, 10)
    horizontal_check = [*collide_left, *collide_right]
    vertical_collide = rev_handle_vertical_collision(player, objects, player.vel[1])
    vertical_check = [*vertical_collide]

    if keys[game.keys["left"]] and not collide_left and not keys[game.keys["right"]]:
        player.move(player.vel[0], 0)
    if keys[game.keys["right"]] and not collide_right and not keys[game.keys["left"]]:
        player.move(player.vel[0], 0)

    for obj in vertical_check:
        if obj and (obj.name == "spike" or obj.name == "saw") and player.hit_count == 0:
            player.hit = True
            if not game.invincible:
                game.lives -= 1
            game.score -= 1
            game.assets['music'][2].play()
            break

    for obj in horizontal_check:
        if obj and obj.name == "block":
            player.vel[1] = 0
