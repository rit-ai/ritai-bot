# author Paul Galatic
#
# script to generate and return a joke
#

import os
import random
import numpy as np
from pymarkovchain import MarkovChain

def main():
    chain = MarkovChain('./markov.pkl')

    with open('in.txt') as f:
        chain.generateDatabase(f.read())
        chain.dumpdb()

    print(chain.generateString())

if __name__ == '__main__':
    main()
