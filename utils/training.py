import numpy as np

from .characters import character_setup


def get_best_list(characters, num_best):
    sorted_characters = characters.copy()
    sorted_characters.sort(reverse=True, key=lambda c: c.fitness)
    return [character for character in sorted_characters[0:num_best]]


def format_weights_character(character):
    return {
        "W": character.W,
    }


def mutate_weights(W):
    W = [w * np.random.normal(1, 0.05, w.shape) for w in W]
    squash = np.vectorize(lambda x: max(min(x, 1), -1))
    W = [squash(w) for w in W]
    for w in W:
        assert (abs(w) <= 1).all(), "Values in W outside the range of [-1, 1]"
    return W


def create_next_gen(chars, strategy, mutation_rate, **kwargs):
    W_new = strategy(chars, **kwargs)
    new_char_weights = []
    char_type = chars[0].character_type

    for i, W in enumerate(W_new):
        if np.random.rand() < mutation_rate:
            W_new[i] = mutate_weights(W)
        W_new_char = format_weights_character(
            character_setup(char_type, 1, weights=W)[0]
        )
        new_char_weights.append(W_new_char)

    return new_char_weights


def fit_prop(chars, log_scale=False):
    N = len(chars)
    fit_vector = [c.fitness for c in chars]

    if log_scale is True:
        fit_vector = [np.log(val + 1) + 1 for val in fit_vector]

    total_fit = sum(fit_vector)

    try:
        norm_fit = [fit_val / total_fit for fit_val in fit_vector]
    except ZeroDivisionError:
        print("Divide by zero error! Using fitness = 1/N for everyone.")
        norm_fit = np.repeat(1 / N, repeats=N)

    W_new = []
    for _ in range(N):
        c1, c2 = np.random.choice(chars, 2, replace=False, p=norm_fit)
        W_new.append(crossover(c1, c2))
    return W_new


def crossover(c1, c2):
    crossover_weight = np.random.uniform(0, 1)
    return (crossover_weight * c1.W) + ((1 - crossover_weight) * c2.W)
