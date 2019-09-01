#
# author: Paul Galatic
#
# Test suite designed to verify:
# 1) Can the bot launch?
# 2) Do all the skills work?

from . import bot
from . import const

import traceback as track
from PIL import Image

class MockClient():
    def api_call(self, **kwargs):
        bot.log(f'Message sent via API:\n' +\
            '\n'.join([f'\t{key}:\t{val}' for key, val in kwargs.items()]))
            
MOCK_INFO = {
    const.INFO_CLIENT: MockClient(), 
    const.INFO_CHANNEL: 'MOCK_CHANNEL', 
    const.INFO_THREAD: 'MOCK_THREAD'
}

def gen_mock_image():
    img = Image.new('RGB', (800,1280), (255, 255, 255))
    img.save(const.TEMP_PATH / const.IN_IMG_NAME, 'PNG')

def test_slack_client():
    return bot.launch_bot()

def test_help():
    bot.handle_prompt('help kmeans', MOCK_INFO)

def test_mnist():
    bot.handle_prompt('mnist', MOCK_INFO)

def test_kmeans():
    bot.handle_prompt('kmeans 7', MOCK_INFO)

def test_stylize():
    bot.handle_prompt('stylize', MOCK_INFO)
    bot.handle_prompt('stylize mosaic', MOCK_INFO)

def test_caption():
    bot.handle_prompt('caption', MOCK_INFO)

def test(idx, function):
    bot.log(f'Test {idx}: {function.__name__}')
    try:
        result = function()
        if not result == False:
            bot.log('...success.')
            return
    except:
        track.print_exc()
    bot.log('FAILED.')

def main():
    '''
    The test suite mocks a Slack environment and runs tests locally. This means
    that we don't have to launch the Slackbot and run every command to see if 
    any of them crash.
    '''
    
    # generate a blank image for testing image-manipulation skills
    gen_mock_image()
    
    suite = [
        test_slack_client,
        test_help,
        test_mnist,
        test_kmeans,
        test_stylize,
        test_caption
    ]

    for idx in range(len(suite)):
        test(idx, suite[idx])