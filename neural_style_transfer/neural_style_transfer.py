# USAGE
# python neural_style_transfer.py --image images/baden_baden.jpg --model models/instance_norm/starry_night.t7

# import the necessary packages
import random
import time
import os

import imutils
import cv2

MODEL_DIR = 'models/'

def parse_args():
    '''construct the argument parser and parse the arguments'''
    ap = argparse.ArgumentParser()
    ap.add_argument("-m", "--model", required=False,
        help="neural style transfer model")
    ap.add_argument("-i", "--im_name", required=True,
        help="name of input image to apply neural style transfer to")
    return ap.parse_args()

def style_transfer(im_name, ckpt):
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
    
    # load the input image, resize it to have a width of 600 pixels, and
    # then grab the image dimensions
    image = cv2.imread(im_name)
    image = imutils.resize(image, width=600)
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
    
    cv2.imwrite('out.png', output * 255)
    
    return image, output

if __name__ == '__main__':
    args = parse_args()
    
    image, output = style_transfer(args.im_name, args.model)
    
    # show the images
    cv2.imshow("Input", image)
    cv2.imshow("Output", output)

    cv2.waitKey(0)
        