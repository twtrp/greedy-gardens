from src.library.essentials import *
from src.template.BaseState import BaseState
from src.classes.Button import Button
from src.classes.SettingsManager import SettingsManager

class Menu_SettingsState(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)
        self.settings_manager = SettingsManager()
        print(self.game.settings)

        self.page_title = utils.get_text(text='Settings', font=fonts.lf2, size='huge', color=colors.yellow_light,
                                         long_shadow=True, outline=True)
        
        self.settings_options_list = [
            {
                
            }
        ]
        
        self.button_surface_list = [
            {
                'id': 'reset',
                'surface': utils.get_text(text='Reset', font=fonts.lf2, size='medium', color=colors.white,
                                          long_shadow=True, outline=True),
                'scale': 1.0,
            },
            {
                'id': 'back',
                'surface': utils.get_text(text='Back', font=fonts.lf2, size='medium', color=colors.white,
                                          long_shadow=True, outline=True),
                'scale': 1.0,
            }
        ]
        
        self.button_list = [
            
        ]
        
    #Main methods

    def update(self, dt, events):
        utils.set_cursor(cursor=self.cursor)
        self.cursor = cursors.normal


    def render(self, canvas):
        utils.blit(dest=canvas, source=self.page_title, pos=(constants.canvas_width/2, 120), pos_anchor='center')
        for i, surface in enumerate(self.button_surface_list):
            utils.blit(dest=canvas, source=surface['surface'], pos=(constants.canvas_width/2, 520 + i*60), pos_anchor='center')
