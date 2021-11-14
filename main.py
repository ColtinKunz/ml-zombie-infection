import os
import pickle
import pygame

pygame.font.init()
win_width = 512
win_height = 512
stat_font = pygame.font.SysFont("comicsans", 50)
end_font = pygame.font.SysFont("comicsans", 70)
draw_lines = False
fps = 30
generations_each = 10
loops = generations_each * 3
counter = 0

win = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption("Infection")

bg_img = pygame.transform.scale2x(
    pygame.image.load(os.path.join("images", "bg.png")).convert_alpha()
)

# IF THESE NUMBERS CHANGE, THEY MUST ALSO CHANGE IN THE RESPECTIVE CONFIG FILE
# pop_size = <num_characters>
num_zombies = 50
num_citizens = 1
num_soldiers = 10


def draw_window(win, game_map, zombies, citizens, soldiers, bullets):
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

    if gen == 0:
        with open(
            os.path.join("pickles", "best_zombies.pickle"), "wb"
        ) as z_handle:
            zombies, _, z_nets = z_f.setup(num_zombies)
            pickle.dump(
                z_nets,
                z_handle,
                protocol=pickle.HIGHEST_PROTOCOL,
            )
        with open(
            os.path.join("pickles", "best_citizens.pickle"), "wb"
        ) as c_handle:
            citizens, _, c_nets = c_f.setup(num_citizens)
            pickle.dump(
                c_nets,
                c_handle,
                protocol=pickle.HIGHEST_PROTOCOL,
            )
        with open(
            os.path.join("pickles", "best_soldiers.pickle"), "wb"
        ) as s_handle:
            soldiers, _, s_nets = s_f.setup(num_soldiers)
            pickle.dump(
                s_nets,
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
            c_nets = pickle.load(c_handle)
            citizens = c_f.generate(num_citizens)
        with open(
            os.path.join("pickles", "best_soldiers.pickle"), "rb"
        ) as s_handle:
            s_nets = pickle.load(s_handle)
            soldiers = s_f.generate(num_soldiers)
    elif counter == 1:
        with open(
            os.path.join("pickles", "best_zombies.pickle"), "rb"
        ) as z_handle:
            z_nets = pickle.load(z_handle)
            zombies = z_f.generate(num_zombies)
        citizens, ge, c_nets = c_f.setup(num_citizens, genomes=genomes)
        with open(
            os.path.join("pickles", "best_soldiers.pickle"), "rb"
        ) as s_handle:
            s_nets = pickle.load(s_handle)
            soldiers = s_f.generate(num_soldiers)
    elif counter == 2:
        with open(
            os.path.join("pickles", "best_zombies.pickle"), "rb"
        ) as z_handle:
            z_nets = pickle.load(z_handle)
            zombies = z_f.generate(num_zombies)
        with open(
            os.path.join("pickles", "best_citizens.pickle"), "rb"
        ) as c_handle:
            c_nets = pickle.load(c_handle)
            citizens = c_f.generate(num_citizens)
        soldiers, ge, s_nets = s_f.setup(num_soldiers, genomes=genomes)

    tick_count = 0
    # Run the simulation
    while (
        run
        and len(soldiers) > 0
        or len(citizens) > 0
        and len(zombies) > 0
        and len(ge) > 0
    ):
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break
        tick_count += 1
        # Character interaction logic
        for x, zombie in enumerate(zombies):
            if counter == 0:
                ge[x].fitness += 0.1
            output = z_nets[x].activate(
                (
                    closest(zombie, zombies)[0],
                    closest(zombie, zombies)[1],
                    closest(zombie, citizens)[0],
                    closest(zombie, citizens)[1],
                    closest(zombie, soldiers)[0],
                    closest(zombie, soldiers)[1],
                )
            )
            zombie.vel = (output[0], output[1])
            zombie.move(game_map)

        for x, citizen in enumerate(citizens):
            if counter == 1:
                ge[x].fitness += 0.1
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
                overlap = citizen.mask.overlap(
                    zombie.mask,
                    (
                        citizen.position[0] - zombie.position[0],
                        citizen.position[1] - zombie.position[1],
                    ),
                )
                if overlap:
                    print("overlapped")
                    # if counter == 1:
                    #     ge.pop(x - 1)
                    # c_nets.pop(x - 1)
                    # citizens.pop(x - 1)
                    # zombies.append(Zombie(citizen.position))
                    # z_nets.append(z_nets[zombies.index(zombie)])
                    # if counter == 0:
                    #     ge.append(ge[zombies.index(zombie)])
                    # ge[x].fitness += 1

        for x, soldier in enumerate(soldiers):
            if counter == 1:
                ge[x].fitness += 0.1
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
            soldier.vel = (output[0], output[1])
            soldier.move(game_map)
            for zombie in zombies:
                overlap = soldier.mask.overlap(
                    zombie.mask,
                    (
                        soldier.position[0] - zombie.position[0],
                        soldier.position[1] - zombie.position[1],
                    ),
                )
                if overlap:
                    if counter == 1:
                        ge.pop(x - 1)
                #     s_nets.pop(x-1)
                #     soldiers.pop(x-1)
                #     zombies.append(Zombie(soldier.position))
                #     z_nets.append(z_nets[zombies.index(zombie)])
                #     if counter == 0:
                #         ge.append(ge[zombies.index(zombie)])
                #     ge[x].fitness += 1
            if output[2] > 0.5:
                bullets.append(soldier.shoot())

        # Bullet logic
        for bullet in bullets:
            move = bullet.move(game_map)
            for x, zombie in enumerate(zombies):
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
                    if counter == 0:
                        ge.pop(x - 1)
                    zombies.pop(x - 1)
                    z_nets.pop(x - 1)
                    if counter == 2:
                        ge[soldiers.index(bullet.soldier)].fitness -= 1
                    for g in ge:
                        g.fitness -= 1
            for x, citizen in enumerate(citizens):
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
                    if counter == 1:
                        ge.pop(x - 1)
                    if citizen in citizens:
                        citizens.pop(x - 1)
                    if counter == 2:
                        ge[soldiers.index(bullet.soldier)].fitness += 1
                    ge[x].fitness += 1
            for x, soldier in enumerate(soldiers):
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
                    if counter == 2:
                        ge.pop(x - 1)
                    if soldier in soldiers:
                        soldiers.pop(x - 1)
                    if counter == 2:
                        ge[soldiers.index(bullet.soldier)].fitness += 1
                    ge[x].fitness += 1
            if move == "out" and bullet in bullets:
                bullets.remove(bullet)

        draw_window(win, game_map, zombies, citizens, soldiers, bullets)


def closest(base_character, character_list):
    character_list = character_list.copy()
    if base_character in character_list:
        character_list.remove(base_character)
    try:
        closest = character_list[0]
    except IndexError:
        return (-1, -1)
    for character in character_list:
        if (
            pygame.Vector2(character.position)
            - pygame.Vector2(base_character.position)
        ).magnitude() < (
            pygame.Vector2(closest.position)
            - pygame.Vector2(base_character.position)
        ).magnitude():
            closest = character
    return closest.position


if __name__ == "__main__":
    from fitness.zombies import fitness as z_f
    from fitness.citizens import fitness as c_f
    from fitness.soldiers import fitness as s_f

    for loop in range(loops):
        counter = loop % 3
        # 0 = Zombies
        # 1 = Citizens
        # 2 = Soldiers
        if counter == 0:
            z_f.run(func=main)
        elif counter == 1:
            c_f.run(func=main)
        elif counter == 2:
            s_f.run(func=main)
