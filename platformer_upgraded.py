import sys
import pygame
import time

from load_sprite_sheets import get_background
from tilemap import TileMap
from player import Player
from objects import load_images, load_music, Button, Block, Traps, Function, Arrow, Bonus, Start, CheckPoint
from font import Font
from handle_collision import handle_move, rev_handle_move
from vector import *


pygame.init()
font_B2 = Font('platformer_assets/menu/text/Text_Black.png', 2)
font_B3 = Font('platformer_assets/menu/text/Text_Black.png', 3)
font_B6 = Font('platformer_assets/menu/text/Text_Black.png', 6)
font_B10 = Font('platformer_assets/menu/text/Text_Black.png', 10)
font_R2 = Font('platformer_assets/menu/text/Text_Red.png', 2)
font_R3 = Font('platformer_assets/menu/text/Text_Red.png', 3)
font_R10 = Font('platformer_assets/menu/text/Text_Red.png', 10)


class Game:
    def __init__(self):
        self.width = 1200
        self.height = 576
        self.window = pygame.display.set_mode((self.width, self.height))

        self.clock = pygame.time.Clock()

        self.assets = {'background': load_images('background'),
                       'buttons': load_images('menu/buttons'),
                       'levels': load_images('menu/levels'),
                       'music': load_music('music/sound'),
                       'functions': [],
                       'blocks': [],
                       'animations': [],
                       'start': [],
                       'CP': [],
                       'arrows': [],
                       'bonus': [],
                       }

        self.keys = {"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_SPACE, "ability": pygame.K_w}

        self.player = Player(400, 300, 32, 32)
        self.level = 0
        self.complete = False
        self.tile_map = TileMap(self, tile_size=48)
        self.transition = -30
        self.next_lv = False

        self.platforms = []
        self.saws = []
        self.decode_map()

        self.state = 'run'
        self.start_time = 0
        self.timing = False
        self.scroll = [0, 0]
        self.anti_grav = False

        self.score = 0
        self.lives = 5
        self.invincible = False

        self.music = 1
        self.bgm_vol = 0.5
        self.sound_vol = 0.5

    def decode_map(self):
        self.tile_map.load(f"level_{self.level}.json")

        self.platforms = []
        self.saws = []
        for (i, key) in enumerate(self.assets.keys()):
            if i in range(5, len(self.assets)):
                self.assets[key].clear()

        for platform in self.tile_map.extract([('spawners', 2)], True):
            self.platforms.append(Traps(platform['pos'][0], platform['pos'][1], 32, 7, 'platform', 2, False))
        for saw in self.tile_map.extract([('spawners', 4)], True):
            self.saws.append(Traps(saw['pos'][0], saw['pos'][1], 38, 38, 'saw', 2, False))

        for block in self.tile_map.extract([('blocks', i) for i in range(10)]):
            self.assets['blocks'].append(Block(block['pos'][0], block['pos'][1], 'blocks/' + str(block['variant'] + 1)))
        for brick in self.tile_map.extract([('bricks', i) for i in range(3)]):
            self.assets['blocks'].append(Block(brick['pos'][0], brick['pos'][1], 'bricks/' + str(brick['variant'] + 1)))
        for arrow in self.tile_map.extract([('spawners', 0), ('spawners', 1)]):
            self.assets['arrows'].append(Arrow(arrow['pos'][0], arrow['pos'][1], 18, 18,
                                               True if arrow['variant'] == 1 else False))
        for platform in self.platforms:
            self.assets['animations'].append(platform)
        for saw in self.saws:
            self.assets['animations'].append(saw)
        for spike in self.tile_map.extract([('spawners', 6), ('spawners', 7)]):
            self.assets['animations'].append(Traps(spike['pos'][0], spike['pos'][1], 24, 8, 'spike',
                                                   2, True if spike['variant'] == 7 else False))
        for apple in self.tile_map.extract([('items', 0)]):
            self.assets['bonus'].append(Bonus(apple['pos'][0], apple['pos'][1], 32, 32, "Apple"))
        for gln in self.tile_map.extract([('items', 2)]):
            self.assets['bonus'].append(Bonus(gln['pos'][0], gln['pos'][1], 32, 32, "Galleon"))
        for start in self.tile_map.extract([('items', 3)]):
            self.assets['start'].append(Start(start['pos'][0], start['pos'][1], 64, 64))
        for cp in self.tile_map.extract([('items', 1)]):
            self.assets['CP'].append(CheckPoint(cp['pos'][0], cp['pos'][1], 64, 64))

    def menu(self):
        pygame.display.set_caption("menu")
        get_background(self, self.window, 8)
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.load('platformer_assets/music/BGM/Menu_BGM.mp3')
            pygame.mixer.music.play()

        play_button = Button(self.width / 2 - 105, self.height / 2 - 40, self.assets['buttons'][7], 10)
        settings_button = Button(30, 150, self.assets['buttons'][10], 3)
        key_pos_button = Button(30, 270, self.assets['buttons'][5], 3)
        close_button = Button(self.width - 120, 30, self.assets['buttons'][2], 5)

        play_button.draw(self.window)
        settings_button.draw(self.window)
        key_pos_button.draw(self.window)
        close_button.draw(self.window)

        font_B10.render(self.window, 'MENU', (450, 100))
        font_B3.render(self.window, "SETTINGS", (110, 170))
        font_B3.render(self.window, "KEY POSITIONS", (110, 290))

        while True:
            if play_button.pressed():
                self.run()
            if settings_button.pressed():
                self.settings()
            if key_pos_button.pressed():
                self.key_pos()
            if close_button.pressed():
                pygame.quit()
                sys.exit()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.update()
            self.clock.tick(60)

    def settings(self):
        pygame.display.set_caption('settings')
        pygame.mixer.music.load('platformer_assets/music/BGM/music_0' + str(self.music) + '.mp3')
        pygame.mixer.music.play()
        start_time = time.time()

        vol_bar_x = 250
        vol_bar_y_bgm = 160
        vol_bar_y_sound = 290
        vol_bar_width = 800
        vol_bar_height = 30

        bgm_button_dragging = False
        sound_button_dragging = False

        back_button = Button(30, 30, self.assets['buttons'][1], 5)
        music_button = {"1": Button(330, 380, self.assets['levels'][0], 10),
                        "2": Button(580, 380, self.assets['levels'][1], 10),
                        "3": Button(840, 380, self.assets['levels'][2], 10)}
        bgm_vol_button = Button(self.bgm_vol * vol_bar_width + vol_bar_x, 145, self.assets['buttons'][11], 3)
        sound_vol_button = Button(self.sound_vol * vol_bar_width + vol_bar_x, 275, self.assets['buttons'][11], 3)

        while True:
            get_background(self, self.window, 8)

            bgm_rect = pygame.Rect(vol_bar_x, vol_bar_y_bgm, vol_bar_width, vol_bar_height)
            pygame.draw.rect(self.window, (240, 150, 40), bgm_rect)
            sound_effect_rect = pygame.Rect(vol_bar_x, vol_bar_y_sound, vol_bar_width, vol_bar_height)
            pygame.draw.rect(self.window, (240, 150, 40), sound_effect_rect)

            back_button.draw(self.window)
            for button in music_button:
                if button == str(self.music):
                    cur_time = time.time()
                    if ((cur_time - start_time) // 0.3) % 2 == 0:
                        music_button[button].draw(self.window)
                else:
                    music_button[button].draw(self.window)

            font_B6.render(self.window, 'SETTINGS', (480, 60))
            font_B3.render(self.window, 'BGM', (90, 170))
            font_B3.render(self.window, 'SOUND', (80, 280))
            font_B3.render(self.window, 'EFFECT', (70, 330))
            font_B3.render(self.window, 'BGM MUSIC', (60, 450))

            m_pos = pygame.mouse.get_pos()
            if back_button.pressed():
                pygame.mixer.music.stop()
                self.menu()

            for event in pygame.event.get():
                if bgm_vol_button.pressed():
                    bgm_button_dragging = True
                elif sound_vol_button.pressed():
                    sound_button_dragging = True
                if event.type == pygame.MOUSEBUTTONUP:
                    bgm_button_dragging = False
                    sound_button_dragging = False

                for music in music_button:
                    if music_button[music].pressed():
                        self.music = int(music)
                        pygame.mixer.music.load(f"platformer_assets/music/BGM/music_0{self.music}.mp3")
                        pygame.mixer.music.play()

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            if bgm_button_dragging:
                bgm_vol_button = Button(max(min(m_pos[0] - 63 / 2, vol_bar_x + vol_bar_width - 66), vol_bar_x),
                                        145, self.assets['buttons'][11], 3)

                self.bgm_vol = (bgm_vol_button.rect.x - vol_bar_x) / vol_bar_width
                pygame.mixer.music.set_volume(self.bgm_vol)
                bgm_vol_button.draw(self.window)

            if sound_button_dragging:
                sound_vol_button = Button(max(min(m_pos[0] - 63 / 2, vol_bar_x + vol_bar_width - 66), vol_bar_x),
                                          275, self.assets['buttons'][11], 3)

                self.sound_vol = (sound_vol_button.rect.x - vol_bar_x) / vol_bar_width
                self.assets['music'][0].set_volume(self.sound_vol * 0.4)
                self.assets['music'][1].set_volume(self.sound_vol * 0.5)
                self.assets['music'][2].set_volume(self.sound_vol * 1.0)
                self.assets['music'][3].set_volume(self.sound_vol * 0.4)
                self.assets['music'][4].set_volume(self.sound_vol * 0.4)
                self.assets['music'][5].set_volume(self.sound_vol * 2.0)

                sound_vol_button.draw(self.window)

            bgm_vol_button.draw(self.window)
            sound_vol_button.draw(self.window)

            pygame.display.update()
            self.clock.tick(60)

    def key_pos(self):
        pygame.display.set_caption("key_pos")
        start_time = time.time()
        back_button = Button(30, 30, self.assets['buttons'][1], 5)

        # first value for editing, second value for confronting
        states = {"left": [False, False], "right": [False, False], "jump": [False, False], "ability": [False, False]}
        rects = {"left": pygame.Rect((260, 200), (260, 50)),
                 "right": pygame.Rect((810, 200), (260, 50)),
                 "jump": pygame.Rect((260, 360), (260, 50)),
                 "ability": pygame.Rect((890, 360), (260, 50))
                 }
        text_pos = {"left": (280, 215), "right": (830, 215), "jump": (280, 375), "ability": (910, 375)}

        while True:
            get_background(self, self.window, 8)
            back_button.draw(self.window)
            for rect in rects.values():
                pygame.draw.rect(self.window, (100, 100, 100), rect, 3)

            if back_button.pressed():
                confront = []
                for option in states:
                    confront.append(not states[option][1])
                if all(confront):
                    self.menu()

            for option in states:
                key_copy = self.keys.copy()
                del key_copy[option]
                if self.keys[option] not in key_copy.values():
                    states[option][1] = False

            font_B3.render(self.window, "CLICK BOXES TO CHANGE PREFERRED KEY POSITIONS", (140, 70))
            font_B6.render(self.window, "LEFT:", (40, 200))
            font_B6.render(self.window, "RIGHT:", (550, 200))
            font_B6.render(self.window, "JUMP:", (40, 360))
            font_B6.render(self.window, "ABILITY:", (550, 360))

            for option in states:
                if not states[option][0]:
                    font_R3.render(self.window, pygame.key.name(self.keys[option]).upper(), text_pos[option])
                else:
                    cur_time = time.time()
                    if ((cur_time - start_time) // 0.4) % 2 == 0:
                        font_R3.render(self.window, pygame.key.name(self.keys[option]).upper(), text_pos[option])
                if states[option][1]:
                    font_B2.render(self.window, "THIS KEY IS ALREADY ASSIGNED", (rects[option].x - 100, rects[option].y + 60))

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for option in rects:
                        if rects[option].collidepoint(pygame.mouse.get_pos()):
                            states[option][0] = True
                            others = list(rects).copy()
                            others.remove(option)
                            for other in others:
                                states[other][0] = False

                for option in states:
                    if states[option][0]:
                        if event.type == pygame.KEYDOWN:
                            key_copy = self.keys.copy()
                            del key_copy[option]
                            if event.key in key_copy.values():
                                states[option][1] = True
                            else:
                                states[option][1] = False
                            self.keys[option] = event.key
                            states[option][0] = False

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.update()
            self.clock.tick(60)

    def window_update(self, window, background, hearts, elp_time, offset=(0, 0)):
        get_background(self, window, background)

        for block in self.assets['blocks']:
            block.draw(window, offset)

        for animator in self.assets['animations']:
            animator.draw(window, offset)
            animator.loop()

        for start in self.assets['start']:
            start.draw(window, offset)
            start.loop()

        for cp in self.assets['CP']:
            cp.draw(window, offset)
            cp.loop()

        for arrow in self.assets['arrows']:
            arrow.draw(window, offset)
            arrow.loop()

        for function in self.assets['functions']:
            function.draw(window)

        for bonus in self.assets['bonus']:
            bonus.draw(window, offset)
            bonus.loop()

        for i, saw in enumerate(self.saws):
            vector_saw = Vector.from_points(self.tile_map.saws["start"][i]['pos'], self.tile_map.saws["end"][i]['pos'])
            pos_list = [self.tile_map.saws["start"][i]['pos'], self.tile_map.saws["end"][i]['pos']]
            saw.moving(pos_list, vector_saw)

        for i, platform in enumerate(self.platforms):
            vector_platform = Vector.from_points(self.tile_map.platforms["start"][i]['pos'],
                                                 self.tile_map.platforms["end"][i]['pos'])
            pos_list = [self.tile_map.platforms["start"][i]['pos'], self.tile_map.platforms["end"][i]['pos']]
            platform.moving(pos_list, vector_platform)

        if self.level == 0:
            font_B2.render(window, "YOU CAN CUSTOMISE KEYBOARD POSITIONS IN MENU - KEY POSITIONS", (200 - offset[0], 180 - offset[1]))
            font_B2.render(window, "BY DEFAULT: A FOR LEFT,", (250 - offset[0], 230 - offset[1]))
            font_B2.render(window, "D FOR RIGHT, SPACE FOR JUMP", (250 - offset[0], 280 - offset[1]))
            font_R2.render(window, "SPIKES ARE DANGEROUS!", (780 - offset[0], 330 - offset[1]))
            font_B2.render(window, "TIME YOUR DOUBLE JUMPS WELL", (900 - offset[0], 260 - offset[1]))
            font_B2.render(window, "USE THE PLATFORM", (1180 - offset[0], 210 - offset[1]))
            font_R2.render(window, "BE CAREFUL OF", (1080 - offset[0], -140 - offset[1]))
            font_R2.render(window, "THE SAWS AHEAD!", (1130 - offset[0], -110 - offset[1]))
            font_B2.render(window, "PRESS W BY DEFAULT TO", (650 - offset[0], -360 - offset[1]))
            font_B2.render(window, "ACTIVATE ANTI-GRAVITY ABILITY", (630 - offset[0], -330 - offset[1]))
            font_B2.render(window, "YOU CAN ONLY USE THE ABILITY ONCE EVERY TWO SECONDS!", (430 - offset[0], -230 - offset[1]))
            font_R2.render(window, "GALLEONS GET YOU HIGHER SCORE", (0 - offset[0], -370 - offset[1]))
            font_R2.render(window, "AND APPLES GET YOU MORE LIVES", (-50 - offset[0], -180 - offset[1]))
            font_B2.render(window, "TRUST THE ARROWS", (-230 - offset[0], -260 - offset[1]))
            font_B2.render(window, "DON'T FORGET TO", (-260 - offset[0], 750 - offset[1]))
            font_B2.render(window, "TOUCH THE FLAG AT THE END!", (-350 - offset[0], 790 - offset[1]))
            font_B2.render(window, "THANKS FOR COMPLETING THE TUTORIAL:)", (20 - offset[0], -700 - offset[1]))
            font_B2.render(window, "CONGRATULATIONS ON FINDING A HIDDEN APPLE!", (500 - offset[0], 700 - offset[1]))

        if self.level == 1:
            font_B2.render(window, "NOW THAT YOU'VE COMPLETED THE TUTORIAL...", (140 - offset[0], 180 - offset[1]))
            font_B2.render(window, "IT'S TIME TO CHALLENGE YOUR ABILITY!", (840 - offset[0], 180 - offset[1]))
            font_B2.render(window, "HAVE FUN :)", (1460 - offset[0], 270 - offset[1]))
            font_B3.render(window, "YOU WON!!", (-2920 - offset[0], -1600 - offset[1]))

        if self.complete and self.level == 0:
            font_R3.render(window, "PRESS ENTER TO THE REAL LEVEL", (300, 500))

        self.player.draw(window, offset)

        for hrt in hearts:
            hrt.draw(window)
        if self.invincible:
            font_B6.render(window, "∞", (90, 95))

        minute = elp_time // 60
        font_B3.render(window, f"{round(minute)}MIN " + f"{(float(f'{elp_time:.1f}') - 60 * round(minute)):.1f}" + "S", (120, 20))
        font_B3.render(window, "SCORE: " + str(self.score), (120, 60))

    def dead(self, player):
        player.GRAVITY = 0

        font_B6.render(self.window, 'UR DEAD', (400, 200))
        font_B3.render(self.window, 'PRESS R TO RESTART', (100, 400))
        font_B3.render(self.window, 'PRESS B TO MENU', (100, 450))
        pygame.display.update()

    def restart(self, player):
        player.reset()
        self.state = 'run'
        self.start_time = time.time()
        self.timing = False
        self.anti_grav = False
        self.score = 0
        self.lives = 5
        self.invincible = False
        self.complete = False
        self.transition = -30
        self.next_lv = False
        self.assets['music'][5].play()
        for cp in self.assets['CP']:
            cp.reset()
        for i, saw in enumerate(self.saws):
            saw.pos.x, saw.pos.y = self.tile_map.saws["start"][i]['pos']
            saw.next_pos_index = 1
        for i, platform in enumerate(self.platforms):
            platform.pos.x, platform.pos.y = self.tile_map.platforms["start"][i]['pos']
            platform.next_pos_index = 1

        for bonus in self.assets['bonus']:
            if bonus.state == "Collected":
                bonus.state = bonus.name
                bonus.animating = True

    def run(self):
        pygame.display.set_caption('run')
        get_background(self, self.window, 5)
        pygame.mixer.music.load('platformer_assets/music/BGM/music_0' + str(self.music) + '.mp3')
        pygame.mixer.music.play(loops=-1)

        self.restart(self.player)
        elapsed_time = 0

        back_button = Button(30, 15, self.assets['buttons'][1], 4)
        restart_button = Button(1120, 15, self.assets['buttons'][9], 3)

        back_button.draw(self.window)
        restart_button.draw(self.window)

        self.assets['functions'].append(Function(30, 15, "Back", 4))
        self.assets['functions'].append(Function(1120, 15, "Restart", 3))

        while True:
            if self.timing:
                elapsed_time = time.time() - self.start_time
            if self.invincible:
                heart = [Function(30, 100, "Heart", 2)]
            else:
                heart = [Function(30 + i * 50, 100, "Heart", 2) for i in range(0, self.lives)]

            colliders = [*self.assets['blocks'], *self.assets['animations']]

            if back_button.pressed():
                pygame.mixer.music.stop()
                self.menu()
            if restart_button.pressed():
                self.restart(self.player)
                elapsed_time = 0

            if self.next_lv:
                self.transition += 1
                if self.transition > 30:
                    if self.complete:
                        self.level += 1
                    try:
                        self.decode_map()
                        elapsed_time = 0
                        self.restart(self.player)
                    except FileNotFoundError:
                        pass
            if self.transition < 0 and not self.next_lv:
                self.transition += 1

            if self.state == 'run':
                for bonus in self.assets['bonus']:
                    if self.player.rect.colliderect(bonus) and bonus.state != "Collected":
                        bonus.state = "Collected"
                        bonus.animation_count = 0
                        if bonus.name == "Apple" and self.lives < 15:
                            self.lives += 1
                        elif bonus.name == "Apple":
                            self.score += 1000
                        elif bonus.name == "Galleon":
                            self.score += 50
                if self.lives >= 15:
                    self.invincible = True

                for start in self.assets['start']:
                    if self.player.rect.colliderect(start) and not self.timing:
                        self.start_time = time.time()
                        self.timing = True

                for cp in self.assets['CP']:
                    if self.player.rect.colliderect(cp):
                        self.timing = False
                        self.complete = True
                        if cp.state == "none":
                            cp.state = "out"

                if self.anti_grav:
                    self.player.anti_grav()
                    rev_handle_move(self.player, colliders, self)
                    self.player.loop(60, self)
                else:
                    self.player.normal_grav()
                    self.player.loop(60, self)
                    handle_move(self.player, colliders, self)

                self.scroll[0] += (self.player.rect.centerx - self.width / 2 - self.scroll[0]) / 5
                self.scroll[1] += (self.player.rect.centery - self.height / 2 - self.scroll[1]) / 5
                render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

                if self.player.rect.y >= 10000 or self.player.rect.y <= -10000:
                    self.state = 'dead'
                    self.assets['music'][0].play()

                if self.lives <= 0:
                    self.lives = 0
                    heart = [Function(30 + i * 50, 90, "Heart", 2) for i in range(0, self.lives)]
                    self.window_update(self.window, 5, heart, elapsed_time, self.scroll)
                    self.state = 'dead'
                    self.assets['music'][0].play()

                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN and self.complete:
                            self.next_lv = True
                        if event.key == self.keys["ability"] and self.player.gravity_count > 120:
                            self.anti_grav = not self.anti_grav
                            self.player.gravity_count = 0

                        if not self.anti_grav:
                            if event.key == self.keys["jump"] and (self.player.jump_count == 1 or (self.player.jump_count == 0 and self.player.vel[1] > 2)):
                                self.player.second_jump()
                                self.assets['music'][3].play()

                            if event.key == self.keys["jump"] and self.player.jump_count == 0:
                                self.player.first_jump()
                                self.assets['music'][3].play()

                        elif self.anti_grav:
                            if event.key == self.keys["jump"] and (self.player.jump_count == 1 or (self.player.jump_count == 0 and self.player.vel[1] < -2)):
                                self.player.second_jump()
                                self.assets['music'][3].play()
                            elif event.key == self.keys["jump"] and self.player.jump_count == 0:
                                self.player.first_jump()
                                self.assets['music'][3].play()

                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                self.window_update(self.window, 5, heart, elapsed_time, render_scroll)

                if self.transition:
                    transition_surf = pygame.Surface((self.width, self.height))
                    pygame.draw.circle(transition_surf, (255, 255, 255), (self.width // 2, self.height // 2), (30 - abs(self.transition)) * 24)
                    transition_surf.set_colorkey((255, 255, 255))
                    self.window.blit(transition_surf, (0, 0))
                print(self.transition)
                pygame.display.update()
                self.clock.tick(60)

            elif self.state == 'dead':
                self.player.GRAVITY = 0
                font_R10.render(self.window, 'UR DEAD', (400, 200))
                font_R3.render(self.window, 'PRESS R TO RESTART', (430, 400))
                font_R3.render(self.window, 'PRESS B TO MENU', (450, 450))

                if back_button.pressed():
                    self.menu()
                if restart_button.pressed():
                    self.next_lv = True

                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self.next_lv = True
                        if event.key == pygame.K_b:
                            self.menu()
                        if event.key == pygame.K_RETURN and self.complete:
                            self.next_lv = True
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                if self.transition:
                    transition_surf = pygame.Surface((self.width, self.height))
                    pygame.draw.circle(transition_surf, (255, 255, 255), (self.width // 2, self.height // 2), (30 - abs(self.transition)) * 24)
                    transition_surf.set_colorkey((255, 255, 255))
                    self.window.blit(transition_surf, (0, 0))

                pygame.display.update()
                self.clock.tick(60)


Game().menu()
