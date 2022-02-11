import os
import pygame

map_img = pygame.transform.scale2x(
    pygame.image.load(os.path.join("images", "wall_map.png")).convert_alpha()
)


class Map:
    def __init__(self):
        self.img = map_img
        self.mask = self.create_mask()

    def create_mask(self):
        return pygame.mask.from_surface(self.img)

    def draw(self, win):
        win.blit(self.img, (0, 0))
