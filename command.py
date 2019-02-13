# author: Paul Galatic
# 
# File for storing bot commands in a way that segments them from the rest of
# the program. The commands are designed to be self-contained.

import os
import random

import imageio
import requests
import numpy as np
from scipy import misc
from io import BytesIO

import const
from joke import joke
from mnist import mnist
from kmeans import kMeans
from neural_style_transfer.neural_style_transfer import style_transfer

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

def check_url(url):
    '''
    Returns True if the url returns a response code between 200-300,
    otherwise return False.

    author: Matto Todd
    '''
    
    if url[0] == '<':
        url = url[1:-1]

    try:
        response = requests.get(url, headers=HEADERS)
    except ConnectionError:
        return False

    if response.status_code <= 200:
        return True

    return False

def download_image(img_url):
    '''
    Download an image from a url
    '''

    # sometimes slack packages urls in messages in brackets
    # these will cause an error unless we remove them
    if img_url[0] == '<':
        img_url = img_url[1:-1]
    
    const.BOT_TOKEN = os.environ.get('APP_BOT_USER_TOKEN')
    headers = {'Authorization': 'Bearer %s' % const.BOT_TOKEN}
    response = requests.get(img_url, headers=headers)
    with open(const.IN_IMG_NAME, 'wb') as image:
        image.write(response.content)
        
def upload_image(comment, channel, client, thread):
    '''post image to channel'''
    with open(const.OUT_IMG_NAME, 'rb') as f:
        client.api_call(
            'files.upload',
            channels=[channel],
            filename=const.OUT_IMG_NAME,
            title='output',
            initial_comment=comment,
            file=f,
            thread_ts=thread
        )
        
def read_image(fname):
    '''
    Reads in an image. If the image is not present, it returns a default image.
    '''
    try:
        return imageio.imread(const.IN_IMG_NAME)
    except FileNotFoundError:
        return imageio.imread(const.DEFAULT_IMG_NAME)

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
                    '\t@ritai mnist\n' +\
                    '\t\tguess what number is in attached image\n' +\
                    '\t@ritai mnist [image_url]\n' +\
                    '\t\tguess what number is in image in url\n',
                channel,
                client
            )
        return
    # was an image url provided?
    if len(prompt_list) > 1:
        img_url = prompt_list[1]
    # warn user if they entered too many arguments
    if len(prompt_list) > 2:
        respond('Invalid number of arguments: %d' % len(prompt_list), channel, client, thread)
        return

    # validate url
    if img_url and not check_url(img_url):
        respond('Could not validate url.', channel, client, thread)
        return
    
    if img_url: download_image(img_url) 
    
    # perform mnist
    img = read_image(const.IN_IMG_NAME)
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
                '\t@ritai kmeans [k_value]\n' +\
                '\t\tperform k-means over the attached image\n' +\
                '\t@ritai kmeans [k_value] [image_url]\n' +\
                '\t\tperform k-means over image denoted by url\n' +\
                '\tNOTE: k_value must be in range [1-10]\n' +\
                '\tNOTE: if k_value is not an integer, a random k_value will be chosen\n',
            channel,
            client
        )
        return
    # was an k value provided?
    if len(prompt_list) > 1:
        k_value = prompt_list[1]
    # was a k value provided?
    if len(prompt_list) > 2:
        img_url = prompt_list[2]
    # warn the user if too many arguments were provided
    if len(prompt_list) > 3:
        respond('Invalid numer of arguments: %d' % len(prompt_list), channel, thread)
        return

    # validate url and k-value, as necessary

    if img_url and not check_url(img_url):
        respond('Could not validate url.', channel, client, thread)
        return

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
    
    # acquire image (if no url, assume image has already been downloaded)
    if img_url: download_image(img_url)

    # perform kMeans
    img = read_image(const.IN_IMG_NAME)
    output = kMeans(img, k_value)
    imageio.imwrite(const.OUT_IMG_NAME, output)
    
    upload_image(('k: %d' % k_value), channel, client, thread)

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
                '\t@ritai stylize\n' +\
                '\t\tStylize attached image with random style\n' +\
                '\t@ritai stylize [style]\n' +\
                '\t\tStylize attached image with a specific style\n' +\
                '\t@ritai stylize [style] [img_url]\n' +\
                '\t\tStylize image in URL with a specific style\n' +\
                '\tNOTE: valid styles include:\n' +\
                '\t' + str(STYLES) + '\n',
            channel,
            client
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
    # did the user provide a url in addition to a style?
    if len(prompt_list) > 2:
        img_url = prompt_list[2]
    # warn the user if they provided too many arguments
    if len(prompt_list) > 3:
        respond('Invalid numer of arguments: %d' % len(prompt_list), channel, client, thread)
        return
    
    if img_url and not check_url(img_url):
        respond('Could not validate url.', channel, client, thread)
        return
        
    # acquire image (if no url, assume image has already been downloaded)
    if img_url: download_image(img_url)
    
    if not style:
        style = random.choice(STYLES)
    
    ckpt = 'neural_style_transfer/models/%s.t7' % style
    
    # perform style transfer
    img = read_image(const.IN_IMG_NAME)
    _, output = style_transfer(img, ckpt)
    imageio.imwrite(const.OUT_IMG_NAME, output)
    
    # post image to channel
    upload_image(('style: %s' % style), channel, client, thread)
    
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
