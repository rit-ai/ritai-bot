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
    if not os.path.isfile('markov.pkl'):
        generate_database()
    
    chain = MarkovChain('./markov.pkl')
    generated_joke = ''

    while len(generated_joke) < MIN_LENGTH:
        generated_joke = chain.generateString()

    return generated_joke

def generate_database():
    chain = MarkovChain('./markov.pkl')

    with open('in.txt') as f:
        chain.generateDatabase(f.read())
        chain.dumpdb()

    print(chain.generateString())

if __name__ == '__main__':
    print(joke())
