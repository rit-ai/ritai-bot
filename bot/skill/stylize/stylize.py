# author: Paul Galatic
#
# Program to perform K-means image cartoonization, integrated as a Bot Skill
# source: https://www.pyimagesearch.com/2018/08/27/neural-style-transfer-with-opencv/
#

# standard lib
import random
import time
import os

# required lib
import imageio
import imutils
import cv2

# project lib
from .. import skill

MODEL_DIR = 'bot/skill/stylize/models/'

def parse_args():
    '''construct the argument parser and parse the arguments'''
    ap = argparse.ArgumentParser()
    ap.add_argument("-m", "--model", required=False,
        help="neural style transfer model")
    ap.add_argument("-i", "--im_name", required=True,
        help="name of input image to apply neural style transfer to")
    return ap.parse_args()

def style_transfer(image, ckpt):
    '''
    Applies style tranfer.
    
    args
        im_name : the name of an input image
        chkpt   : the name of the model to use for style transfer
    '''
    # if no model is chosen, then choose a random one
    if not ckpt:
        models = os.listdir(MODEL_DIR)
        ckpt = MODEL_DIR + random.choice(models)
    
    # load the neural style transfer model from disk
    # print("[INFO] loading style transfer model...")
    net = cv2.dnn.readNetFromTorch(ckpt)
    
    # resize the image to have a width of 600 pixels, and
    # then grab the image dimensions

    imutils.resize(image, width=600)
    
    (h, w) = image.shape[:2]
    
    # construct a blob from the image, set the input, and then perform a
    # forward pass of the network
    blob = cv2.dnn.blobFromImage(image, 1.0, (w, h),
        (103.939, 116.779, 123.680), swapRB=False, crop=False)
    net.setInput(blob)
    output = net.forward()

    # reshape the output tensor, add back in the mean subtraction, and
    # then swap the channel ordering
    output = output.reshape((3, output.shape[2], output.shape[3]))
    output[0] += 103.939
    output[1] += 116.779
    output[2] += 123.680
    output /= 255.0
    output = output.transpose(1, 2, 0)
    
    # print("[INFO] neural style transfer took {:.4f} seconds".format(end - start))
    
    return image * 255, output * 255

class SkillStylize(skill.Skill):

    def __init__(self):
        self.styles = [ 'candy', 
                        'composition_vii', 
                        'feathers', 
                        'la_muse', 
                        'mosaic', 
                        'starry_night', 
                        'the_scream',
                        'the_wave', 
                        'udnie' ]
        super().__init__()
    
    def help(self):
        self.respond(
            'usage:\n' +\
                '\t@ritai stylize <image>\n' +\
                '\t\tI will stylize the attached image with a random style.\n' +\
                '\t@ritai stylize [style] <image>\n' +\
                '\t\tI will stylize the attached image with a specific style.\n' +\
                '\tNOTE: valid styles include:\n' +\
                '\t' + str(self.styles) + '\n'
        )
        
    def execute(self, prompt):
        '''
        Applies style transfer to an image using a neural network.
        '''
        prompt_list = prompt.split(' ')
        style = None
        
        # what style does the user want?
        if len(prompt_list) > 1:
            desire = prompt_list[1].lower()
            if desire in self.styles:
                style = desire
            else:
                self.respond(
                    'I don\'t recognize the style %s. Try @ritai help ' % desire +\
                    'stylize for available styles.'
                )
                return
        # warn the user if they provided too many arguments
        if len(prompt_list) > 2:
            self.respond('Invalid numer of arguments: %d' % len(prompt_list))
            return
        
        if not style:
            style = random.choice(self.styles)
        
        ckpt = MODEL_DIR + '{style}.t7'.format(style=style)
        
        # perform style transfer
        img = self.read_image()
        _, output = style_transfer(img, ckpt)
        self.write_image(output)
        
        # post image to channel
        self.upload_image(('style: %s' % style))

def main():
    args = parse_args()
    
    img_in = cv2.imread(args.im_name)
    
    image, output = style_transfer(img_in, args.model)
    
    cv2.imwrite('out.png', output)
    
    # show the images
    cv2.imshow("Input", image)
    cv2.imshow("Output", output)

    cv2.waitKey(0)
    
if __name__ == '__main__':
    main()
        