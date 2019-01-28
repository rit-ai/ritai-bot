# author: Paul Galatic
#
# Some utility functions

# Imports

import argparse

# Constants

MODEL_DIR = 'models/'

def parse_args():
    '''construct the argument parser and parse the arguments'''
    ap = argparse.ArgumentParser()
    ap.add_argument("-m", "--model", required=False,
        help="neural style transfer model")
    ap.add_argument("-i", "--im_name", required=True,
        help="name of input image to apply neural style transfer to")
    return ap.parse_args()