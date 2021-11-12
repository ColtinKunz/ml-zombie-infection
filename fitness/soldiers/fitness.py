import os
import neat
from random import randint


def fitness(genomes, config):
    from characters import Soldier

    nets = []
    ge = []
    soldier_lists = []

    for g in genomes:
        net = neat.nn.FeedForwardNetwork(g, config)
        nets.append(net)
        soldiers = []
        for i in range(50):
            soldiers.append(Soldier((randint(9, 490), randint(9, 490))))
        soldier_lists.append(soldiers)
        g.fitness = 0
        ge.append(g)


def run(config_file):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_file,
    )

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    # p.add_reporter(neat.Checkpointer(5))

    # Run for up to 50 generations.
    winner = p.run(fitness, 50)

    # show final stats
    print("\nBest genome:\n{!s}".format(winner))


def fit():
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    config_path = os.path.join("config-feedforward.txt")
    run(config_path)
