import pygame

from random import randint

from characters import Zombie, Citizen, Soldier


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
    if len(character_list) == 0 or num_closest == 0:
        return []

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


def respawn(character):
    character.position = character.initial_spawn()
    return character


def character_setup(
    character_type,
    num_characters,
    weights=None,
):
    from main import win_width, win_height, num_input_nodes

    ih_weights = weights["ih"] if weights is not None else None
    hh_weights = weights["hh"] if weights is not None else None
    ho_weights = weights["ho"] if weights is not None else None

    if character_type == "zombies":
        characters = [
            Zombie(
                (randint(0, win_width), randint(0, win_height)),
                num_input_nodes,
                2,
                w_input_hidden=ih_weights,
                w_hidden_hidden=hh_weights,
                w_hidden_output=ho_weights,
                initial=True,
            )
            for _ in range(0, num_characters)
        ]
    elif character_type == "citizens":
        characters = [
            Citizen(
                (randint(0, win_width), randint(0, win_height)),
                num_input_nodes,
                2,
                w_input_hidden=ih_weights,
                w_hidden_hidden=hh_weights,
                w_hidden_output=ho_weights,
                initial=True,
            )
            for _ in range(0, num_characters)
        ]
    elif character_type == "soldiers":
        characters = [
            Soldier(
                (randint(0, win_width), randint(0, win_height)),
                num_input_nodes,
                5,
                w_input_hidden=ih_weights,
                w_hidden_hidden=hh_weights,
                w_hidden_output=ho_weights,
                initial=True,
            )
            for _ in range(0, num_characters)
        ]
    return characters
