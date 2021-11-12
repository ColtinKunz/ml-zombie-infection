import os
import pickle
import pygame
import fitness

from random import randint


pygame.font.init()
win_width = 512
win_height = 512
stat_font = pygame.font.SysFont("comicsans", 50)
end_font = pygame.font.SysFont("comicsans", 70)
draw_lines = False
fps = 30
generations = 90

win = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption("Infection")

bg_img = pygame.transform.scale2x(
    pygame.image.load(os.path.join("images", "bg.png")).convert_alpha()
)


num_zombies = 50
num_citizens = 40
num_soldiers = 10

gen = 0


def draw_window(win, game_map, zombies, soldiers, citizens, bullets):
    """
    draws the windows for the main game loop
    :param win: pygame window surface
    :return: None
    """
    win.blit(bg_img, (0, 0))
    game_map.draw(win)

    pygame.Surface((win_width, win_height), masks=game_map.mask)

    for zombie in zombies:
        zombie.draw(win)
    for soldier in soldiers:
        soldier.draw(win)
    for citizen in citizens:
        citizen.draw(win)
    for bullet in bullets:
        bullet.draw(win)
    pygame.display.update()


def main():
    clock = pygame.time.Clock()
    run = True

    from characters import Zombie, Soldier, Citizen
    from map import Map

    game_map = Map()

    characters = []
    bullets = []

    if gen > 0:
        for gen_num in range(generations):
            counter = gen_num % 3
            # 0 = Zombies
            # 1 = Citizens
            # 2 = Soldiers
            if counter == 0:
                zombies = []
                with open(
                    os.path.join("pickles", "best_citizens.pickle"), "rb"
                ) as c_handle:
                    citizens = pickle.load(c_handle)
                with open(
                    os.path.join("pickles", "best_soldiers.pickle"), "rb"
                ) as s_handle:
                    soldiers = pickle.load(s_handle)
            elif counter == 1:
                with open(
                    os.path.join("pickles", "best_zombies.pickle"), "rb"
                ) as z_handle:
                    zombies = pickle.load(z_handle)
                citizens, ge = fitness.citizens.fitness.setup()
                with open(
                    os.path.join("pickles", "best_soldiers.pickle"), "rb"
                ) as s_handle:
                    soldiers = pickle.load(s_handle)
            elif counter == 2:
                with open(
                    os.path.join("pickles", "best_zombies.pickle"), "rb"
                ) as z_handle:
                    zombies = pickle.load(z_handle)
                with open(
                    os.path.join("pickles", "best_citizens.pickle"), "rb"
                ) as c_handle:
                    citizens = pickle.load(c_handle)
                soldiers = []
    elif gen == 0:
        zombies = []
        citizens = []
        soldiers = []
        for i in range(num_zombies):
            characters.append(Zombie((randint(9, 490), randint(9, 490))))
        for i in range(num_citizens):
            characters.append(Citizen((randint(9, 490), randint(9, 490))))
        for i in range(num_soldiers):
            characters.append(Soldier((randint(9, 490), randint(9, 490))))
        with open(
            os.path.join("pickles", "best_zombie.pickle"), "wb"
        ) as z_handle:
            pickle.dump(zombies, z_handle, protocol=pickle.HIGHEST_PROTOCOL)
        with open(
            os.path.join("pickles", "best_citizens.pickle"), "wb"
        ) as c_handle:
            pickle.dump(citizens, c_handle, protocol=pickle.HIGHEST_PROTOCOL)
        with open(
            os.path.join("pickles", "best_soldiers.pickle"), "wb"
        ) as s_handle:
            pickle.dump(soldiers, s_handle, protocol=pickle.HIGHEST_PROTOCOL)

    for z in zombies:
        characters.append(z)
    for c in citizens:
        characters.append(c)
    for s in soldiers:
        characters.append(s)

    while run:
        clock.tick()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break

        for character in characters:
            other_characters = characters
            character.tick_count += 1
            character.random_move()
            character.move(game_map)
            if type(character).__name__ == "Soldier":
                if character.tick_count % (5 * fps) == 0:
                    bullets.append(character.shoot())
            for other_character in other_characters:
                if (
                    type(other_character).__name__ == "Zombie"
                    and type(character).__name__ != "Zombie"
                ):
                    overlap = character.mask.overlap(
                        other_character.mask,
                        (
                            character.position[0] - other_character.position[0],
                            character.position[1] - other_character.position[1],
                        ),
                    )
                    if overlap and character in characters:
                        characters.remove(character)
                        characters.append(Zombie(character.position))

        for bullet in bullets:
            move = bullet.move(game_map)
            for character in characters:
                if type(character).__name__ == "Zombie":
                    overlap = character.mask.overlap(
                        bullet.mask,
                        (
                            character.position[0] - bullet.position[0],
                            character.position[1] - bullet.position[1],
                        ),
                    )
                    if overlap:
                        if bullet in bullets:
                            bullets.remove(bullet)
                        characters.remove(character)
            if move == "out" and bullet in bullets:
                bullets.remove(bullet)
    draw_window(win, game_map, characters, bullets)
