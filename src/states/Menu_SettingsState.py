from src.library.essentials import *
from src.template.BaseState import BaseState
from src.classes.Button import Button
from src.classes.SettingsManager import SettingsManager

class Menu_SettingsState(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)
        self.settings_manager = SettingsManager()
        self.current_settings_index = self.settings_manager.load_all_settings_index()
        print(self.game.settings)
        print(self.current_settings_index)

        self.load_assets()

        
    #Main methods

    def load_assets(self):

        self.page_title = utils.get_text(text='Settings', font=fonts.lf2, size='huge', color=colors.yellow_light)
        
        self.arrow_left = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='arrow_left')
        self.arrow_right = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='arrow_right')
        
        self.settings_option_surface_list = []
        for i, setting in enumerate(self.settings_manager.settings_list):
            text_string = setting['label']+':  '+setting['value_label'][self.current_settings_index[i]]
            text = utils.get_text(text=text_string, font=fonts.lf2, size='small', color=colors.white)
            self.settings_option_surface_list.append({
                'id': setting['id'],
                'surface': text,
                'arrow_visibility': False,
                'scale': 1.0,
            })
            
        self.button_option_list = [
            {
                'id': 'reset',
                'text': 'Reset',
            },
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
        for i, option in enumerate(self.settings_option_surface_list):
            self.button_list.append(Button(game=self.game,
                                           id=option['id'],
                                           surface=option['surface'],
                                           width=300,
                                           height=50,
                                           pos=(constants.canvas_width/2, 200 + i*50),
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

                for option in self.settings_option_surface_list:
                    if button.id == option['id']:
                        option['arrow_visibility'] = True

                for option in self.button_option_surface_list:
                    if button.id == option['id']:
                        option['scale'] = min(option['scale'] + 2.4*dt, 1.2)
            else:
                for option in self.settings_option_surface_list:
                    if button.id == option['id']:
                        option['arrow_visibility'] = False

                for option in self.button_option_surface_list:
                    if button.id == option['id']:
                        option['scale'] = max(option['scale'] - 2.4*dt, 1.0)
            
            if button.clicked:
                if button.id == 'reset':
                    pass
                elif button.id == 'back':
                    self.exit_state()
        utils.set_cursor(cursor=self.cursor)
        self.cursor = cursors.normal


    def render(self, canvas):
        utils.blit(dest=canvas, source=self.page_title, pos=(constants.canvas_width/2, 120), pos_anchor='center')
        for i, option in enumerate(self.settings_option_surface_list):
            processed_surface = pygame.transform.scale_by(surface=option['surface'], factor=option['scale'])
            utils.blit(dest=canvas, source=processed_surface, pos=(constants.canvas_width/2, 200 + i*50), pos_anchor='center')
            if option['arrow_visibility']:
                utils.blit(dest=canvas,
                           source=self.arrow_left,
                           pos=(constants.canvas_width/2 - option['surface'].width/2 - 36, 200 + i*50),
                           pos_anchor='center')
                utils.blit(dest=canvas,
                           source=self.arrow_right,
                           pos=(constants.canvas_width/2 + option['surface'].width/2 + 36, 200 + i*50),
                           pos_anchor='center')
        for i, option in enumerate(self.button_option_surface_list):
            processed_surface = pygame.transform.scale_by(surface=option['surface'], factor=option['scale'])
            utils.blit(dest=canvas, source=processed_surface, pos=(constants.canvas_width/2, 515 + i*65), pos_anchor='center')
