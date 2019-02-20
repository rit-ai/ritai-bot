# author: Paul Galatic
# 
# File for storing bot commands in a way that segments them from the rest of
# the program. The commands are designed to be self-contained.

import os
import random

import cv2
import imageio
import requests
import numpy as np
from scipy import misc
from io import BytesIO

from bot import const
from bot import transmit
from bot.joke import joke
from bot.mnist import mnist
from bot.kmeans import kmeans
from bot.stylize import neural_style_transfer

def respond(message, channel, client, thread):
    '''
    Shorthand for posting a response
    '''
    client.api_call(
        'chat.postMessage',
        channel=channel,
        text=message,
        thread_ts=thread
    )

def bot_help(prompt, channel, client, thread):
    '''
    Prints help prompt, in case the user would like to know more about a 
    particular capability of the bot
    '''
    prompt_list = prompt.split(' ')
    
    # default response
    message =   'RITAI VERSION [%s]:\n' % const.VERSION +\
                '\t@ritai help [command]\n' +\
                '\t\tprints this message, or more info about a command\n' +\
                '\t@ritai kmeans\n' +\
                '\t\tperforms k-means clustering over an image\n' +\
                '\t@ritai mnist\n' +\
                '\t\tguesses what number is in an image\n' +\
                '\t@ritai stylize\n' +\
                '\t\tapplies neural style transfer to an image\n'
    
    # specific responses to particular prompts
    if len(prompt_list) > 1:
        if prompt_list[1] == const.HELP_PROMPT:
            respond('Okay, now you\'re just being silly.', channel, client, thread)

        elif prompt_list[1] == const.KMEANS_PROMPT:
            bot_kmeans(const.HELP_PROMPT, channel, client, thread)
        
        elif prompt_list[1] == const.MNIST_PROMPT:
            bot_mnist(const.HELP_PROMPT, channel, client, thread)
            
        elif prompt_list[1] == const.STYLIZE_PROMPT:
            bot_stylize(const.HELP_PROMPT, channel, client, thread)
        
        else:
            respond('Command not recognized.', channel, client, thread)
         
    else:
        respond(message, channel, client, thread)

    
def bot_mnist(prompt, channel, client, thread):
    '''
    Uses a rudimentary neural net to guess which number is in an image.
    '''
    prompt_list = prompt.split(' ')

    img_url = None
    
    # print help message
    if prompt_list[0] == const.HELP_PROMPT:
        respond(    
                'usage:\n' +\
                    '\t@ritai mnist <image>\n' +\
                    '\t\tAttach an image and I will guess what number it is!\n',
                channel,
                client,
                thread
            )
        return
    # warn user if they entered too many arguments
    if len(prompt_list) > 1:
        respond('Invalid number of arguments: %d' % len(prompt_list), channel, client, thread)
        return
    
    # perform mnist
    img = transmit.read_image(const.IN_IMG_NAME)
    prediction = mnist.query(img)

    # report prediction
    respond('I think this is a... %d.' % prediction, channel, client, thread)

def bot_kmeans(prompt, channel, client, thread):
    '''
    Performs k-means clustering over a given image input (color simplification)

    If an image URL is provided, it attempts to download from that URL. 
    Otherwise, it assumes an attachment was added to the original message.

    If a k value was provided, it uses that k value. Otherwise, it choses
    a random one.
    '''
    prompt_list = prompt.split(' ')

    img_url = None
    k_value = None
    
    # print help message
    if prompt_list[0] == const.HELP_PROMPT:
        respond(
            'usage:\n' +\
                '\t@ritai kmeans [k_value] <image>\n' +\
                '\t\tI will perform k-means color simplification on the attached image.\n' +\
                '\tNOTE: k_value must be in range [1-10].\n' +\
                '\tNOTE: If k_value is not an integer, I will choose one randomly.\n',
            channel,
            client,
            thread
        )
        return
    # was an k value provided?
    if len(prompt_list) > 1:
        k_value = prompt_list[1]
    # warn the user if too many arguments were provided
    if len(prompt_list) > 2:
        respond('Invalid numer of arguments: %d' % len(prompt_list), channel, thread)
        return

    # validate k_value
    
    if k_value:
        try:
            k_value = int(k_value)
            if not (0 < k_value < 11):
                respond('K value must be between 1 and 10 inclusive.', channel, thread)
                return
        except ValueError:
            k_value = None
    if not k_value:
        k_value = (int)(np.random.normal(7, 3))
        if k_value < 1: k_value = 1
        if k_value > 10: k_value = 10

    # perform kMeans
    img = transmit.read_image(const.IN_IMG_NAME)
    output = kmeans.kMeans(img, k_value)
    transmit.write_image(const.OUT_IMG_NAME, output)
    
    transmit.upload_image(('k: %d' % k_value), channel, client, thread)

def bot_stylize(prompt, channel, client, thread):
    '''
    Applies style transfer to an image using a neural network.
    '''
    
    prompt_list = prompt.split(' ')
    
    STYLES = ['candy', 'composition_vii', 'feathers', 'la_muse', 'mosaic', 'starry_night', 'the_scream', 'the_wave', 'udnie']
    
    style = None
    img_url = None
    
    # print help message
    if prompt_list[0] == const.HELP_PROMPT:
        respond(
            'usage:\n' +\
                '\t@ritai stylize <image>\n' +\
                '\t\tI will stylize the attached image with a random style.\n' +\
                '\t@ritai stylize [style] <image>\n' +\
                '\t\tI will stylize the attached image with a specific style.\n' +\
                '\tNOTE: valid styles include:\n' +\
                '\t' + str(STYLES) + '\n',
            channel,
            client,
            thread
        )
        return
    # what style does the user want?
    if len(prompt_list) > 1:
        desire = prompt_list[1].lower()
        if desire in STYLES:
            style = desire
        else:
            respond(
                'I don\'t recognize the style %s. Try @ritai help ' % desire +\
                'stylize for available styles.',
                channel,
                client
            )
            return
    # warn the user if they provided too many arguments
    if len(prompt_list) > 2:
        respond('Invalid numer of arguments: %d' % len(prompt_list), channel, client, thread)
        return
    
    if not style:
        style = random.choice(STYLES)
    
    ckpt = str(const.MODEL_PATH / ('{style}.t7'.format(style=style)))
    
    # perform style transfer
    img = transmit.read_image(const.IN_IMG_NAME)
    _, output = neural_style_transfer.style_transfer(img, ckpt)
    transmit.write_image(const.OUT_IMG_NAME, output)
    
    # post image to channel
    transmit.upload_image(('style: %s' % style), channel, client, thread)
    
def bot_joke(prompt, channel, client, thread):
    '''
    Has the bot try to tell a joke using a joke database and a Markov chain.

    The user can provide a seed if desired.
    '''

    prompt_list = prompt.split(' ')

    seed = None
    response = None

    # markov samples can be seeded by a provided string
    if len(prompt_list) > 1:
        seed = ' '.join(prompt_list[1:])

    if seed:
        response = joke.joke_with_seed(seed)
    else:
        response = joke.joke()

    respond(response, channel, client, thread)
