import os
from bot import bot

if __name__ == '__main__':
    access_token                        = os.environ.get('APP_ACCESS_TOKEN', '<app_secret>')
    bot_user_token                      = os.environ.get('APP_BOT_USER_TOKEN', '<bot_user_secret>')
    bot.main(access_token, bot_user_token)
