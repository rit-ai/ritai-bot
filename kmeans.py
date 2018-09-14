import pdb
import numpy as np
from scipy import misc

def closest_centroids(points, centroids):
    # get differences between each point
    differences = points - centroids[:, np.newaxis, np.newaxis]
    squareDifferences = differences**2
    summedSquaredDifferences = squareDifferences.sum(axis=3)
    finalDistances = np.sqrt(summedSquaredDifferences)
    return np.argmin(finalDistances, axis=0)

def move_centroids(points, closest, centroids):
    newCentroids = []
    for i in range(centroids.shape[0]):
        # find which points are in group i
        indices = (closest == i)
        # get all points that are in group i
        correspondingPoints = points[indices]
        # average rgb values
        average = correspondingPoints.mean(axis=0)
        # add to new centroids list
        newCentroids.append(average)

    return np.array(newCentroids)

def initialize_centroids(points, k):
    (x, y, z) = points.shape
    # ensure unique centroids are chosen
    centroids = np.unique(points.reshape(-1, points.shape[2]), axis=0)
    np.random.shuffle(centroids)
    return centroids[:k]

def set_to_centroids(points, centroids, closestCentroids):
    newPoints = np.zeros(points.shape)
    (x, y) = closestCentroids.shape
    for i in range(x):
        for j in range(y):
            newPoints[i][j] = centroids[closestCentroids[i][j]]

    return newPoints

def kMeans(points, k, maxIter=10):
    # init centroids randomly
    centroids = initialize_centroids(points, k)

    for i in range(0, maxIter):
        # print("Iteration: " + str(i + 1))
        closestCentroids = closest_centroids(points, centroids)
        centroids = move_centroids(points, closestCentroids, centroids)

    finalPoints = set_to_centroids(points, centroids, closestCentroids)
    return finalPoints

def main():
    # get input
    imageName = input("Please enter image name: ")
    points = misc.imread(imageName) # width x height x 3 array
    k = int(input("Please enter k: ")) # number of groups

    # copy points and save them
    newPoints = kMeans(points, k)

    # same new pixels to new image
    misc.imsave("outfile.jpg", newPoints)

if __name__ == '__main__':
    main()
