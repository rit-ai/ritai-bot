"""
Adapted from: https://jrusev.github.io/post/hacking-mnist/
"""

import os
import mnist
import pickle
import numpy as np

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

def train():
    trX, trY, teX, teY = mnist.load_data()
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

def main():
    train()

if __name__ == '__main__':
    main()
    print(i, np.mean(prediction == np.argmax(teY, axis=1)))
