
from . import core
from .. import skill

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
            style = core.random.choice(self.styles)
        
        ckpt = core.MODEL_DIR + '{style}.t7'.format(style=style)
        
        # perform style transfer
        img = self.read_image()
        _, output = core.style_transfer(img, ckpt)
        self.write_image(output)
        
        # post image to channel
        self.upload_image(('style: %s' % style))
