# author: Paul Galatic
#
# Abstract clsas blueprint for writing bot skills, and for aggregating existing
# skills

# standard lib
import os
import abc # Abstract Base Class

# required lib
import cv2

# project lib
from .. import const

class Skill(abc.ABC):
    '''
    The recipe for a bot skill is fairly simple, and this class serves as an 
    accumulator for various utility functions that would otherwise be spread 
    over multiple files, causing import/dependency headaches. Every function
    below is one that most bot skills will find plenty useful.
    '''
    
    def __init__(self):
        super().__init__()        
    
    def set_info(self, info):
        '''
        Grabs response data for the current prompt, so that the same Skill 
        object can be reused.
        '''
        # the slack client, which the bot uses to respond
        self.client = info[const.INFO_CLIENT]
        # the channel in which we are participating
        self.channel = info[const.INFO_CHANNEL]
        # the particular thread we were created to respond to
        self.thread = info[const.INFO_THREAD]
    
    def respond(self, message):
        '''Has the bot post a message.'''
        self.client.api_call(
            method='chat.postMessage',
            channel=self.channel,
            text=message,
            thread_ts=self.thread
        )
    
    def upload_image(self, comment=''):
        '''Has the bot post an image.'''
        with open(str(const.TEMP_PATH / const.OUT_IMG_NAME), 'rb') as img:
            self.client.api_call(
                method='files.upload',
                channels=[self.channel],
                filename=const.OUT_IMG_NAME,
                title='output',
                initial_comment=comment,
                file=img,
                thread_ts=self.thread
            )
            
    def read_image(self, fname=const.IN_IMG_NAME):
        '''
        Reads in an image. If the image is not present, it returns a default image.
        '''
        img = cv2.imread(str(const.TEMP_PATH / const.IN_IMG_NAME))
        if img is None: # invalid image paths yield None
            img = cv2.imread(str(const.DEFAULT_PATH / const.DEFAULT_IMG_NAME))    
        if img is None: # if image is still none, there's a real problem
            raise Exception('Default image is missing in read_image(): {path}'.format(path=const.DEFAULT_PATH / const.DEFAULT_IMG_NAME))
        
        return img
        
    def write_image(self, image, fname=const.OUT_IMG_NAME):
        '''Writes an image to the temp folder'''
        if not os.path.isdir((const.TEMP_PATH)):
            os.makedirs(str(const.TEMP_PATH))
        
        cv2.imwrite(str(const.TEMP_PATH / fname), image)
    
    @abc.abstractmethod
    def help(self):
        '''
        The help() method should provide the user a basic understanding of how 
        to invoke the bot's Skill.
        '''
        pass
        
    @abc.abstractmethod
    def execute(self, prompt):
        '''
        Execute is the bulk of the skill; it's what makes the bot actually 
        perform computations and generate results based on input.
        '''
        pass