# USAGE
#  python neural_style_transfer_examine.py --models models --image images/giraffe.jpg 

# import the necessary packages
import os

import imutils
import cv2

IM_DIMS = (240, 240)
MONTAGE_SHAPE = (5, 2)
MODEL_DIR = 'models/'

def parse_args():
    '''construct the argument parser and parse the arguments'''
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--im_name", required=True,
        help="name of input image to apply neural style transfer to")
    return ap.parse_args()
    
if __name__ == '__main__':
    args = parse_args()
    
    models = [MODEL_DIR + name for name in os.listdir(MODEL_DIR)]
    im_name = args.im_name
    out_imgs = []
    
    for model in models:
        # load the neural style transfer model from disk
        # print("[INFO] loading {}...".format(modelPath))
        net = cv2.dnn.readNetFromTorch(model)

        # load the input image, resize it to have a width of 600 pixels,
        # then grab the image dimensions
        image = cv2.imread(im_name)
        image = imutils.resize(image, width=600)
        (h, w) = image.shape[:2]

        # construct a blob from the image, set the input, and then
        # perform a forward pass of the network
        blob = cv2.dnn.blobFromImage(image, 1.0, (w, h),
            (103.939, 116.779, 123.680), swapRB=False, crop=False)
        net.setInput(blob)
        output = net.forward()

        # reshape the output tensor, add back in the mean subtraction,
        # and then swap the channel ordering
        output = output.reshape((3, output.shape[2], output.shape[3]))
        output[0] += 103.939
        output[1] += 116.779
        output[2] += 123.680
        output /= 255.0
        output = output.transpose(1, 2, 0)
        
        out_imgs.append(output * 255)
    
    out_imgs = [image] + out_imgs

    montages = imutils.build_montages(out_imgs, IM_DIMS, MONTAGE_SHAPE)
    
    # show the images
    for montage in montages:
        cv2.imwrite('out.png', montage)
        cv2.imshow("Montage", montage)
        cv2.waitKey(0)
        
        