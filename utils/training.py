import numpy as np


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
