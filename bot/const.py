# author: Paul Galatic
#
# contains constants for ritai-bot

import os

VERSION = '0.6'
BOT_TOKEN = os.environ.get('APP_BOT_USER_TOKEN')
CWD = os.getcwd() + '\\'

# shared
HELP_PROMPT     = 'help'
KMEANS_PROMPT   = 'kmeans'
MNIST_PROMPT    = 'mnist'
STYLIZE_PROMPT  = 'stylize'
JOKE_PROMPT     = 'joke'
ERROR_PROMPT    = 'whoops'

HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

LOG_PATH = 'logs\\'
MODEL_PATH = CWD + 'stylize\\models\\'
STORAGE_PATH = CWD + 'images\\storage\\'
TEMP_PATH = CWD + 'images\\temp\\'
DEFAULT_PATH = CWD +'images\\default\\'

# bot.py
RTM_READ_DELAY  = 2 # second delay between reading from RTM
MENTION_REGEX = '^<@(|[WU].+?)>(.*)'

# command.py
DEFAULT_IMG_NAME = 'default.png'
IN_IMG_NAME = 'in.png'
OUT_IMG_NAME = 'out.png'

HELP_COMMAND = ''
