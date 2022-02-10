import os
import math
import pygame
import numpy as np


fps = 90
real_time = True
max_ticks = 500
overwrite_current_pickles = True
draw = True
elitism = 0.04
mutation_rate = 0.1

loop_index = 0
pygame.font.init()
win_width = 1000
win_height = 1000
stat_font = pygame.font.SysFont("comicsans", 12)
best_font = pygame.font.SysFont("comicsans", 50)
draw_stats = True

character_choices = {"z": "zombies", "c": "citizens", "s": "soldiers"}

characters_testing_string = character_choices["z"]

win = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption("Infection")
central_vector = pygame.Vector2((win_height / 2, win_width / 2))

bg_img = pygame.transform.scale2x(
    pygame.image.load(os.path.join("images", "bg.png")).convert_alpha()
)

num_zombies = 50
num_citizens = 0
num_soldiers = 0

highest_pop = max(num_zombies, num_citizens, num_soldiers)
zombie_loops = np.ceil(highest_pop / num_zombies) if num_zombies > 0 else 0
citizen_loops = np.ceil(highest_pop / num_citizens) if num_citizens > 0 else 0
soldier_loops = np.ceil(highest_pop / num_soldiers) if num_soldiers > 0 else 0

num_input_nodes = (num_zombies + num_citizens + num_soldiers) * 2

from utils import (  # noqa: E402
    create_map,
    closest_list,
    alive_count,
    pickle_results,
    load_pickle,
    character_setup,
    closest,
)

game_map = create_map()


def draw_window(
    win,
    game_map,
    zombies,
    citizens,
    soldiers,
    bullets,
    tick_count,
    max_fitness,
    min_fitness,
):
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

    if draw_stats:
        # score
        score_label = stat_font.render(
            "Tick Count: " + str(tick_count), 1, (255, 255, 255)
        )
        win.blit(score_label, (win_width - score_label.get_width() - 15, 10))

        try:
            # generations
            score_label = stat_font.render(
                "Highest Fitness: " + str(round(max_fitness)),
                1,
                (255, 255, 255),
            )
            win.blit(score_label, (10, 10))

            score_label = stat_font.render(
                "Lowest Fitness: " + str(round(min_fitness)), 1, (255, 255, 255)
            )
            win.blit(score_label, (10, 25))

        except TypeError:
            print("fitness returned as none")
            pass

        score_label = stat_font.render(
            "Zombies Alive: " + str(alive_count(zombies)), 1, (255, 255, 255)
        )
        win.blit(score_label, (10, 100))

        score_label = stat_font.render(
            "Citizens Alive: " + str(alive_count(citizens)), 1, (255, 255, 255)
        )
        win.blit(score_label, (10, 140))

        score_label = stat_font.render(
            "Soldiers Alive: " + str(alive_count(soldiers)), 1, (255, 255, 255)
        )
        win.blit(score_label, (10, 60))

        score_label = stat_font.render(
            "Characters Testing: " + characters_testing_string,
            1,
            (255, 255, 255),
        )
        win.blit(score_label, (10, 200))

        score_label = stat_font.render(
            "Loop Number: " + str(loop), 1, (255, 255, 255)
        )
        win.blit(score_label, (win_width - score_label.get_width() - 15, 30))

    pygame.display.update()


def simulate():
    clock = pygame.time.Clock()
    run = True
    gen = 0

    from characters import Zombie

    bullets = []

    max_fitness = None
    min_fitness = None

    # Start from beginning
    if overwrite_current_pickles and loop_index == 0:
        zombies = character_setup(character_choices["z"], num_zombies)
        pickle_results("best_zombies.pickle", zombies)
        citizens = character_setup(character_choices["c"], num_citizens)
        pickle_results("best_citizens.pickle", citizens)
        soldiers = character_setup(character_choices["s"], num_soldiers)
        pickle_results("best_soldiers.pickle", soldiers)

    zombies = load_pickle(
        num_zombies,
        character_choices["z"],
        mutate=(True if counter == 0 else False),
    )
    citizens = load_pickle(
        num_citizens,
        character_choices["c"],
        mutate=(True if counter == 1 else False),
    )
    soldiers = load_pickle(
        num_soldiers,
        character_choices["s"],
        mutate=(True if counter == 2 else False),
    )

    gen += 1
    # Grab data from pickle files

    alive_citizens = citizens.copy()
    alive_zombies = zombies.copy()
    alive_soldiers = soldiers.copy()

    tick_count = 0
    # Run the simulation
    while (
        run
        and (
            (alive_count(soldiers) > 0 or num_soldiers == 0)
            or (alive_count(citizens) > 0 or num_citizens == 0)
        )
        and (alive_count(zombies) > 0 or num_zombies == 0)
        and tick_count < max_ticks
    ):
        clock.tick()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break
        tick_count += 1
        # Character interaction logic
        for zombie in alive_zombies:
            output = zombie.think(
                tuple(
                    [zombie.position[0], zombie.position[1]]
                    + closest_list(zombie, alive_zombies, num_zombies - 1)
                    + closest_list(zombie, alive_citizens, num_citizens)
                    + closest_list(zombie, alive_soldiers, num_soldiers),
                ),
            )
            zombie.vel = (output[0], output[1])
            zombie.move(game_map)

            zombie.fitness += (
                1
                / (
                    (
                        pygame.Vector2(zombie.position) + central_vector
                    ).magnitude()
                )
                * 10
            )
        for citizen in alive_citizens:
            output = citizen.think(
                tuple(
                    [citizen.position[0], citizen.position[1]]
                    + closest_list(citizen, alive_zombies, num_zombies)
                    + closest_list(citizen, alive_citizens, num_citizens - 1)
                    + closest_list(citizen, alive_soldiers, num_soldiers),
                ),
            )
            citizen.vel = (output[0], output[1])
            citizen.move(game_map)
            citizen.fitness += (
                pygame.Vector2(
                    closest(citizen, alive_zombies),
                ).magnitude()
                / 10000
            ) * 10
            citizen.fitness += 1 / (
                (pygame.Vector2(citizen.position) + central_vector).magnitude()
            )

            for zombie in zombies:
                if not citizen.is_dead and not zombie.is_dead:
                    overlap = citizen.mask.overlap(
                        zombie.mask,
                        (
                            citizen.position[0] - zombie.position[0],
                            citizen.position[1] - zombie.position[1],
                        ),
                    )
                    if overlap and citizen in citizens:
                        citizen.is_dead = True
                        alive_citizens.remove(citizen)
                        new_zombie = Zombie(
                            citizen.position,
                            num_input_nodes,
                            2,
                            w_input_hidden=zombie.w_input_hidden,
                            w_hidden_hidden=zombie.w_hidden_hidden,
                            w_hidden_output=zombie.w_hidden_output,
                        )
                        new_zombie.fitness = zombie.fitness
                        zombies.append(new_zombie)
                        alive_zombies.append(new_zombie)
                        zombie.fitness += 5

        for soldier in alive_soldiers:
            output = soldier.think(
                tuple(
                    [soldier.position[0], soldier.position[1]]
                    + closest_list(soldier, alive_zombies, num_zombies)
                    + closest_list(soldier, alive_citizens, num_citizens)
                    + closest_list(soldier, alive_soldiers, num_soldiers - 1),
                ),
            )
            soldier.reload_count += 1
            soldier.vel = (output[0], output[1])
            soldier.move(game_map)
            soldier.fitness += (
                1
                / (
                    (
                        pygame.Vector2(soldier.position) + central_vector
                    ).magnitude()
                )
                * 10
            )
            for zombie in zombies:
                if not soldier.is_dead and not zombie.is_dead:
                    overlap = soldier.mask.overlap(
                        zombie.mask,
                        (
                            soldier.position[0] - zombie.position[0],
                            soldier.position[1] - zombie.position[1],
                        ),
                    )
                    if overlap and soldier in soldiers:
                        soldier.is_dead = True
                        alive_soldiers.remove(soldier)
                        new_zombie = Zombie(
                            soldier.position,
                            num_input_nodes,
                            2,
                            w_input_hidden=zombie.w_input_hidden,
                            w_hidden_hidden=zombie.w_hidden_hidden,
                            w_hidden_output=zombie.w_hidden_output,
                        )
                        new_zombie.fitness = zombie.fitness
                        zombies.append(new_zombie)
                        alive_zombies.append(new_zombie)
                        zombie.fitness += 5
            if (
                output[2] > 0.5
                and soldier.reload_count > soldier.ticks_to_reload
            ):
                bullets.append(soldier.shoot(output[3], output[4]))

        # Bullet logic
        for bullet in bullets:
            move = bullet.move(game_map)
            for x, zombie in enumerate(alive_zombies):
                overlap = zombie.mask.overlap(
                    bullet.mask,
                    (
                        zombie.position[0] - bullet.position[0],
                        zombie.position[1] - bullet.position[1],
                    ),
                )
                if overlap:
                    if bullet in bullets:
                        bullets.remove(bullet)
                    zombie.is_dead = True
                    alive_zombies.remove(zombie)
                    bullet.soldier.fitness += 5
            for x, citizen in enumerate(citizens):
                overlap = citizen.mask.overlap(
                    bullet.mask,
                    (
                        citizen.position[0] - bullet.position[0],
                        citizen.position[1] - bullet.position[1],
                    ),
                )
                if overlap:
                    if not citizen.is_dead:
                        if bullet in bullets:
                            bullets.remove(bullet)
                        citizen.is_dead = True
                        alive_citizens.remove(citizen)
            for x, soldier in enumerate(soldiers):
                overlap = soldier.mask.overlap(
                    bullet.mask,
                    (
                        soldier.position[0] - bullet.position[0],
                        soldier.position[1] - bullet.position[1],
                    ),
                )
                if overlap:
                    if not soldier.is_dead and bullet in bullets:
                        bullets.remove(bullet)
                    if not soldier.is_dead:
                        soldier.is_dead = True
                        alive_soldiers.remove(soldier)
            if move == "out" and bullet in bullets:
                bullets.remove(bullet)

        if counter == 0:
            characters_testing = zombies
        elif counter == 1:
            characters_testing = citizens
        elif counter == 2:
            characters_testing = soldiers

        characters_testing.sort(reverse=True, key=lambda c: c.fitness)

        max_fitness = characters_testing[0].fitness
        min_fitness = characters_testing[len(characters_testing) - 1].fitness

        if draw:
            draw_window(
                win,
                game_map,
                zombies,
                citizens,
                soldiers,
                bullets,
                tick_count,
                max_fitness,
                min_fitness,
            )

    # Only save characters when on the associated counter value
    if counter == 0:
        pickle_results(
            "best_zombies.pickle",
            zombies,
        )
    elif counter == 1:
        pickle_results(
            "best_citizens.pickle",
            citizens,
        )
    elif counter == 2:
        pickle_results(
            "best_soldiers.pickle",
            soldiers,
        )

    print(
        f"{characters_testing_string}: Max = {np.round(max_fitness, decimals=2)}; Min = {np.round(min_fitness, decimals=2)}; Mean = {np.round(np.mean([c.fitness for c in characters_testing]), decimals=2)}"
    )


if __name__ == "__main__":
    while True:
        loop = math.floor(loop_index / 3)
        counter = 2
        if counter == 0:
        if counter == 0 and num_zombies > 0:
            sub_loops = zombie_loops
            characters_testing_string = character_choices["z"]
        elif counter == 1 and num_citizens > 0:
            sub_loops = citizen_loops
            characters_testing_string = character_choices["c"]
        elif counter == 2 and num_soldiers > 0:
            sub_loops = soldier_loops
            characters_testing_string = character_choices["s"]
        sub_counter = 0
        while sub_loops > sub_counter:
            simulate()
            sub_counter += 1
        loop_index += 1
