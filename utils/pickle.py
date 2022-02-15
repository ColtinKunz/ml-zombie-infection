import os
import pickle

from .training import create_next_gen


def pickle_results(
    file_name,
    characters,
):
    from utils import fit_prop

    if len(characters) == 0:
        return

    new_character_weights = create_next_gen(
        characters,
        fit_prop,
        mutation_rate=0.1,
        log_scale=False,
    )

    with open(os.path.join("pickles", file_name), "wb") as handle:
        pickle.dump(
            new_character_weights,
            handle,
            protocol=pickle.HIGHEST_PROTOCOL,
        )


def load_pickle(num_characters, character_type, mutate=True):
    from utils import character_setup

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
