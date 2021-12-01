import os
import pygame

from random import randint

from main import game_map
from utils import spawn

citizen_img = pygame.transform.scale2x(
    pygame.image.load(
        os.path.join("images", "characters", "citizen.png")
    ).convert_alpha()
)

soldier_img = pygame.transform.scale2x(
    pygame.image.load(
        os.path.join("images", "characters", "soldier.png")
    ).convert_alpha()
)

zombie_img = pygame.transform.scale2x(
    pygame.image.load(
        os.path.join("images", "characters", "zombie.png")
    ).convert_alpha()
)


class Character:
    """
    Class representing the base of any character.
    """

    def __init__(self, position):
        """
        Initialize the object
        :param x: starting x pos (int)
        :param y: starting y pos (int)
        :return: None
        """

        self.max_vel = 5
        self.speed = 3
        self.img = None
        self.is_dead = False

        self.position = position
        self.vel = (0, 0)

    def random_move(self):
        self.vel = (
            randint(-self.max_vel, self.max_vel),
            randint(-self.max_vel, self.max_vel),
        )

    def move(self, game_map):
        if not self.is_dead:
            # if self.vel[0] > 1:
            #     self.vel = (1, self.vel[1])
            # elif self.vel[0] < -1:
            #     self.vel = (-1, self.vel[1])
            # if self.vel[1] > 1:
            #     self.vel = (self.vel[0], 1)
            # elif self.vel[1] < -1:
            #     self.vel = (self.vel[0], -1)
            direction = pygame.Vector2((0, 0)) + pygame.Vector2(self.vel)
            overlap = game_map.mask.overlap(
                self.mask,
                self.position + direction * self.speed,
            )
            if overlap:
                x_direction = pygame.Vector2((self.vel[0], 0))
                x_overlap = game_map.mask.overlap(
                    self.mask,
                    self.position
                    + pygame.Vector2((0, 0))
                    + x_direction * self.speed,
                )
                y_direction = pygame.Vector2((0, self.vel[1]))
                y_overlap = game_map.mask.overlap(
                    self.mask,
                    self.position
                    + pygame.Vector2((0, 0))
                    + y_direction * self.speed,
                )
                if not x_overlap:
                    direction = pygame.Vector2((0, 0)) + x_direction
                elif not y_overlap:
                    direction = pygame.Vector2((0, 0)) + y_direction
                else:
                    return
        if direction != pygame.Vector2(0, 0):
            direction.normalize_ip()
            self.position += direction * self.speed

    def draw(self, win):
        if self.is_dead:
            dead_image = self.img.copy().convert_alpha()
            dead_image.set_alpha(33)
            win.blit(
                dead_image,
                self.position,
            )
        else:
            win.blit(self.img, self.position)

    def get_mask(self):
        """
        Grabs mask for the current image of the character.
        """
        return pygame.mask.from_surface(self.img)


class Zombie(Character):
    """
    Class representing a zombie.
    """

    def __init__(self, position):
        Character.__init__(self, position)
        self.img = zombie_img
        self.speed = 3.5
        self.mask = self.get_mask()
        self.position = spawn(self, position, game_map)


class Citizen(Character):
    """
    Class representing a citizen.
    """

    def __init__(self, position):
        Character.__init__(self, position)
        self.img = citizen_img
        self.mask = self.get_mask()
        self.position = spawn(self, position, game_map)


class Soldier(Character):
    """
    Class representing a soldier.
    """

    def __init__(self, position):
        Character.__init__(self, position)
        self.img = soldier_img
        self.mask = self.get_mask()
        self.position = spawn(self, position, game_map)
        self.distance_measure = 10

        self.reload_count = 0
        self.secs_to_reload = 0.1

    def shoot(self, x, y):
        self.reload_count = 0
        return Bullet(
            self.position,
            (
                x,
                y,
            ),
            self,
        )


class Bullet:
    def __init__(self, position, direction, soldier):
        self.position = (position[0], position[1])
        self.direction = pygame.Vector2(direction)
        self.soldier = soldier
        self.speed = 15
        self.radius = 4

        self.surface = pygame.Surface((self.radius * 2, self.radius * 2))
        self.mask = pygame.mask.from_surface(self.surface)

    def move(self, game_map):
        overlap = game_map.mask.overlap(self.mask, self.position)
        if self.direction != pygame.Vector2(0, 0) and not overlap:
            self.direction.normalize_ip()
            self.position += self.direction * self.speed
        elif overlap:
            return "out"

    def draw(self, win):
        pygame.draw.circle(
            win, pygame.Color("white"), self.position, self.radius
        )
