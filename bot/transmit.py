# author: Paul Galatic
#
# Utilities for reading/serving images to programs

# standard lib
import os

# required lib
import cv2
import requests

# project lib
from bot import const

def download_image(img_url):
    '''Downloads an image from a url'''
    # sometimes slack packages urls in messages in brackets
    # these will cause an error unless we remove them
    if img_url[0] == '<':
        img_url = img_url[1:-1]
    
    headers = {'Authorization': 'Bearer %s' % const.BOT_TOKEN}
    response = requests.get(img_url, headers=headers)
    
    if not os.path.isdir(const.TEMP_PATH):
        os.makedirs(const.TEMP_PATH)
    
    with open(const.TEMP_PATH + const.IN_IMG_NAME, 'wb') as image:
        image.write(response.content)
        
def upload_image(comment, channel, client, thread):
    '''Post image to channel'''
    with open(const.TEMP_PATH + const.OUT_IMG_NAME, 'rb') as img:
        client.api_call(
            'files.upload',
            channels=[channel],
            filename=const.OUT_IMG_NAME,
            title='output',
            initial_comment=comment,
            file=img,
            thread_ts=thread
        )
        
def read_image(fname):
    '''
    Reads in an image. If the image is not present, it returns a default image.
    '''
    img = cv2.imread(const.TEMP_PATH + const.IN_IMG_NAME)
    if img is None: # invalid image paths yield None
        img = cv2.imread(const.DEFAULT_PATH + const.DEFAULT_IMG_NAME)    
    if img is None: # if image is still none, there's a real problem
        raise Exception('Default image is missing in read_image()')
    
    return img
    
def write_image(fname, image):
    '''Writes an image to the temp folder'''
    if not os.path.isdir(const.TEMP_PATH):
        os.makedirs(const.TEMP_PATH)
    
    cv2.imwrite(const.TEMP_PATH + fname, image)