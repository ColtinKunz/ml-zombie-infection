import os
import pickle
import pygame
import numpy as np

from random import randint, uniform

from characters import Zombie, Citizen, Soldier


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


def get_best_list(characters, num_best):
    sorted_characters = characters.copy()
    sorted_characters.sort(reverse=True, key=lambda c: c.fitness)
    return [character for character in sorted_characters[0:num_best]]


def format_weights_character(character):
    return {
        "ih": character.w_input_hidden,
        "hh": character.w_hidden_hidden,
        "ho": character.w_hidden_output,
    }


def format_weights(w_input_hidden, w_hidden_hidden, w_hidden_output):
    return {
        "ih": w_input_hidden,
        "hh": w_hidden_hidden,
        "ho": w_hidden_output,
    }


def pickle_results(
    file_name,
    characters,
):
    from main import (
        elitism,
        num_zombies,
        num_citizens,
        num_soldiers,
        mutation_rate,
    )

    if len(characters) == 0:
        return

    # Set number of characters equal to original number of characters.
    num_characters = 0
    if characters[0].character_type == "zombies":
        num_characters = num_zombies
    elif characters[0].character_type == "citizens":
        num_characters = num_citizens
    elif characters[0].character_type == "soldiers":
        num_characters = num_soldiers

    # Set number of characters to keep out of the best performing
    elite_count = round(num_characters * elitism)

    # Sort characters with the best performing first
    characters.sort(reverse=True, key=lambda c: c.fitness)

    # Keep the top performing characters
    elite_characters = characters[0:elite_count]

    new_character_weights = []

    # Append all but one of combined characters
    for i in range(0, num_characters - 1):
        # Grab 2 characters from the elite characters
        c1, c2 = np.random.choice(elite_characters, 2)

        # Perform crossover
        # (how much we choose one character's weights over the other)
        w_input_hidden = (np.random.uniform(0, 1) * c1.w_input_hidden) + (
            (1 - np.random.uniform(0, 1)) * c2.w_input_hidden
        )
        w_hidden_output = (np.random.uniform(0, 1) * c1.w_hidden_output) + (
            (1 - np.random.uniform(0, 1)) * c2.w_hidden_output
        )
        w_hidden_hidden = (np.random.uniform(0, 1) * c1.w_hidden_hidden) + (
            (1 - np.random.uniform(0, 1)) * c2.w_hidden_hidden
        )

        # Clean up weights for creating a new character
        weights = format_weights(
            w_input_hidden, w_hidden_hidden, w_hidden_output
        )

        # Create a new character based on the evolved weights and mutate some
        new_character_weights.append(
            format_weights_character(
                character_setup(c1.character_type, 1, weights=weights)[0]
                if uniform(0, 1) > mutation_rate
                else mutate_weights(
                    character_setup(c1.character_type, 1, weights=weights)[0]
                )
            )
        )

    # Append best character
    new_character_weights.append(
        format_weights_character(
            character_setup(
                c1.character_type,
                1,
                weights=format_weights(
                    c1.w_input_hidden, c1.w_hidden_hidden, c1.w_hidden_output
                ),
            )[0]
        )
    )

    with open(os.path.join("pickles", file_name), "wb") as handle:
        pickle.dump(
            new_character_weights,
            handle,
            protocol=pickle.HIGHEST_PROTOCOL,
        )


def load_pickle(num_characters, character_type, mutate=True):
    with open(
        os.path.join("pickles", f"best_{character_type}.pickle"), "rb"
    ) as handle:
        pickled_weights = pickle.load(handle)
        all_weights = pickled_weights

        characters = []

        while len(characters) < num_characters:
            for weight in all_weights:
                if len(characters) == num_characters:
                    return characters
                characters.append(character_setup(character_type, 1, weight)[0])
        return characters


def mutate_weights(character):
    if np.random.randint(0, 1) == 0:
        # Mutate [input -> hidden] weights.
        w_row = np.random.randint(0, character.num_input_nodes - 1)
        character.w_input_hidden[0][w_row] *= np.random.uniform(0.99, 1.01)
        if character.w_input_hidden[0][w_row] > 1:
            character.w_input_hidden[0][w_row] = 1
        elif character.w_input_hidden[0][w_row] < -1:
            character.w_input_hidden[0][w_row] = -1

    else:
        # Mutate [hidden -> output] weights.
        w_row = np.random.randint(0, character.num_output_nodes - 1)
        character.w_hidden_output[len(character.w_hidden_output) - 1][
            w_row
        ] *= np.random.uniform(0.99, 1.01)
        if (
            character.w_hidden_output[len(character.w_hidden_output) - 1][w_row]
            > 1
        ):
            character.w_hidden_output[len(character.w_hidden_output) - 1][
                w_row
            ] = 1
        if (
            character.w_hidden_output[len(character.w_hidden_output) - 1][w_row]
            < -1
        ):
            character.w_hidden_output[len(character.w_hidden_output) - 1][
                w_row
            ] = -1
    return character


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
    for c in characters:
        c.initial_spawn()
    return characters
