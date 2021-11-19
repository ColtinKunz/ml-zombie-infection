import pygame


def closest(base_character, character_list):
    character_list = character_list.copy()
    if base_character in character_list:
        character_list.remove(base_character)
    try:
        closest_character = character_list[0]
    except IndexError:
        return (-1000, -1000)
    for character in character_list:
        if (
            pygame.Vector2(character.position)
            - pygame.Vector2(base_character.position)
        ).magnitude() < (
            pygame.Vector2(closest_character.position)
            - pygame.Vector2(base_character.position)
        ).magnitude():
            if not character.is_dead:
                closest_character = character
    if closest_character.is_dead:
        return closest(base_character, character_list)
    else:
        return closest_character.position


def alive_count(character_list):
    count = 0
    for char in character_list:
        if not char.is_dead:
            count += 1
    return count


def get_best_index(counter, ge):
    best_index = 0
    for i, g in enumerate(ge):
        if counter == 0 and g.fitness > ge[best_index].fitness:
            best_index = i
        elif (counter == 1 or counter == 2) and g.fitness < ge[
            best_index
        ].fitness:
            best_index = i
    return best_index
