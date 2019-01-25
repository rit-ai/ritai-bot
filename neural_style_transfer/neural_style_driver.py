# import the necessary packages
import argparse
import imutils
import time
import cv2

def style_transfer(img, ckpt):
    # load the neural style transfer model from disk
    net = cv2.dnn.readNetFromTorch(ckpt)
    
    # load the input image, resize it to have a width of 600 pixels, and
    # then grab the image dimensions
    image = cv2.imread(img)
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
    
    cv2.imwrite('out.png', output * 255)

if __name__ == '__main__':
    style_transfer('in.png', 'models/eccv16/starry_night.t7')