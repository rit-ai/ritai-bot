# TODO
# http://arno.uvt.nl/show.cgi?fid=144631
# https://arxiv.org/abs/1806.04510
#
# Code based on:
# machinelearningmastery.com/text-generation-lstm-recurrent-neural-networks-python-keras/


import os
import re
import sys
import keras
import pickle
import numpy as np

SEQUENCE_LENGTH = 1 * 10**3
MAX_LENGTH = 1 * 10**4

# regular expression to remove control characters
STRIP_STRING = lambda s: re.sub('[\0\200-\377]', '', s)

class Database():
    def __init__(self, sequences, out_shape):
        self.sequences = sequences
        self.out_shape = out_shape

def generate_database(fname):
    
    with open(fname + '.txt', 'r') as f:
        raw = f.read()
    raw = STRIP_STRING(raw)[:MAX_LENGTH]
    chars = sorted(list(set(raw)))
    int_chars = dict((c, i) for i, c in enumerate(chars))

    n_chars = len(raw)
    n_vocab = len(chars)

    print('Length: %d' % n_chars)
    print('Vocab: %d' % n_vocab)

    dataX = []
    dataY = []
    
    for i in range(0, len(raw) - SEQUENCE_LENGTH, 1):
        seq_in = raw[i:i+SEQUENCE_LENGTH]
        seq_out = raw[i + SEQUENCE_LENGTH]
        dataX.append([int_chars[char] for char in seq_in])
        dataY.append(int_chars[seq_out])

    n_patterns = len(dataX)
    print('Total patterns: %d' % n_patterns)

    sequences = np.reshape(dataX, (n_patterns, SEQUENCE_LENGTH, 1))
    sequences = sequences / float(n_vocab)

    out_shape = keras.utils.np_utils.to_categorical(dataY)

    db = Database(sequences, out_shape)
    with open('db.pkl', 'wb') as f:
        pickle.dump(db, f)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: python deepjoke.py [filename]')
        sys.exit(1)
    fname = sys.argv[1]
    generate_database(fname)

