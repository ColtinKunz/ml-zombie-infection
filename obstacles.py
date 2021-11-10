import os
import pygame


hard_obs_img = pygame.transform.scale2x(
    pygame.image.load(
        os.path.join("images", "obstacles", "hard.png")
    ).convert_alpha()
)

soft_obs_img = pygame.transform.scale2x(
    pygame.image.load(
        os.path.join("images", "obstacles", "soft.png")
    ).convert_alpha()
)


class Obstacle:
    """
    Class representing an obstacle that can be moved by citizens.
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.img = None


class SoftObstacle(Obstacle):
    """
    Class representing an obstacle that can be moved by citizens and be
    shot through.
    """

    def __init__(self, x, y):
        Obstacle.__init__(self, x, y)
        self.img = soft_obs_img


class HardObstacle(Obstacle):
    """
    Class representing an obstacle that can be moved by citizens and be
    shot through.
    """

    def __init__(self, x, y):
        Obstacle.__init__(self, x, y)
        self.img = hard_obs_img
