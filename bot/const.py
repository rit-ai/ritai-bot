# author: Paul Galatic
#
# contains constants for ritai-bot

import os
import pathlib

VERSION = '0.8'
CWD = pathlib.Path(os.getcwd()) / 'bot'

# shared
HELP_PROMPT     = 'help'
KMEANS_PROMPT   = 'kmeans'
MNIST_PROMPT    = 'mnist'
STYLIZE_PROMPT  = 'stylize'
CAPTION_PROMPT  = 'caption'
ERROR_PROMPT    = 'whoops'
STASH_PROMPT    = 'stash'

INFO_CLIENT = 'client'
INFO_CHANNEL = 'channel'
INFO_THREAD = 'thread'

HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

LOG_PATH        = CWD / 'logs'
MODEL_PATH      = CWD / 'stylize' / 'models'
STORAGE_PATH    = CWD / 'images' / 'storage'
TEMP_PATH       = CWD / 'images' / 'temp'
DEFAULT_PATH    = CWD / 'images' / 'default'

# bot.py
RTM_READ_DELAY  = 2 # second delay between reading from RTM
MENTION_REGEX = '^<@(|[WU].+?)>(.*)'

# command.py
DEFAULT_IMG_NAME = 'default.png'
IN_IMG_NAME = 'in.png'
OUT_IMG_NAME = 'out.png'

HELP_COMMAND = ''
