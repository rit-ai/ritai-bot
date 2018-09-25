# author: Paul Galatic
# 
# boilerplate code from:
#   fullstackpython.com
#   https://github.com/mattmakai

import os
import re
import sys
import pdb
import time
import urllib
import requests
import traceback
import validators
import numpy as np
from scipy import misc
from io import BytesIO
from joke import joke
from mnist import mnist
from kmeans import kMeans
from slackclient import SlackClient
from download_img import download_img

# instantiate Slack client
BOT_TOKEN = os.environ.get('APP_BOT_USER_TOKEN')
slack_client = SlackClient(BOT_TOKEN)
# starterbot's user ID in Slack: value is assigned after the bot starts up
bot_name = None

# constants
RTM_READ_DELAY  = 2 # second delay between reading from RTM
HELP_COMMAND    = 'help'
MNIST_COMMAND   = 'mnist'
KMEANS_COMMAND  = 'kmeans'
JOKE_COMMAND    = 'joke'
MENTION_REGEX   = '^<@(|[WU].+?)>(.*)'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

def check_url(url):
    """
    Returns True if the url returns a response code between 200-300,
    otherwise return False.

    author: Matto Todd
    """
    
    if url[0] == '<':
        url = url[1:-1]

    # TODO consier replacing with requests library
    try:
        response = requests.get(url, headers=HEADERS)
    except ConnectionError:
        return False

    if 200 <= response.status_code <= 200:
        return True

    return False

def parse_bot_commands(slack_events):
    """
    Parses a list of events coming from the Slack RTM API to find bot commands.
    If a bot command is found, this function returns a tuple of command and 
    channel. If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event['type'] == 'message' and not 'subtype' in event:
            user_name, message = parse_direct_mention(event['text'])
            if user_name == bot_name:
                # download a file if it was present in the message
                if 'files' in event:
                    # file is present
                    f = event['files'][0]
                    download_image(f['url_private_download'])
                #try:
                #    f = event['files'][0]
                #    download_image(f['url_private_download'])
                #except KeyError:
                #    # no file is present in the message
                #    pass
                return message, event['channel']
    return None, None

def parse_direct_mention(message_text):
    """
    Finds a direct mention (a mention that is at the beginning) in message text
    and returns the user ID which was mentioned. If there is no direct mention, 
    returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username
    # the second group contains the remaining message
    if matches:
        return (matches.group(1), matches.group(2).strip())
    else:
        return (None, None)

def handle_command(command, channel):
    """
    Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = 'Unknown command. Try @ritai {}'.format(KMEANS_COMMAND)
    error_response = 'There\'s been an error. Whoops, please edit.'

    try:
        if command.startswith(HELP_COMMAND):
            bot_help(command, channel)

        elif command.startswith(MNIST_COMMAND):
            bot_mnist(command, channel)
        
        elif command.startswith(KMEANS_COMMAND):
            bot_kmeans(command, channel)

        elif command.startswith(JOKE_COMMAND):
            bot_joke(command, channel)

        else:
            respond(default_response, channel)
    except Exception:
        # we don't want the bot to crash because we cannot easily restart it
        # this default response will at least make us aware that there's an 
        # error happening, so we can hopefully replicate and fix it on the 
        # dev version of the bot
        err = traceback.format_exc()
        with open('elog.txt', 'a') as elog:
            elog.write(err + '\n\n')
        print(err)
        respond(error_response, channel)

def respond(message, channel):
    """
    Shorthand for posting a response
    """
    slack_client.api_call(
        'chat.postMessage',
        channel=channel,
        text=message
    )

def download_image(img_url):
    """
    Download an image from a url
    """

    # sometimes slack packages urls in messages in brackets
    # these will cause an error unless we remove them
    if img_url[0] == '<':
        img_url = img_url[1:-1]
    
    headers = {'Authorization': 'Bearer %s' % BOT_TOKEN}
    response = requests.get(img_url, headers=headers)
    with open('in.png', 'wb') as image:
        image.write(response.content)

def bot_help(command, channel):
    """
    Prints help command, in case the user would like to know more about a 
    particular capability of the bot
    """
    command_list = command.split(' ')
    
    # default response
    message =   'Available commands:\n' +\
                '\t@ritai help [command]\n' +\
                '\t\tprints this message, or more info about a command\n' +\
                '\t@ritai kmeans [image_url] [k_value]\n' +\
                '\t\tperforms k-means clustering over an image\n' +\
                '\t@ritai mnist [image_url]\n' +\
                '\t\tguesses what number is in an image\n'
    
    # specific responses to particular commands
    if len(command_list) == 2:
        if command_list[1] == HELP_COMMAND:
            message =   'Okay, now you\'re just being silly.'

        if command_list[1] == KMEANS_COMMAND:
            message =   'usage:\n' +\
                        '\t@ritai kmeans [k_value]\n' +\
                        '\t\tperform k-means over latest attachment\n' +\
                        '\t@ritai kmeans [image_url] [k_value]\n' +\
                        '\t\tperform k-means over image in url\n' +\
                        '\tNOTE: k_value must be in range [1-10]\n' +\
                        '\tNOTE: omit k_value to have it chosen randomly'
        
        if command_list[2] == MNIST_COMMAND:
            message =   'usage:\n' +\
                        '\t@ritai mnist\n' +\
                        '\t\tguess what number is in latest attachment\n' +\
                        '\t@ritai mnist [image_url]\n' +\
                        '\t\tguess what number is in image in url\n'

    respond(message, channel)

def bot_mnist(command, channel):
    """
    Uses a rudimentary neural net to guess which number is in an image.
    """
    command_list = command.split(' ')

    img_url = None

    # was an image url provided?
    if len(command_list) > 1:
        img_url = command_list[1]
    # warn user if they entered too many arguments
    if len(command_list) > 2:
        respond('Invalid number of arguments: %d' % len(command_list), channel)
        return

    # validate url
    if img_url and not check_url(img_url):
        respond('Could not validate url. Are you sure it is correct?', channel)
        return
    
    if img_url: download_image(img_url) 
    
    # perform mnist
    img = misc.imread('in.png', flatten=True)
    prediction = mnist.query(img)

    # report prediction
    respond('I think this is a... %d.' % prediction, channel)

def bot_kmeans(command, channel):
    """
    Performs k-means clustering over a given image input (color simplification)

    If an image URL is provided, it attempts to download from that URL. 
    Otherwise, it assumes an attachment was added to the original message.

    If a k value was provided, it uses that k value. Otherwise, it choses
    a random one.
    """
    command_list = command.split(' ')

    img_url = None
    k_value = None

    # was an image url provided?
    if len(command_list) > 1:
        img_url = command_list[1]
    # was a k value provided?
    if len(command_list) > 2:
        k_value = command_list[2]
    # warn the user if too many arguments were provided
    if len(command_list) > 3:
        respond('Invalid numer of arguments: %d' % len(command_list), channel)
        return
    
    # validate url and k-value, as necessary

    # if the url is only a few characters, it was probably the k value
    if img_url and len(img_url) < 5:
        k_value = img_url
        img_url = None

    if img_url and not check_url(img_url):
        respond('Could not validate url.', channel)
        return

    if k_value:
        try:
            k_value = int(k_value)
        except ValueError:
            respond('K value must be an integer')
            return
        if not (0 < k_value < 11):
            respond('K value must be between 1 and 10 inclusive.', channel)
            return
    else:
        k_value = (int)(np.random.normal(7, 3))
        if k_value < 1: k_value = 1
        if k_value > 10: k_value = 10

    # acquire image (if no url, assume image has already been downloaded)
    if img_url: download_image(img_url)

    # perform kMeans
    im = misc.imread('in.png')
    newIm = kMeans(im, k_value)
    misc.imsave('out.png', newIm)

    # post image to channel
    with open('out.png', 'rb') as f:
        slack_client.api_call(
            'files.upload',
            channels=[channel],
            filename='out.png',
            title='output',
            initial_comment=('k: %d' % k_value),
            file=f
        )

def bot_joke(command, channel):
    """
    Has the bot try to tell a joke using a joke database and a Markov chain.

    The user can provide a seed if desired.
    """

    command_list = command.split(' ')

    seed = None
    response = None

    # markov samples can be seeded by a provided string
    if len(command_list) > 1:
        seed = ' '.join(command_list[1:])

    if seed:
        response = joke.joke_with_seed(seed)
    else:
        response = joke.joke()

    respond(response, channel)

if __name__ == '__main__':
    # try to connect to slack
    if slack_client.rtm_connect(with_team_state=False):
        # Read bot's user ID by calling Web API method `auth.test`
        bot_name = slack_client.api_call('auth.test')['user_id']
        # connection is successful
        print('ritai-bot connected and running!')
        while True:
            # loop forever, checking for mentions every RTM_READ_DELAY
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                print(command)
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print('Connection failed. Exception traceback printed above.')
