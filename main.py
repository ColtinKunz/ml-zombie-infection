import os
import pygame

from random import randint


pygame.font.init()
win_width = 512
win_height = 512
stat_font = pygame.font.SysFont("comicsans", 50)
end_font = pygame.font.SysFont("comicsans", 70)
draw_lines = False

fps = 30

win = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption("Infection")

bg_img = pygame.transform.scale2x(
    pygame.image.load(os.path.join("images", "bg.png")).convert_alpha()
)


gen = 0


def draw_window(win, game_map, characters, bullets):
    """
    draws the windows for the main game loop
    :param win: pygame window surface
    :return: None
    """
    win.blit(bg_img, (0, 0))
    game_map.draw(win)

    pygame.Surface((win_width, win_height), masks=game_map.mask)

    for character in characters:
        character.draw(win)
    for bullet in bullets:
        bullet.draw(win)
    pygame.display.update()


def main():
    from characters import Zombie, Soldier, Citizen
    from obstacles import HardObstacle, SoftObstacle
    from map import Map

    game_map = Map()

    characters = []
    for i in range(5):
        characters.append(Zombie((randint(9, 490), randint(9, 490))))
    for i in range(50):
        characters.append(Citizen((randint(9, 490), randint(9, 490))))
    for i in range(10):
        characters.append(Soldier((randint(9, 490), randint(9, 490))))

    bullets = []

    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(fps)
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
                        character.position - bullet.position,
                    )
                    if overlap:
                        if bullet in bullets:
                            bullets.remove(bullet)
                        characters.remove(character)
            if move == "out" and bullet in bullets:
                bullets.remove(bullet)

        draw_window(win, game_map, characters, bullets)


main()
