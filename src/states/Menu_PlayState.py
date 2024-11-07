from src.library.essentials import *
from src.template.BaseState import BaseState
from src.classes.Button import Button
from src.classes.SettingsManager import SettingsManager
from src.states.PlayState import PlayState

class Menu_PlayState(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)
        self.settings_manager = SettingsManager()
        self.current_settings_index = self.settings_manager.load_all_settings_index()
        print(self.game.settings)
        print(self.current_settings_index)

        self.load_assets()

    #Main methods

    def load_assets(self):

        self.page_title = utils.get_text(text='Play', font=fonts.lf2, size='huge', color=colors.green_medium)
        
        self.plays_option_list = [
            {
                'id': 'start',
                'text': 'Start',
            }
        ]

        self.plays_option_surface_list = []
        for option in self.plays_option_list:
            text = utils.get_text(text=option['text'], font=fonts.lf2, size='medium', color=colors.white)
            self.plays_option_surface_list.append({
                'id': option['id'],
                'surface': text,
                'scale': 1.0
            })
            
        self.button_option_list = [
            {
                'id': 'back',
                'text': 'Back',
            }
        ]

        self.button_option_surface_list = []
        for option in self.button_option_list:
            text = utils.get_text(text=option['text'], font=fonts.lf2, size='medium', color=colors.white)
            self.button_option_surface_list.append({
                'id': option['id'],
                'surface': text,
                'scale': 1.0
            })
        
        self.button_list = []
        for i, option in enumerate(self.plays_option_surface_list):
            self.button_list.append(Button(game=self.game,
                                           id=option['id'],
                                           surface=option['surface'],
                                           width=300,
                                           height=60,
                                           pos=(constants.canvas_width/2, 300 + i*65),
                                           pos_anchor='center',
                                           hover_cursor=cursors.normal))
        for i, option in enumerate(self.button_option_surface_list):
            self.button_list.append(Button(game=self.game,
                                           id=option['id'],
                                           surface=option['surface'],
                                           width=300,
                                           height=60,
                                           pos=(constants.canvas_width/2, 515 + i*65),
                                           pos_anchor='center'))


    def update(self, dt, events):
        for button in self.button_list:
            button.update(dt=dt, events=events)
            
            if button.hovered:
                self.cursor = button.hover_cursor

                for option in self.plays_option_surface_list:
                    if button.id == option['id']:
                        option['scale'] = min(option['scale'] + 2.4*dt, 1.2)

                for option in self.button_option_surface_list:
                    if button.id == option['id']:
                        option['scale'] = min(option['scale'] + 2.4*dt, 1.2)
            else:
                for option in self.plays_option_surface_list:
                    if button.id == option['id']:
                        option['scale'] = max(option['scale'] - 2.4*dt, 1.0)

                for option in self.button_option_surface_list:
                    if button.id == option['id']:
                        option['scale'] = max(option['scale'] - 2.4*dt, 1.0)
            
            if button.clicked:
                if button.id == 'start':
                    PlayState(game=self.game, parent=self.game, stack=self.game.state_stack).enter_state()
                    self.exit_state()                  
                elif button.id == 'back':
                    self.exit_state()
        utils.set_cursor(cursor=self.cursor)
        self.cursor = cursors.normal


    def render(self, canvas):
        utils.blit(dest=canvas, source=self.page_title, pos=(constants.canvas_width/2, 120), pos_anchor='center')
        for i, option in enumerate(self.plays_option_surface_list):
            processed_surface = pygame.transform.scale_by(surface=option['surface'], factor=option['scale'])
            utils.blit(dest=canvas, source=processed_surface, pos=(constants.canvas_width/2, 300 + i*65), pos_anchor='center')
        for i, option in enumerate(self.button_option_surface_list):
            processed_surface = pygame.transform.scale_by(surface=option['surface'], factor=option['scale'])
            utils.blit(dest=canvas, source=processed_surface, pos=(constants.canvas_width/2, 515 + i*65), pos_anchor='center')
