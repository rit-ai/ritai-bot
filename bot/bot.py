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
from slack import WebClient


# project-specific libraries
from . import const
from .skill.help import help
from .skill.mnist import mnist
from .skill.kmeans import kmeans
from .skill.stylize import stylize
from .skill.caption import caption


TIME_FORMAT = '%H:%M:%S'
ELOG_CHANNEL = 'test_bots'
# A dictionary of string prompts mapping to functions
CATALOGUE = {
    const.HELP_PROMPT       : help.SkillHelp(),
    const.KMEANS_PROMPT     : kmeans.SkillKmeans(),
    const.MNIST_PROMPT      : mnist.SkillMnist(),
    const.STYLIZE_PROMPT    : stylize.SkillStylize(),
    const.CAPTION_PROMPT    : caption.SkillCaption()
}

def log(s):
    '''More informative print debugging'''
    print('[%s]: %s' % (time.strftime(TIME_FORMAT, time.localtime()), str(s)))

def post_error(error, client):
    '''Posts stack trace to a channel dedicated to bot maintenance'''
    channels = client.api_call(method='conversations.list', exclude_archived=1)['channels']
    if channels:
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
    
def download_attached_image(img_url, bot_token):
    '''Downloads an image from a url'''
    # sometimes slack packages urls in messages in brackets
    # these will cause an error unless we remove them
    if img_url[0] == '<':
        img_url = img_url[1:-1]
    
    headers = {'Authorization': 'Bearer %s' % bot_token}
    response = requests.get(img_url, headers=headers)
    
    if not os.path.isdir(const.TEMP_PATH):
        os.makedirs(const.TEMP_PATH)
    
    with open(const.TEMP_PATH / const.IN_IMG_NAME, 'wb') as image:
        image.write(response.content)

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
                # download a file if it was present in the message
                if 'files' in event:
                    # file is present
                    f = event['files'][0]
                    download_attached_image(f['url_private_download'], bot_token)
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

def handle_prompt(prompt, info):
    '''
    Executes bot prompt if the prompt is known. The bot runs continuously and 
    logs errors to a file.
    '''    
    
    # Help is a special Skill that we use to inform the user as to what the bot
    # can and cannot do
    Help = CATALOGUE[const.HELP_PROMPT]
    Help.set_info(info)

    try:
        # get the first and second words of the sent message (if they exist)
        words = prompt.split(' ')
        firstword = words[0]
        if len(words) > 1:
            secondword = words[1]
        else:
            secondword = None
        
        # if the first word is asking for clarification, print a message
        if firstword == const.HELP_PROMPT:
            # send clarification about a command
            if secondword and secondword in CATALOGUE.keys():
                CATALOGUE[secondword].set_info(info)
                CATALOGUE[secondword].help()
            # send general clarification
            else:
                Help.help(info)

        elif prompt.startswith(const.ERROR_PROMPT):
            raise Exception('please edit')
  
        # if we recognize the command, then execute it
        elif firstword in CATALOGUE.keys():
            CATALOGUE[firstword].set_info(info)
            CATALOGUE[firstword].execute(prompt)

        # otherwise, warn the user that we don't understand
        else:
            Help.execute(prompt)
    
    except Exception:
        # we don't want the bot to crash because we cannot easily restart it
        # this default response will at least make us aware that there's an 
        # error happening, so we can hopefully replicate and fix it on the 
        # dev version of the bot
        err = traceback.format_exc()
        if not os.path.isdir(const.LOG_PATH):
            os.makedirs(const.LOG_PATH)
        with open(str(const.LOG_PATH / 'elog.txt'), 'a') as elog:
            elog.write('[%s]: %s\n' % (time.strftime(TIME_FORMAT, time.localtime()), prompt))
            elog.write('[%s]: %s\n' % (time.strftime(TIME_FORMAT, time.localtime()), err))
        post_error(err, info[const.INFO_CLIENT])
        log(err)
        Help.error()

def main(access_token=None, bot_user_token=None):
    # if the environment variables we need to log in were provided, set them
    if access_token:
        os.environ['APP_ACCESS_TOKEN'] = access_token
    if bot_user_token:
        os.environ['APP_BOT_USER_TOKEN'] = bot_user_token
        
    bot_token = os.environ.get('APP_BOT_USER_TOKEN')
    # instantiate Slack client
    client = SlackClient(bot_token)

def launch_bot():
    try:
        bot_token = os.environ.get('APP_BOT_USER_TOKEN')
        # instantiate Slack client
        client = WebClient(bot_token)

        # try to connect to slack
        if client.rtm_connect(with_team_state=False):
            # Read bot's user ID by calling Web API method `auth.test`
            bot_name = client.api_call('auth.test')['user_id']
            # connection is successful
            log('ritai-bot connected and running!')
            
        return True
    except:
        log('Connection failed. Exception traceback printed above.')
        return False

def main():
    if launch_bot(access_token, bot_user_token):
        while True:
            # loop forever, checking for mentions every RTM_READ_DELAY
            prompt, channel, thread = parse_bot_commands(client.rtm_read(), bot_name, bot_token)
            if prompt:
                log(prompt)
                # info is an object that lets the bot keep track of who it's responding to.
                info = {
                    const.INFO_CLIENT: client, 
                    const.INFO_CHANNEL: channel, 
                    const.INFO_THREAD: thread
                }
                handle_prompt(prompt, info)
            time.sleep(const.RTM_READ_DELAY)
            
    else:
        log('Connection failed. Exception traceback printed above.')

if __name__ == '__main__':
    main()
