# author: Paul Galatic
#
# Skill for testing, debugging, and letting the user know what's going on both
# in general and especially when the commands bug out

from ... import const
from .. import skill

MAX_LEN = 30

class SkillHelp(skill.Skill):
    
    def help(self):
        self.respond(
            'RITAI VERSION [%s]:\n' % const.VERSION +\
                '\t@ritai help [command]\n' +\
                '\t\tprints this message, or more info about a command\n' +\
                '\t@ritai kmeans\n' +\
                '\t\tperforms k-means clustering over an image\n' +\
                '\t@ritai mnist\n' +\
                '\t\tguesses what number is in an image\n' +\
                '\t@ritai stylize\n' +\
                '\t\tapplies neural style transfer to an image\n'
        )
    
    def execute(self, prompt):
        if len(prompt) > MAX_LEN + 3: # add three for the ellipsis
            prompt = '{short}...'.format(short=prompt[:MAX_LEN])
        self.respond('Unknown prompt: {}. Try @ritai help'.format(prompt))
        
    def error(self):
        self.respond('There\'s been an error. Whoops, please edit.')