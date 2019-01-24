# author: Paul Galatic
# 
# boilerplate code from:
#   fullstackpython.com
#   https://github.com/mattmakai

# standard libraries
import os
import re
import sys
import pdb
import time

# additional libraries
import requests
import traceback
from slackclient import SlackClient

# project-specific libraries
import command

# instantiate Slack client
BOT_TOKEN = os.environ.get('APP_BOT_USER_TOKEN')
client = SlackClient(BOT_TOKEN)
# starterbot's user ID in Slack: value is assigned after the bot starts up
bot_name = None

# constants
RTM_READ_DELAY  = 2 # second delay between reading from RTM
HELP_COMMAND    = 'help'
MNIST_COMMAND   = 'mnist'
KMEANS_COMMAND  = 'kmeans'
JOKE_COMMAND    = 'joke'
STYLIZE_COMMAND = 'stylize'
MENTION_REGEX = '^<@(|[WU].+?)>(.*)'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

def check_url(url):
    """
    Returns True if the url returns a response code between 200-300,
    otherwise return False.

    author: Matto Todd
    """
    
    if url[0] == '<':
        url = url[1:-1]

    try:
        response = requests.get(url, headers=HEADERS)
    except ConnectionError:
        return False

    if response.status_code <= 200:
        return True

    return False

def parse_bot_commands(slack_events):
    """
    Parses a list of events coming from the Slack RTM API to find bot commands.
    If a bot prompt is found, this function returns a tuple of prompt and 
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
                    command.download_image(f['url_private_download'])
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

def handle_prompt(prompt, channel):
    """
    Executes bot prompt if the prompt is known
    """
    # Default response is help text for the user
    default_response = 'Unknown prompt. Try @ritai {}'.format(KMEANS_COMMAND)
    error_response = 'There\'s been an error. Whoops, please edit.'

    try:
        if prompt.startswith(HELP_COMMAND):
            command.bot_help(prompt, channel, client)

        elif prompt.startswith(KMEANS_COMMAND):
            command.bot_kmeans(prompt, channel, client)

        elif prompt.startswith(MNIST_COMMAND):
            command.bot_mnist(prompt, channel, client)

        elif prompt.startswith(JOKE_COMMAND):
            command.bot_joke(prompt, channel, client)
            
        elif prompt.startswith(STYLIZE_COMMAND):
            command.bot_stylize(prompt, channel, client)

        else:
            command.respond(default_response, channel, client)
    except Exception:
        # we don't want the bot to crash because we cannot easily restart it
        # this default response will at least make us aware that there's an 
        # error happening, so we can hopefully replicate and fix it on the 
        # dev version of the bot
        err = traceback.format_exc()
        with open('elog.txt', 'a') as elog:
            elog.write(err + '\n\n')
        print(err)
        command.respond(error_response, channel, client)

if __name__ == '__main__':
    # try to connect to slack
    if client.rtm_connect(with_team_state=False):
        # Read bot's user ID by calling Web API method `auth.test`
        bot_name = client.api_call('auth.test')['user_id']
        # connection is successful
        print('ritai-bot connected and running!')
        while True:
            # loop forever, checking for mentions every RTM_READ_DELAY
            prompt, channel = parse_bot_commands(client.rtm_read())
            if prompt:
                print(prompt)
                handle_prompt(prompt, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print('Connection failed. Exception traceback printed above.')
