import os
import pygame

from utils import (
    create_map,
    closest,
    closest_list,
    get_best_index_list,
    alive_count,
    pickle_results,
    load_pickle,
)

pygame.font.init()
win_width = 512
win_height = 512
stat_font = pygame.font.SysFont("comicsans", 12)
best_font = pygame.font.SysFont("comicsans", 50)
draw_stats = True

overwrite_current_pickles = True

fps = 60
seconds_per_run = 5

generations_each = 10000
loops = generations_each * 3
loop_num = 0
counter = 0
characters_testing = "zombies"

win = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption("Infection")

bg_img = pygame.transform.scale2x(
    pygame.image.load(os.path.join("images", "bg.png")).convert_alpha()
)

# IF THESE NUMBERS CHANGE, THEY MUST ALSO CHANGE IN THE RESPECTIVE CONFIG FILE
# pop_size = <num_characters>
num_zombies = 5
num_citizens = 20
num_soldiers = 10

num_closest = 35

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
    genome,
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
        score_label = stat_font.render(
            "Seconds Passed: " + str(round(tick_count / fps)),
            1,
            (255, 255, 255),
        )
        win.blit(score_label, (win_width - score_label.get_width() - 15, 50))

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
            "Characters Testing: " + characters_testing, 1, (255, 255, 255)
        )
        win.blit(score_label, (10, 200))

        score_label = stat_font.render(
            "Loop Number: " + str(loop_num), 1, (255, 255, 255)
        )
        win.blit(score_label, (win_width - score_label.get_width() - 15, 30))

    pygame.display.update()


def main(genomes, config):
    clock = pygame.time.Clock()
    run = True
    gen = 0

    from fitness.zombies import fitness as z_f
    from fitness.citizens import fitness as c_f
    from fitness.soldiers import fitness as s_f
    from characters import Zombie

    bullets = []

    # Start from beginning
    if overwrite_current_pickles:
        zombies, _, z_nets = z_f.setup(num_zombies)
        pickle_results(num_zombies, "best_zombies.pickle", z_nets)
        citizens, _, c_nets = c_f.setup(num_citizens)
        pickle_results(num_citizens, "best_citizens.pickle", c_nets)
        soldiers, _, s_nets = s_f.setup(num_soldiers)
        pickle_results(num_soldiers, "best_soldiers.pickle", s_nets)

    gen += 1
    # Grab data from pickle files
    if counter == 0:
        zombies, ge, z_nets = z_f.setup(num_zombies, genomes=genomes)
        c_nets, citizens = load_pickle(
            num_citizens, c_f, "best_citizens.pickle"
        )
        s_nets, soldiers = load_pickle(
            num_soldiers, s_f, "best_soldiers.pickle"
        )
    elif counter == 1:
        z_nets, zombies = load_pickle(num_zombies, z_f, "best_zombies.pickle")
        citizens, ge, c_nets = c_f.setup(num_citizens, genomes=genomes)
        s_nets, soldiers = load_pickle(
            num_soldiers, s_f, "best_soldiers.pickle"
        )
    elif counter == 2:
        z_nets, zombies = load_pickle(num_zombies, z_f, "best_zombies.pickle")
        c_nets, citizens = load_pickle(
            num_citizens, c_f, "best_citizens.pickle"
        )
        soldiers, ge, s_nets = s_f.setup(num_soldiers, genomes=genomes)

    alive_citizens = citizens.copy()
    alive_zombies = zombies.copy()
    alive_soldiers = soldiers.copy()

    tick_count = 0
    # Run the simulation
    while (
        run
        and (alive_count(soldiers) > 0 or alive_count(citizens) > 0)
        and alive_count(zombies) > 0
        and tick_count < seconds_per_run * fps
    ):
        clock.tick(fps)
        max_fitness = None
        min_fitness = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break
        tick_count += 1
        # Character interaction logic
        for x, zombie in enumerate(zombies):
            if not zombie.is_dead:
                output = z_nets[x].activate(
                    tuple(
                        [zombie.position[0], zombie.position[1]]
                        + closest_list(zombie, alive_zombies, num_closest)
                        + closest_list(zombie, alive_citizens, num_closest)
                        + closest_list(zombie, alive_soldiers, num_closest),
                    ),
                )
                zombie.vel = (output[0], output[1])
                zombie.move(game_map)

            if counter == 0:
                try:
                    max_fitness = max([g.fitness for g in ge])
                    min_fitness = min([g.fitness for g in ge])
                except ValueError:
                    max_fitness = 0
                    min_fitness = 0

        for x, citizen in enumerate(citizens):
            if counter == 1 and not citizen.is_dead:
                ge[x].fitness += (
                    pygame.Vector2(
                        closest(citizen, alive_zombies)[0],
                        closest(citizen, alive_zombies)[1],
                    ).magnitude()
                    / (1000)
                )
            output = c_nets[x].activate(
                tuple(
                    [citizen.position[0], citizen.position[1]]
                    + closest_list(citizen, alive_zombies, num_closest)
                    + closest_list(citizen, alive_citizens, num_closest)
                    + closest_list(citizen, alive_soldiers, num_closest),
                ),
            )

        for citizen in alive_citizens:
            citizen.vel = (output[0], output[1])
            citizen.move(game_map)
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
                        zombies.append(
                            Zombie((citizen.position[0], citizen.position[1]))
                        )
                        z_nets.append(z_nets[zombies.index(zombie)])
                        if counter == 0:
                            ge[zombies.index(zombie)].fitness += 5
                            ge.append(ge[zombies.index(zombie)])
            if counter == 1:
                try:
                    max_fitness = max([g.fitness for g in ge])
                    min_fitness = min([g.fitness for g in ge])
                except ValueError:
                    max_fitness = 0
                    min_fitness = 0

        for x, soldier in enumerate(soldiers):
            if not soldier.is_dead:
                if counter == 2:
                    ge[x].fitness += 0.01
                output = s_nets[x].activate(
                    tuple(
                        [soldier.position[0], soldier.position[1]]
                        + closest_list(soldier, alive_zombies, num_closest)
                        + closest_list(soldier, alive_citizens, num_closest)
                        + closest_list(soldier, alive_soldiers, num_closest),
                    ),
                )
                soldier.reload_count += 1
                soldier.vel = (output[0], output[1])
                soldier.move(game_map)
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
                            zombies.append(
                                Zombie(
                                    (soldier.position[0], soldier.position[1])
                                )
                            )
                            z_nets.append(z_nets[zombies.index(zombie)])
                            if counter == 0:
                                ge[zombies.index(zombie)].fitness += 10
                                ge.append(ge[zombies.index(zombie)])
                if (
                    output[2] > 0.5
                    and soldier.reload_count / fps > soldier.secs_to_reload
                ):
                    bullets.append(soldier.shoot(output[3], output[4]))
            if counter == 2:
                try:
                    max_fitness = max([g.fitness for g in ge])
                    min_fitness = min([g.fitness for g in ge])
                except ValueError:
                    max_fitness = 0
                    min_fitness = 0

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
                    if counter == 2:
                        try:
                            ge[soldiers.index(bullet.soldier)].fitness += 5
                        except ValueError:
                            # if they are already dead
                            pass
            for x, citizen in enumerate(citizens):
                overlap = citizen.mask.overlap(
                    bullet.mask,
                    (
                        citizen.position[0] - bullet.position[0],
                        citizen.position[1] - bullet.position[1],
                    ),
                )
                if overlap:
                    if not citizen.is_dead and bullet in bullets:
                        bullets.remove(bullet)
                    if not citizen.is_dead:
                        citizen.is_dead = True
                        alive_citizens.remove(citizen)
                        if counter == 2:
                            try:

                                ge[soldiers.index(bullet.soldier)].fitness -= 25
                            except ValueError:
                                # if they are already dead
                                pass
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
                        if counter == 2:
                            try:
                                ge[soldiers.index(bullet.soldier)].fitness -= 25
                            except ValueError:
                                # if they are already dead
                                pass
                        soldier.is_dead = True
                        alive_soldiers.remove(soldier)
            if move == "out" and bullet in bullets:
                bullets.remove(bullet)

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
            ge,
        )

    if counter == 0:
        nets = z_nets
    elif counter == 1:
        nets = c_nets
    elif counter == 2:
        nets = s_nets

    best_index_list = get_best_index_list(counter, ge)

    try:
        if len(nets) > 0:
            pickle_results(
                len(nets),
                f"best_{characters_testing}.pickle",
                nets,
                best_index_list,
            )
    except IndexError:
        pass


if __name__ == "__main__":
    from fitness.zombies import fitness as z_f
    from fitness.citizens import fitness as c_f
    from fitness.soldiers import fitness as s_f

    for loop in range(loops):
        loop_num = loop
        counter = loop % 3
        if counter == 0:
            characters_testing = "zombies"
        elif counter == 1:
            characters_testing = "citizens"
        elif counter == 2:
            characters_testing = "soldiers"
        # 0 = Zombies
        # 1 = Citizens
        # 2 = Soldiers
        if counter == 0:
            z_f.run(func=main)
        elif counter == 1:
            c_f.run(func=main)
        elif counter == 2:
            s_f.run(func=main)
