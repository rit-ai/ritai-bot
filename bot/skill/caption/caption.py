# author: Paul Galatic
#
# Program to perform image captioning, implemented as a bot skill
# source: https://github.com/sgrvinod/a-PyTorch-Tutorial-to-Image-Captioning
#

from .. import skill
from . import models

import os
import pathlib
import requests

def download_gdrive_file(id, destination):
    # source: https://stackoverflow.com/questions/25010369/wget-curl-large-file-from-google-drive/39225039#39225039
    def get_confirm_token(response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value

        return None

    def save_response_content(response, destination):
        CHUNK_SIZE = 32768

        with open(destination, "wb") as f:
            for chunk in response.iter_content(CHUNK_SIZE):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)

    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)
    
    save_response_content(response, destination)

def download_and_extract_model(dest):
    if not os.path.isdir(dest):
        os.mkdir(dest)
    if not os.path.exists(dest / MODEL_NAME):
        download_gdrive_file(MODEL_ID, str(dest / MODEL_NAME))
    if not os.path.exists(dest / WORD_MAP_NAME):
        download_gdrive_file(WORD_MAP_ID, str(dest / WORD_MAP_NAME))

class SkillCaption(skill.Skill):
    
    def __init__(self):
        super().__init__()

    def help(self):
        self.respond(
            'usage:\n' +\
                '\t@ritai caption <image>\n' +\
                '\t\tI will do my best to describe the contents of the image.\n'
        )
        
    def execute(self, prompt):
        '''
        Captions an image using a neural network.
        '''
        prompt_list = prompt.split(' ')
        
        # warn the user if they provided too many arguments
        if len(prompt_list) > 1:
            self.respond('Invalid numer of arguments: %d' % len(prompt_list))
            return
        
        # perform caption
        img = self.read_image()
        caption = 'NOT IMPLEMENTED YET'
        
        # post image to channel
        self.respond(caption)