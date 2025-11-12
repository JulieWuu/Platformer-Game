import pygame
pygame.init()


def clip(surf, x, y, x_size, y_size):
    handle_surf = surf.copy()
    clip_rect = pygame.Rect(x, y, x_size, y_size)
    handle_surf.set_clip(clip_rect)
    image = surf.subsurface(handle_surf.get_clip())
    return image.copy()


def colouring(image, start_clr, end_clr):
    for i in range(image.get_width()):
        for j in range(image.get_height()):
            if image.get_at((i, j)) == start_clr:
                image.set_at((i, j), end_clr)
    return image


class Font:
    def __init__(self, path, scale, colour=(0, 0, 0)):
        self.spacing = 2 * scale
        self.characters = {}
        self.character_order = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', ',', ':', '?', '!', '(', ')', '+', '-', '"', '"', ' ', '[', ']', '=', '-', '/', "\\", "'", "'", ";", "~", "#", "%", "£", "*", "^", "`", "∞"]
        self.space_width = 6
        self.colour = pygame.Color(colour)

        font_image = pygame.image.load(path).convert()
        font_image.set_colorkey((255, 255, 255))
        font_img = colouring(font_image, pygame.Color(0, 0, 0), self.colour)

        current_char_width = 0
        character_count = 0
        for x in range(font_img.get_width()):
            c = font_img.get_at((x, 0))
            if c[0] == 127:
                char_img = clip(font_img, x - current_char_width, 0, current_char_width, font_img.get_height())
                self.characters[self.character_order[character_count]] = (
                    pygame.transform.scale(char_img, (char_img.get_width() * scale, char_img.get_height() * scale)))
                character_count += 1
                current_char_width = 0
            else:
                current_char_width += 1

    def render(self, surf, text, loc):
        offset_x = 0
        for char in text:
            if char != ' ':
                surf.blit(self.characters[char], (loc[0] + offset_x, loc[1]))
                offset_x += self.characters[char].get_width() + self.spacing
            else:
                offset_x += self.space_width + self.spacing
