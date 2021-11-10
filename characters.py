import os
import pygame

from random import randint, choice

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
        self.tick_count = 0
        self.img = None

        self.position = position
        self.vel = (0, 0)

    def random_move(self):
        self.vel = (
            randint(-self.max_vel, self.max_vel),
            randint(-self.max_vel, self.max_vel),
        )

    def move(self, game_map):
        direction = pygame.Vector2((0, 0)) + pygame.Vector2(self.vel)
        overlap = game_map.mask.overlap(
            self.mask,
            self.position + direction * self.speed,
        )
        if direction != pygame.Vector2(0, 0) and not overlap:
            direction.normalize_ip()
            self.position += direction * self.speed

    def draw(self, win):
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
        self.speed = 1
        self.mask = self.get_mask()


class Citizen(Character):
    """
    Class representing a citizen.
    """

    def __init__(self, position):
        Character.__init__(self, position)
        self.img = citizen_img
        self.mask = self.get_mask()


class Soldier(Character):
    """
    Class representing a soldier.
    """

    def __init__(self, position):
        Character.__init__(self, position)
        self.img = soldier_img
        self.mask = self.get_mask()
        self.distance_measure = 10

    def shoot(self):
        return Bullet(
            self.position,
            (
                choice(
                    [
                        randint(-self.distance_measure, -1),
                        randint(1, self.distance_measure),
                    ]
                ),
                choice(
                    [
                        randint(-self.distance_measure, -1),
                        randint(1, self.distance_measure),
                    ]
                ),
            ),
        )


class Bullet:
    def __init__(self, position, direction):
        self.position = (position.x, position.y)
        self.direction = pygame.Vector2(direction)
        self.speed = 15
        self.radius = 4

        self.surface = pygame.Surface((self.radius * 2, self.radius * 2))
        self.mask = pygame.mask.from_surface(self.surface)

    def move(self, game_map):
        overlap = game_map.mask.overlap(
            self.mask,
            self.position + self.direction * self.speed,
        )
        if self.direction != pygame.Vector2(0, 0) and not overlap:
            self.direction.normalize_ip()
            self.position += self.direction * self.speed
        elif overlap:
            return "out"

    def draw(self, win):
        pygame.draw.circle(
            win, pygame.Color("white"), self.position, self.radius
        )
