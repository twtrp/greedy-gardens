from src.library.essentials import *
from src.template.BaseState import BaseState
from src.classes.Button import Button

class Menu_PlayState(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)


    #Main methods

    def load_assets(self):

        self.page_title = utils.get_text(text='Play', font=fonts.lf2, size='huge', color=colors.green_light)

        self.title_button_option_list = [
            {
                'id': 'start',
                'text': 'Start Game',
            }
        ]


        # Load menu options        
        self.title_button_option_list = [
            {
                'id': 'play',
                'text': 'Play',
            },
            {
                'id': 'records',
                'text': 'Records',
            },
            {
                'id': 'settings',
                'text': 'Settings',
            },
            {
                'id': 'quit',
                'text': 'Quit',
            },
        ]
        self.title_button_option_surface_list = []
        for option in self.title_button_option_list:
            text = utils.get_text(text=option['text'], font=fonts.lf2, size='medium', color=colors.white)
            self.title_button_option_surface_list.append({
                'id': option['id'],
                'surface': text,
                'scale': 0.5,
                'alpha': 0,
            })
        

    def update(self, dt, events):
        utils.set_cursor(cursor=self.cursor)
        self.cursor = cursors.normal


    def render(self, canvas):
        pass