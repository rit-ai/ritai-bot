# author Paul Galatic
#
# script to generate and return a joke
#

import os
import random
import numpy as np
from pymarkovchain import MarkovChain

MIN_LENGTH = 50

def joke():
    """
    Produces a joke based on the existing database (creates database if 
    one doesn't already exist).
    """
    if not os.path.isfile('markovdb'):
        generate_database()
    
    chain = MarkovChain()
    generated_joke = ''

    while len(generated_joke) < MIN_LENGTH:
        generated_joke = chain.generateString()

    return generated_joke

def joke_with_seed(seed):
    """
    Same as joke(), but takes a seed to feed into the Markov Chain.
    """
    if not os.path.isfile('markovdb'):
        generate_database()

    chain = MarkovChain()
    generated_joke = ''

    while len(generated_joke) < MIN_LENGTH:
        generated_joke = chain.generateStringWithSeed(seed)

    return generated_joke

def generate_database():
    """
    Generates the database that the Markov Chain will use to make its word-by-
    word predictions. It will attempt to create this file in the same directory
    as where the script is currently located.
    """
    currpath = os.path.dirname(__file__)
    path_to_data = os.path.join(currpath, 'in.txt')

    chain = MarkovChain()
    
    with open(path_to_data) as f:
        chain.generateDatabase(f.read())
        chain.dumpdb()

    print(chain.generateString())

if __name__ == '__main__':
    print(joke())
