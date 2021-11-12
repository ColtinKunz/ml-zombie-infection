import os
import neat
import pickle


def setup(genomes, config):
    nets = []
    ge = []
    citizen_lists = []

    for g in genomes:
        net = neat.nn.FeedForwardNetwork(g, config)
        nets.append(net)
        citizens = []
        for i in range(50):
            with open(
                os.path.join("pickles", "best_citizens.pickle"), "rb"
            ) as c_handle:
                citizens = pickle.load(c_handle)
        citizen_lists.append(citizens)
        g.fitness = 0
        ge.append(g)

    return citizen_lists, ge
