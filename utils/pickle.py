import os
import pickle
import numpy as np

from random import uniform

from main.utils import (
    format_weights_character,
    format_weights,
    mutate_weights,
)


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
