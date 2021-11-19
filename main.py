import os
import pickle
import pygame

from utils import closest, get_best_index, alive_count

pygame.font.init()
win_width = 512
win_height = 512
stat_font = pygame.font.SysFont("comicsans", 12)
best_font = pygame.font.SysFont("comicsans", 50)
draw_stats = True

overwrite_current_pickles = True

fps = 60
seconds_per_run = 10

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
num_zombies = 50
num_citizens = 40
num_soldiers = 10


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
    best_character_pos,
):
    """
    draws the windows for the main game loop
    :param win: pygame window surface
    :return: None
    """
    best_character_label_pos = (
        best_character_pos[0] - 10,
        best_character_pos[1] - 40,
    )
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

        # generations
        score_label = stat_font.render(
            "Highest Fitness: " + str(round(max_fitness)), 1, (255, 255, 255)
        )
        win.blit(score_label, (10, 10))

        score_label = stat_font.render(
            "Lowest Fitness: " + str(round(min_fitness)), 1, (255, 255, 255)
        )
        win.blit(score_label, (10, 25))

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

        score_label = best_font.render("*", 1, (255, 255, 255))
        win.blit(score_label, best_character_label_pos)

    pygame.display.update()


def main(genomes, config):
    clock = pygame.time.Clock()
    run = True
    gen = 0

    from fitness.zombies import fitness as z_f
    from fitness.citizens import fitness as c_f
    from fitness.soldiers import fitness as s_f
    from characters import Zombie
    from map import Map

    game_map = Map()

    bullets = []

    # Start from beginning
    if overwrite_current_pickles:
        with open(
            os.path.join("pickles", "best_zombies.pickle"), "wb"
        ) as z_handle:
            zombies, _, z_nets = z_f.setup(num_zombies)
            pickle.dump(
                z_nets[0],
                z_handle,
                protocol=pickle.HIGHEST_PROTOCOL,
            )
        with open(
            os.path.join("pickles", "best_citizens.pickle"), "wb"
        ) as c_handle:
            citizens, _, c_nets = c_f.setup(num_citizens)
            pickle.dump(
                c_nets[0],
                c_handle,
                protocol=pickle.HIGHEST_PROTOCOL,
            )
        with open(
            os.path.join("pickles", "best_soldiers.pickle"), "wb"
        ) as s_handle:
            soldiers, _, s_nets = s_f.setup(num_soldiers)
            pickle.dump(
                s_nets[0],
                s_handle,
                protocol=pickle.HIGHEST_PROTOCOL,
            )

    gen += 1
    # Grab data from pickle files
    if counter == 0:
        zombies, ge, z_nets = z_f.setup(num_zombies, genomes=genomes)
        with open(
            os.path.join("pickles", "best_citizens.pickle"), "rb"
        ) as c_handle:
            c_net = pickle.load(c_handle)
            c_nets = [c_net for i in range(num_citizens)]
            citizens = c_f.generate(num_citizens)
        with open(
            os.path.join("pickles", "best_soldiers.pickle"), "rb"
        ) as s_handle:
            s_net = pickle.load(s_handle)
            s_nets = [s_net for i in range(num_soldiers)]
            soldiers = s_f.generate(num_soldiers)
    elif counter == 1:
        with open(
            os.path.join("pickles", "best_zombies.pickle"), "rb"
        ) as z_handle:
            z_net = pickle.load(z_handle)
            z_nets = [z_net for i in range(num_zombies)]
            zombies = z_f.generate(num_zombies)
        citizens, ge, c_nets = c_f.setup(num_citizens, genomes=genomes)
        with open(
            os.path.join("pickles", "best_soldiers.pickle"), "rb"
        ) as s_handle:
            s_net = pickle.load(s_handle)
            s_nets = [s_net for i in range(num_soldiers)]
            soldiers = s_f.generate(num_soldiers)
    elif counter == 2:
        with open(
            os.path.join("pickles", "best_zombies.pickle"), "rb"
        ) as z_handle:
            z_net = pickle.load(z_handle)
            z_nets = [z_net for i in range(num_zombies)]
            zombies = z_f.generate(num_zombies)
        with open(
            os.path.join("pickles", "best_citizens.pickle"), "rb"
        ) as c_handle:
            c_net = pickle.load(c_handle)
            c_nets = [c_net for i in range(num_citizens)]
            citizens = c_f.generate(num_citizens)
        soldiers, ge, s_nets = s_f.setup(num_soldiers, genomes=genomes)

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
                # if counter == 0:
                #     ge[x].fitness += 0.1
                closest_citizen = closest(zombie, citizens)
                closest_soldier = closest(zombie, soldiers)
                print(closest_citizen)
                output = z_nets[x].activate(
                    (
                        closest(zombie, zombies)[0],
                        closest(zombie, zombies)[1],
                        closest_citizen[0],
                        closest_citizen[1],
                        closest_soldier[0],
                        closest_soldier[1],
                        0 if closest_citizen[0] < -100 else 1,
                        0 if closest_soldier[0] < -100 else 1,
                    )
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
            if not citizen.is_dead:
                if counter == 1:
                    ge[x].fitness -= 0.1
                    ge[x].fitness -= (
                        pygame.Vector2(
                            closest(citizen, zombies)[0],
                            closest(citizen, zombies)[1],
                        ).magnitude()
                        / (tick_count * fps)
                    )
                output = c_nets[x].activate(
                    (
                        closest(citizen, zombies)[0],
                        closest(citizen, zombies)[1],
                        closest(citizen, citizens)[0],
                        closest(citizen, citizens)[1],
                        closest(citizen, soldiers)[0],
                        closest(citizen, soldiers)[1],
                    )
                )
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
                            zombies.append(Zombie(citizen.position))
                            z_nets.append(z_nets[zombies.index(zombie)])
                            if counter == 0:
                                ge[zombies.index(zombie)].fitness += 5
                                ge.append(ge[zombies.index(zombie)])
                            for g in ge:
                                g.fitness += 5
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
                    ge[x].fitness -= 0.01
                output = s_nets[x].activate(
                    (
                        closest(soldier, zombies)[0],
                        closest(soldier, zombies)[1],
                        closest(soldier, citizens)[0],
                        closest(soldier, citizens)[1],
                        closest(soldier, soldiers)[0],
                        closest(soldier, soldiers)[1],
                    )
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
                            zombies.append(Zombie(soldier.position))
                            z_nets.append(z_nets[zombies.index(zombie)])
                            if counter == 0:
                                ge[zombies.index(zombie)].fitness += 10
                                ge.append(ge[zombies.index(zombie)])
                            for g in ge:
                                g.fitness += 5
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
            for x, zombie in enumerate(zombies):
                if not zombie.is_dead:
                    overlap = zombie.mask.overlap(
                        bullet.mask,
                        (
                            zombie.position[0] - bullet.position[0],
                            zombie.position[1] - bullet.position[1],
                        ),
                    )
                    if overlap:
                        for g in ge:
                            g.fitness -= 1
                        if bullet in bullets:
                            bullets.remove(bullet)
                        zombie.is_dead = True
                        if counter == 2:
                            try:
                                ge[soldiers.index(bullet.soldier)].fitness -= 5
                            except ValueError:
                                # if they are already dead
                                pass
            for x, citizen in enumerate(citizens):
                if not citizen.is_dead:
                    overlap = citizen.mask.overlap(
                        bullet.mask,
                        (
                            citizen.position[0] - bullet.position[0],
                            citizen.position[1] - bullet.position[1],
                        ),
                    )
                    if overlap:
                        if bullet in bullets:
                            bullets.remove(bullet)
                        for g in ge:
                            g.fitness += 1
                        citizen.is_dead = True
                        if counter == 2:
                            try:
                                ge[soldiers.index(bullet.soldier)].fitness += 5
                            except ValueError:
                                # if they are already dead
                                pass
            for x, soldier in enumerate(soldiers):
                if not soldier.is_dead:
                    overlap = soldier.mask.overlap(
                        bullet.mask,
                        (
                            soldier.position[0] - bullet.position[0],
                            soldier.position[1] - bullet.position[1],
                        ),
                    )
                    if overlap:
                        if bullet in bullets:
                            bullets.remove(bullet)
                        for g in ge:
                            g.fitness += 1
                        if counter == 2:
                            try:
                                ge[soldiers.index(bullet.soldier)].fitness += 5
                            except ValueError:
                                # if they are already dead
                                pass
                        soldier.is_dead = True
            if move == "out" and bullet in bullets:
                bullets.remove(bullet)
        try:
            best_index = get_best_index(counter, ge)
            if counter == 0:
                best_position = zombies[best_index].position
            elif counter == 1:
                best_position = citizens[best_index].position
            elif counter == 2:
                best_position = soldiers[best_index].position
        except IndexError:
            best_position = (-1000, -1000)
        except ValueError:
            best_position = (-1000, -1000)
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
            best_position,
        )

    if counter == 0:
        nets = z_nets
    elif counter == 1:
        nets = c_nets
    elif counter == 2:
        nets = s_nets

    best_index = get_best_index(counter, ge)

    try:
        if len(nets) > 0:
            with open(
                os.path.join("pickles", f"best_{characters_testing}.pickle"),
                "wb",
            ) as handle:
                pickle.dump(
                    nets[best_index],
                    handle,
                    protocol=pickle.HIGHEST_PROTOCOL,
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
