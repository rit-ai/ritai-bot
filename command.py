# author: Paul Galatic
# 
# File for storing bot commands in a way that segments them from the rest of
# the program. The commands are designed to be self-contained.

from joke import joke
from mnist import mnist
from kmeans import kMeans

HELP_COMMAND = 'help'
KMEANS_COMMAND = 'kmeans'
MNIST_COMMAND = 'mnist'
STYLIZE_COMMAND = 'stylize'

def respond(message, channel, client):
    """
    Shorthand for posting a response
    """
    client.api_call(
        'chat.postMessage',
        channel=channel,
        text=message
    )

def download_image(img_url):
    """
    Download an image from a url
    """

    # sometimes slack packages urls in messages in brackets
    # these will cause an error unless we remove them
    if img_url[0] == '<':
        img_url = img_url[1:-1]
    
    headers = {'Authorization': 'Bearer %s' % BOT_TOKEN}
    response = requests.get(img_url, headers=headers)
    with open('in.png', 'wb') as image:
        image.write(response.content)

def bot_help(command, channel, client):
    """
    Prints help command, in case the user would like to know more about a 
    particular capability of the bot
    """
    command_list = command.split(' ')
    
    # default response
    message =   'Available commands:\n' +\
                '\t@ritai help [command]\n' +\
                '\t\tprints this message, or more info about a command\n' +\
                '\t@ritai kmeans\n' +\
                '\t\tperforms k-means clustering over an image\n' +\
                '\t@ritai mnist\n' +\
                '\t\tguesses what number is in an image\n' +\
				'\t@ritai stylize\n' +\
				'\t\tapplies style transfer to an image\n'
    
    # specific responses to particular commands
    if len(command_list) == 1:
		respond(message, channel, client)
	elif len(command_list) > 1:
        if command_list[1] == HELP_COMMAND:
            respond('Okay, now you\'re just being silly.', channel, client)

        if command_list[1] == KMEANS_COMMAND:
            bot_kmeans('', channel, client)
        
        if command_list[2] == MNIST_COMMAND:
            bot_mnist('', channel, client)
		
		respond('Command not recognized.', channel, client)
		
	respond(message, channel, client)

	
def bot_mnist(command, channel, client):
    """
    Uses a rudimentary neural net to guess which number is in an image.
    """
    command_list = command.split(' ')

    img_url = None

    # was an image url provided?
    if len(command_list) > 1:
        img_url = command_list[1]
    # warn user if they entered too many arguments
    if len(command_list) > 2:
        respond('Invalid number of arguments: %d' % len(command_list), channel, client)
        return
	# print help message
	else:
		respond(	
			message='usage:\n' +\
				'\t@ritai mnist\n' +\
				'\t\tguess what number is in latest attachment\n' +\
				'\t@ritai mnist [image_url]\n' +\
				'\t\tguess what number is in image in url\n',
			channel,
			client
		)
		return

    # validate url
    if img_url and not check_url(img_url):
        respond('Could not validate url. Are you sure it is correct?', channel, client)
        return
    
    if img_url: download_image(img_url) 
    
    # perform mnist
    img = misc.imread('in.png', flatten=True)
    prediction = mnist.query(img)

    # report prediction
    respond('I think this is a... %d.' % prediction, channel, client)


def bot_kmeans(command, channel, client):
    """
    Performs k-means clustering over a given image input (color simplification)

    If an image URL is provided, it attempts to download from that URL. 
    Otherwise, it assumes an attachment was added to the original message.

    If a k value was provided, it uses that k value. Otherwise, it choses
    a random one.
    """
    command_list = command.split(' ')

    img_url = None
    k_value = None

    # was an image url provided?
    if len(command_list) > 1:
        img_url = command_list[1]
    # was a k value provided?
    if len(command_list) > 2:
        k_value = command_list[2]
    # warn the user if too many arguments were provided
    if len(command_list) > 3:
        respond('Invalid numer of arguments: %d' % len(command_list), channel)
        return
	# print help message
	else:
		respond(
			message='usage:\n' +\
				'\t@ritai kmeans [k_value]\n' +\
				'\t\tperform k-means over latest attachment\n' +\
				'\t@ritai kmeans [image_url] [k_value]\n' +\
				'\t\tperform k-means over image in url\n' +\
				'\tNOTE: k_value must be in range [1-10]\n' +\
				'\tNOTE: omit k_value to have it chosen randomly',
			channel,
			client
		)
		return
    
    # validate url and k-value, as necessary

    # if the url is only a few characters, it was probably the k value
    if img_url and len(img_url) < 5:
        k_value = img_url
        img_url = None

    if img_url and not check_url(img_url):
        respond('Could not validate url.', channel)
        return

    if k_value:
        try:
            k_value = int(k_value)
        except ValueError:
            respond('K value must be an integer')
            return
        if not (0 < k_value < 11):
            respond('K value must be between 1 and 10 inclusive.', channel)
            return
    else:
        k_value = (int)(np.random.normal(7, 3))
        if k_value < 1: k_value = 1
        if k_value > 10: k_value = 10

    # acquire image (if no url, assume image has already been downloaded)
    if img_url: download_image(img_url)

    # perform kMeans
    im = misc.imread('in.png')
    newIm = kMeans(im, k_value)
    misc.imsave('out.png', newIm)

    # post image to channel
    with open('out.png', 'rb') as f:
        client.api_call(
            'files.upload',
            channels=[channel],
            filename='out.png',
            title='output',
            initial_comment=('k: %d' % k_value),
            file=f
        )
		
def bot_joke(command, channel, client):
    """
    Has the bot try to tell a joke using a joke database and a Markov chain.

    The user can provide a seed if desired.
    """

    command_list = command.split(' ')

    seed = None
    response = None

    # markov samples can be seeded by a provided string
    if len(command_list) > 1:
        seed = ' '.join(command_list[1:])

    if seed:
        response = joke.joke_with_seed(seed)
    else:
        response = joke.joke()

    respond(response, channel, client)

def bot_stylize(command, channel, client):
	respond('Stylize command received!', channel, client)