import os
import math
import pygame
import numpy as np

from random import uniform

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

    def __init__(
        self,
        position,
        num_input_nodes,
        num_output_nodes,
        w_input_hidden=None,
        w_hidden_hidden=None,
        w_hidden_output=None,
        initial=False,
    ):
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

        self.fitness = 0

        self.num_input_nodes = num_input_nodes
        self.num_hidden_nodes = 10
        self.num_hidden_layers = 10
        self.num_output_nodes = num_output_nodes

        self.w_input_hidden = w_input_hidden
        self.w_hidden_hidden = w_hidden_hidden
        self.w_hidden_output = w_hidden_output

        # If weights are passed then use those, otherwise generate randomly.
        if self.w_input_hidden is None:
            self.w_input_hidden = np.random.uniform(
                -1, 1, (self.num_hidden_nodes, self.num_input_nodes)
            )
        if self.w_hidden_output is None:
            self.w_hidden_output = np.random.uniform(
                -1, 1, (self.num_output_nodes, self.num_hidden_nodes)
            )
        if self.w_hidden_hidden is None:
            self.w_hidden_hidden = np.random.uniform(
                -1,
                1,
                (
                    self.num_hidden_layers - 2,
                    self.num_hidden_nodes,
                    self.num_hidden_nodes,
                ),
            )

    def move(self, game_map):
        if not self.is_dead:
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

    def initial_spawn(self):
        from main import win_width, win_height

        height = round(win_height * 0.95)
        width = round(win_width * 0.95)

        def elps_axis_calc(x, theta):
            return x ** 2 * math.sin(theta) ** 2

        center_position = (win_width / 2, win_height / 2)

        angle = uniform(0, 360)
        num = height * width
        den = math.sqrt(
            elps_axis_calc(height, angle) + elps_axis_calc(width, angle)
        )

        max_distance_spawn = num / den

        spawn_vector = pygame.Vector2(center_position) + pygame.Vector2(
            uniform(0, max_distance_spawn) * math.cos(angle),
            uniform(0, max_distance_spawn) * math.sin(angle),
        )

        return (spawn_vector.x, spawn_vector.y)

    def spawn(self, new_position):
        from main import win_width, win_height, game_map

        overlap = game_map.mask.overlap(
            self.get_mask(),
            self.position,
        )
        if overlap:
            new_position = (0, 0)
            new_position = (
                new_position[0] + 2
                if new_position[0] > win_width / 2
                else new_position[0] - 2,
                new_position[1],
            )
            new_position = (
                new_position[0],
                new_position[1] + 2
                if new_position[1] > win_height / 2
                else new_position[1] - 2,
            )
            try:
                return self.spawn(new_position)
            except RecursionError:
                return self.position
        else:
            return self.position

    def get_mask(self):
        """
        Grabs mask for the current image of the character.
        """
        return pygame.mask.from_surface(self.img)

    def think(self, inputs):
        # Run MLP.
        def af(x):
            return np.tanh(x.reshape(-1, 1))  # Activation function

        ih = af(np.dot(self.w_input_hidden, np.array(inputs)))  # Hidden layer 1
        h_to_h = False
        for x, hh in enumerate(self.w_hidden_hidden):
            if not h_to_h:
                h = af(np.dot(hh, ih))  # The rest of the hidden layers
                h_to_h = True
            else:
                h = af(np.dot(hh, h))  # The rest of the hidden layers
        return af(np.dot(self.w_hidden_output, h))  # Output layer

    def get_weights(self):
        return (
            self.w_input_hidden,
            self.w_hidden_hidden,
            self.w_hidden_output,
        )


class Zombie(Character):
    """
    Class representing a zombie.
    """

    def __init__(
        self,
        position,
        num_input_nodes,
        num_output_nodes,
        w_input_hidden=None,
        w_hidden_hidden=None,
        w_hidden_output=None,
        initial=False,
    ):
        Character.__init__(self, position, num_input_nodes, num_output_nodes)
        self.img = zombie_img
        self.speed = 3.5
        self.mask = self.get_mask()
        if initial:
            self.position = self.initial_spawn()
        self.position = self.spawn(position)


class Citizen(Character):
    """
    Class representing a citizen.
    """

    def __init__(
        self,
        position,
        num_input_nodes,
        num_output_nodes,
        w_input_hidden=None,
        w_hidden_hidden=None,
        w_hidden_output=None,
        initial=False,
    ):
        Character.__init__(self, position, num_input_nodes, num_output_nodes)
        self.img = citizen_img
        self.mask = self.get_mask()
        if initial:
            self.position = self.initial_spawn()
        self.position = self.spawn(position)


class Soldier(Character):
    """
    Class representing a soldier.
    """

    def __init__(
        self,
        position,
        num_input_nodes,
        num_output_nodes,
        w_input_hidden=None,
        w_hidden_hidden=None,
        w_hidden_output=None,
        initial=False,
    ):
        Character.__init__(self, position, num_input_nodes, num_output_nodes)
        self.img = soldier_img
        self.mask = self.get_mask()
        self.position = self.initial_spawn()
        self.position = self.spawn(position)
        self.distance_measure = 10

        self.reload_count = 0
        self.ticks_to_reload = 60

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
