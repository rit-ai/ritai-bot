"""
Adapted from: https://jrusev.github.io/post/hacking-mnist/
"""

# standard lib
import os
import sys
import pickle

# required lib
import numpy as np
from scipy import misc

# project lib
from .. import skill

def feed_forward(X, weights):
    a = [X]
    for w in weights:
        a.append(np.maximum(a[-1].dot(w),0))
    return a

def grads(X, Y, weights):
    grads = np.empty_like(weights)
    a = feed_forward(X, weights)
    delta = a[-1] - Y
    grads[-1] = a[-2].T.dot(delta)
    for i in range(len(a)-2, 0, -1):
        delta = (a[i] > 0) * delta.dot(weights[i].T)
        grads[i-1] = a[i-1].T.dot(delta)
    return grads / len(X)

def query(img):
    # gets "true" location of image, regardless of from where the script is
    # being run
    loc = os.path.realpath(
            os.path.join(os.getcwd(), 
            os.path.dirname(__file__))
        )
    path = os.path.join(loc, 'model.pkl')

    if os.path.isfile(path):
        with open(path, 'rb') as model:
            weights = pickle.load(model)
    else:
        raise Exception('Cannot query without existing model!')

    img_smol = misc.imresize(img, [28, 28])

    img_lin = np.resize(img_smol, [1, 784])

    prediction = np.argmax(feed_forward(img_lin, weights)[-1], axis=1)
    
    return prediction[0]

def train():
    import load_data
    trX, trY, teX, teY = load_data.load_data()
    num_epochs, batch_size, learn_rate = 30, 20, 0.1

    if os.path.isfile('model.pkl'):
        print('Loading model...')
        with open('model.pkl', 'rb') as model:
            weights = pickle.load(model)
    else:
        print('Generating model...')
        weights = [np.random.randn(*w) * 0.1 for w in [(784, 100), (100, 10)]]
    
    print('...done.')

    for i in range(num_epochs):
        for j in range(0, len(trX), batch_size):
            X, Y = trX[j:j+batch_size], trY[j:j+batch_size]
            weights -= learn_rate * grads(X, Y, weights)
        
        prediction = np.argmax(feed_forward(teX, weights)[-1], axis=1)
        print(i, np.mean(prediction == np.argmax(teY, axis=1)))

        with open('model.pkl', 'wb') as model:
            pickle.dump(weights, model)
            
class SkillMnist(skill.Skill):
    
    def help(self):
        self.respond(    
            'usage:\n' +\
                '\t@ritai mnist <image>\n' +\
                '\t\tAttach an image and I will guess what number it is!\n'
        )
    
    def execute(self, prompt):
        '''
        Uses a rudimentary neural net to guess which number is in an image.
        '''
        prompt_list = prompt.split(' ')
        
        # warn user if they entered too many arguments
        if len(prompt_list) > 1:
            self.respond('Invalid number of arguments: %d' % len(prompt_list))
            return
        
        # perform mnist
        img = self.read_image()
        prediction = query(img)

        # report prediction
        self.respond('I think this is a... %d.' % prediction)

def main():
    train()

if __name__ == '__main__':
    main()
