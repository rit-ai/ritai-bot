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
from . import const
from . import command
from . import transmit

TIME_FORMAT = '%H:%M:%S'
ELOG_CHANNEL = 'test_bots'

def log(s):
    '''More informative print debugging'''
    print('[%s]: %s' % (time.strftime(TIME_FORMAT, time.localtime()), str(s)))

def post_error(error, client):
    '''Posts stack trace to a channel dedicated to bot maintenance'''
    channels = client.api_call('conversations.list', exclude_archived=1)['channels']
    elog_channel = None
    for channel in channels:
        if channel['name'] == ELOG_CHANNEL:
            elog_channel = channel['id']
            break
    if not elog_channel:
        log('WARNING: No channel in which to log errors!')

    error = '```\n' + error + '```' # makes it look fancy, I think

    client.api_call(
        'chat.postMessage',
        channel=elog_channel,
        text=error,
    )

def parse_bot_commands(slack_events, bot_name, bot_token):
    '''
    Parses a list of events coming from the Slack RTM API to find bot commands.
    If a bot prompt is found, this function returns a tuple of prompt and 
    channel. If its not found, then this function returns None, None.
    '''
    for event in slack_events:
        if event['type'] == 'message' and not 'subtype' in event:
            user_name, message = parse_direct_mention(event['text'])
            if user_name == bot_name:
                # log(event)
            
                # download a file if it was present in the message
                if 'files' in event:
                    # file is present
                    f = event['files'][0]
                    transmit.download_image(f['url_private_download'], bot_token)
                
                # reply to the parent thread, not the child thread
                if 'thread_ts' in event:
                    thread = event['thread_ts']
                else:
                    thread = event['ts']

                return message, event['channel'], thread
    return None, None, None

def parse_direct_mention(message_text):
    '''
    Finds a direct mention (a mention that is at the beginning) in message text
    and returns the user ID which was mentioned. If there is no direct mention, 
    returns None
    '''
    matches = re.search(const.MENTION_REGEX, message_text)
    # the first group contains the username
    # the second group contains the remaining message
    if matches:
        return (matches.group(1), matches.group(2).strip())
    else:
        return (None, None)

def handle_prompt(prompt, channel, client, thread):
    '''
    Executes bot prompt if the prompt is known. The bot runs continuously and 
    logs errors to a file.
    '''
    # Default response is help text for the user
    default_response = 'Unknown prompt. Try @ritai {}'.format(const.HELP_PROMPT)
    error_response = 'There\'s been an error. Whoops, please edit.'

    try:
        if prompt.startswith(const.HELP_PROMPT):
            command.bot_help(prompt, channel, client, thread)

        elif prompt.startswith(const.KMEANS_PROMPT):
            command.bot_kmeans(prompt, channel, client, thread)

        elif prompt.startswith(const.MNIST_PROMPT):
            command.bot_mnist(prompt, channel, client, thread)

        elif prompt.startswith(const.JOKE_PROMPT):
            command.bot_joke(prompt, channel, client, thread)
            
        elif prompt.startswith(const.STYLIZE_PROMPT):
            command.bot_stylize(prompt, channel, client, thread)
        
        elif prompt.startswith(const.ERROR_PROMPT):
            raise Exception('please edit')

        else:
            command.respond(default_response, channel, client, thread)
    except Exception:
        # we don't want the bot to crash because we cannot easily restart it
        # this default response will at least make us aware that there's an 
        # error happening, so we can hopefully replicate and fix it on the 
        # dev version of the bot
        err = traceback.format_exc()
        if not os.path.isdir(const.LOG_PATH):
            os.makedirs(const.LOG_PATH)
        with open(const.LOG_PATH / 'elog.txt', 'a') as elog:
            elog.write('[%s]: %s\n' % (time.strftime(TIME_FORMAT, time.localtime()), prompt))
            elog.write('[%s]: %s\n' % (time.strftime(TIME_FORMAT, time.localtime()), err))
        post_error(err, client)
        log(err)
        command.respond(error_response, channel, client, thread)

def main(access_token=None, bot_user_token=None):
    # if the environment variables we need to log in were provided, set them
    if access_token:
        os.environ['APP_ACCESS_TOKEN'] = access_token
    if bot_user_token:
        os.environ['APP_BOT_USER_TOKEN'] = bot_user_token
        
    bot_token = os.environ.get('APP_BOT_USER_TOKEN')
    # instantiate Slack client
    client = SlackClient(bot_token)

    # try to connect to slack
    if client.rtm_connect(with_team_state=False):
        # Read bot's user ID by calling Web API method `auth.test`
        bot_name = client.api_call('auth.test')['user_id']
        # connection is successful
        log('ritai-bot connected and running!')

        while True:
            # loop forever, checking for mentions every RTM_READ_DELAY
            prompt, channel, thread = parse_bot_commands(client.rtm_read(), bot_name, bot_token)
            if prompt:
                log(prompt)
                handle_prompt(prompt, channel, client, thread)
            time.sleep(const.RTM_READ_DELAY)
            
    else:
        log('Connection failed. Exception traceback printed above.')

if __name__ == '__main__':
    main()