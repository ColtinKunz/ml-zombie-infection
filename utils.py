import os
import pickle
import pygame

from random import randint
from math import atan2, degrees, pi


def create_map():
    from map import Map

    return Map()


def closest(base_character, character_list):
    character_list = character_list.copy()
    if base_character in character_list:
        character_list.remove(base_character)
    try:
        closest_character = character_list[0]
    except IndexError:
        return (-10000, -10000)
    for character in character_list:
        if get_character_distance(
            character, base_character
        ) < get_character_distance(closest_character, base_character):
            closest_character = character
    return closest_character.position


def closest_list(
    base_character, character_list, num_closest, return_relative_position=False
):
    # Initialize lists
    character_list = character_list.copy()
    closest_list = [character for character in character_list[0:num_closest]]
    closest_list.sort(
        reverse=True, key=lambda c: get_character_distance(c, base_character)
    )
    if base_character in character_list:
        character_list.remove(base_character)

    for character in character_list:
        if get_character_distance(
            character, base_character
        ) < get_character_distance(
            closest_list[len(closest_list) - 1], base_character
        ):
            closest_list.pop(len(closest_list) - 1)
            closest_list.append(character)
            closest_list.sort(
                reverse=True,
                key=lambda c: get_character_distance(c, base_character),
            )
    # Return only the positions
    closest_pos_list = []
    for c in closest_list:
        if return_relative_position:
            closest_pos_list += list(split_position(c.position))
        else:
            closest_pos_list += list(relative_position(base_character, c))
    while len(closest_pos_list) < num_closest * 2:
        closest_pos_list.append(-10000)
    return closest_pos_list


def relative_position(c1, c2):
    return get_character_distance(c1, c2), pygame.Vector2(c1.vel).angle_to(
        c2.vel
    )


def split_position(pos):
    yield pos[0]
    yield pos[1]


def get_character_distance(c1, c2):
    return (
        pygame.Vector2(c1.position) - pygame.Vector2(c2.position)
    ).magnitude()


def alive_count(character_list):
    count = 0
    for char in character_list:
        if not char.is_dead:
            count += 1
    return count


def get_best_index_list(counter, ge):
    sorted_ge = ge.copy()
    sorted_ge.sort(reverse=True, key=lambda g: g.fitness)
    return [ge.index(g) for g in sorted_ge[0:5]]


def pickle_results(
    num_characters,
    file_name,
    nets,
    best_index_list=None,
):
    with open(os.path.join("pickles", file_name), "wb") as handle:
        if best_index_list is None:
            pickle.dump(
                nets,
                handle,
                protocol=pickle.HIGHEST_PROTOCOL,
            )
        else:
            best_list = []
            best_net = nets.pop(best_index_list[0])
            [
                best_list.append(best_net)
                for i in range(round(num_characters / 2))
            ]
            net = nets.pop(best_index_list[1])
            [best_list.append(net) for i in range(round(num_characters / 4))]
            net = nets.pop(best_index_list[2])
            [best_list.append(net) for i in range(round(num_characters / 8))]
            net = nets.pop(best_index_list[3])
            [best_list.append(net) for i in range(round(num_characters / 16))]
            net = nets.pop(best_index_list[4])
            [best_list.append(net) for i in range(round(num_characters / 32))]
            while num_characters - len(best_list) > 1:
                best_list.append(best_net)
            best_list.append(nets[randint(0, len(nets))])
            pickle.dump(
                best_list,
                handle,
                protocol=pickle.HIGHEST_PROTOCOL,
            )


def load_pickle(num_characters, fitness, file_name):
    with open(os.path.join("pickles", file_name), "rb") as handle:
        return pickle.load(handle), fitness.generate(num_characters)


def spawn(character, position, game_map):
    from main import win_width, win_height

    overlap = game_map.mask.overlap(
        character.get_mask(),
        character.position,
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
            return spawn(character, new_position, game_map)
        except RecursionError:
            return position
    else:
        return position
