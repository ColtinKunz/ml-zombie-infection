import os
import neat

from random import randint
from neat.six_util import iteritems
from neat.reporting import ReporterSet


def setup(num_soldiers, genomes=None):
    nets = []
    ge = []

    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path,
    )

    if genomes is None:
        reporters = ReporterSet()
        stagnation = config.stagnation_type(config.stagnation_config, reporters)
        reproduction = config.reproduction_type(
            config.reproduction_config, reporters, stagnation
        )
        population = reproduction.create_new(
            config.genome_type, config.genome_config, config.pop_size
        )
        genomes = list(iteritems(population))

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0
        ge.append(g)

    return generate(num_soldiers), ge, nets


def generate(num_soldiers):
    from characters import Soldier

    soldiers = []
    for i in range(num_soldiers):
        soldiers.append(Soldier((randint(9, 490), randint(9, 490))))
    return soldiers


def run(func):
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path,
    )
    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(func, 1)
    print("\nBest genome:\n{!s}".format(winner))
