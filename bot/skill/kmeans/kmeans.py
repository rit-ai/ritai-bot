# author: Dan Giaime
# author: Paul Galatic
#
# Program to perform K-means image cartoonization, integrated as a Bot Skill
#

# standard lib

# required lib
import numpy as np
from scipy import misc

# project lib
from .. import skill

def closest_centroids(points, centroids):
    '''
    Given a collection of points and centroids, finds the closest centroids
    to each point and returns those collections. Note that this is computed 
    in COLOR SPACE, not actual proximity.
    '''
    # get the sum of the squared differences between each point
    differences = points - centroids[:, np.newaxis, np.newaxis]
    squareDifferences = differences**2
    summedSquaredDifferences = squareDifferences.sum(axis=3)
    
    # apply square root to complete euclidean distance formula
    finalDistances = np.sqrt(summedSquaredDifferences)
    return np.argmin(finalDistances, axis=0)

def move_centroids(points, closest, centroids):
    '''
    After each iteration, the centroids are adjusted to the center of their
    constituent points.
    '''
    newCentroids = []
    for idx in range(centroids.shape[0]):
        # find which points are in group idx
        indices = (closest == idx)
        # get all points that are in group idx
        correspondingPoints = points[indices]
        # average rgb values
        average = correspondingPoints.mean(axis=0)
        # add to new centroids list
        newCentroids.append(average)

    # Return the resulting centroids.
    return np.array(newCentroids)

def initialize_centroids(points, k_value):
    '''
    Choose a number of random colors from the collection of all colors in 
    the image.
    '''
    # ensure unique centroids are chosen
    centroids = np.unique(points.reshape(-1, points.shape[2]), axis=0)
    np.random.shuffle(centroids)
    return centroids[:k_value]

def set_to_centroids(points, centroids, closestCentroids):
    '''
    Once all the points have been assigned a centroid and the maximum 
    number of iterations has been reached, then it is time to create a new
    image with only the colors of the centroids.
    '''
    # construct a blank image
    newPoints = np.zeros(points.shape)
    (x, y) = closestCentroids.shape
    
    # for each point in that image, set it to be the color of the centroid
    # representing it
    for i in range(x):
        for j in range(y):
            newPoints[i][j] = centroids[closestCentroids[i][j]]

    return newPoints

def k_means(points, k_value, maxIter=10):
    '''
    Driver for the kmeans algorithm. Applies kmeans to an image and then
    displays the result.
    '''
    # initialize centroids randomly
    centroids = initialize_centroids(points, k_value)

    # kmeans runs for a number of iterations. For each iteration, first the 
    # points are assigned to a centroid, and then the centroids are moved
    # to better reflect the points assigned to them.
    for idx in range(0, maxIter):
        # print("Iteration: " + str(idx + 1))
        closestCentroids = closest_centroids(points, centroids)
        centroids = move_centroids(points, closestCentroids, centroids)

    # Get the final, cartoonized image.
    finalPoints = set_to_centroids(points, centroids, closestCentroids)
    return finalPoints

class SkillKmeans(skill.Skill):
    
    def help(self):
        self.respond(
            'usage:\n' +\
                '\t@ritai kmeans [k_value] <image>\n' +\
                '\t\tI will perform k-means color simplification on the attached image.\n' +\
                '\tNOTE: k_value must be in range [1-10].\n' +\
                '\tNOTE: If k_value is not an integer, I will choose one randomly.\n'
        )
    
    def execute(self, prompt):
        '''
        Performs k-means clustering over a given image input (color simplification)

        If an image URL is provided, it attempts to download from that URL. 
        Otherwise, it assumes an attachment was added to the original message.

        If a k value was provided, it uses that k value. Otherwise, it choses
        a random one.
        '''
        prompt_list = prompt.split(' ')

        img_url = None
        k_value = None
        
        # was an k value provided?
        if len(prompt_list) > 1:
            k_value = prompt_list[1]
        # warn the user if too many arguments were provided
        if len(prompt_list) > 2:
            self.respond('Invalid numer of arguments: %d' % len(prompt_list))
            return

        # validate k_value
        if k_value:
            try:
                k_value = int(k_value)
                if not (0 < k_value < 11):
                    self.respond('K value must be between 1 and 10 inclusive.')
                    return
            except ValueError:
                k_value = None
        if not k_value:
            k_value = (int)(np.random.normal(7, 3))
            if k_value < 1: k_value = 1
            if k_value > 10: k_value = 10

        # perform kMeans
        img = self.read_image()
        output = k_means(img, k_value)
        self.write_image(output)
        
        self.upload_image(('k: %d' % k_value))

def main():
    # get input
    imageName = input("Please enter image name: ")
    points = misc.imread(imageName) # width x height x 3 array
    k_value = int(input("Please enter k: ")) # number of groups

    # copy points and save them
    newPoints = k_means(points, k_value)

    # same new pixels to new image
    misc.imsave("outfile.jpg", newPoints)

if __name__ == '__main__':
    main()
