from src.library.essentials import *
from src.template.BaseState import BaseState
from src.classes.Button import Button
from src.classes.SettingsManager import SettingsManager

class Menu_SettingsState(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)
        self.settings_manager = SettingsManager()
        self.current_settings_index = self.settings_manager.load_all_settings_index()
        self.setting_index = 0

        self.button_list = []
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
                'left_arrow_scale': 0,
                'right_arrow_scale': 0,
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
        
        for i, option in enumerate(self.settings_option_surface_list):
            self.button_list.append(Button(game=self.game,
                                           id=option['id'],
                                           width=500,
                                           height=50,
                                           pos=(constants.canvas_width/2, 200 + i*50),
                                           pos_anchor='center',
                                           hover_cursor=None,
                                           enable_click=False))
            self.button_list.append(Button(game=self.game,
                                           id=option['id']+'_left',
                                           width=48,
                                           height=50,
                                           pos=(constants.canvas_width/2 - 180, 200 + i*50),
                                           pos_anchor='center'))
            self.button_list.append(Button(game=self.game,
                                           id=option['id']+'_right',
                                           width=48,
                                           height=50,
                                           pos=(constants.canvas_width/2 + 180, 200 + i*50),
                                           pos_anchor='center'))
        for i, option in enumerate(self.button_option_surface_list):
            self.button_list.append(Button(game=self.game,
                                           id=option['id'],
                                           width=300,
                                           height=60,
                                           pos=(constants.canvas_width/2, 515 + i*65),
                                           pos_anchor='center'))


    def update(self, dt, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.exit_state()

        for button in self.button_list:
            button.update(dt=dt, events=events)
            
            if button.hovered:
                if button.hover_cursor is not None:
                    self.cursor = button.hover_cursor

                for i, option in enumerate(self.settings_option_surface_list):
                    if button.id == option['id']:
                        self.setting_index = i
                        option['left_arrow_scale'] = min(option['left_arrow_scale'] + 10*dt, 1.0)
                        option['right_arrow_scale'] = min(option['right_arrow_scale'] + 10*dt, 1.0)

                for option in self.button_option_surface_list:
                    if button.id == option['id']:
                        option['scale'] = min(option['scale'] + 2.4*dt, 1.2)

            else:
                for option in self.settings_option_surface_list:
                    if button.id == option['id']:
                        option['left_arrow_scale'] = max(option['left_arrow_scale'] - 10*dt, 0)
                        option['right_arrow_scale'] = max(option['right_arrow_scale'] - 10*dt, 0)

                for option in self.button_option_surface_list:
                    if button.id == option['id']:
                        option['scale'] = max(option['scale'] - 2.4*dt, 1.0)
            
            """
            UGLIEST CODE EVER!! DON'T LOOK!!!!!
            """
            if button.clicked:
                if button.id.endswith('_left') or button.id.endswith('_right'):
                    if button.id.endswith('_left'):
                        self.current_settings_index[self.setting_index] = (self.current_settings_index[self.setting_index] - 1) % len(self.settings_manager.settings_list[self.setting_index]['value'])
                        self.settings_manager.save_setting(self.current_settings_index)
                        left_arrow_scale = 0.25
                        right_arrow_scale = 1
                    elif button.id.endswith('_right'):
                        self.current_settings_index[self.setting_index] = (self.current_settings_index[self.setting_index] + 1) % len(self.settings_manager.settings_list[self.setting_index]['value'])
                        self.settings_manager.save_setting(self.current_settings_index)
                        left_arrow_scale = 1
                        right_arrow_scale = 0.25
                    text_string = self.settings_manager.settings_list[self.setting_index]['label']+':  '+self.settings_manager.settings_list[self.setting_index]['value_label'][self.current_settings_index[self.setting_index]]
                    text = utils.get_text(text=text_string, font=fonts.lf2, size='small', color=colors.white)
                    self.settings_option_surface_list[self.setting_index] = {
                        'id': self.settings_manager.settings_list[self.setting_index]['id'],
                        'surface': text,
                        'left_arrow_scale': left_arrow_scale,
                        'right_arrow_scale': right_arrow_scale,
                    }
                    self.game.apply_settings(self.setting_index)

                if button.id == 'reset':
                    for i in range(len(self.settings_option_surface_list)):
                        text_string = self.settings_manager.settings_list[i]['label']+':  '+self.settings_manager.settings_list[i]['value_default_label']
                        text = utils.get_text(text=text_string, font=fonts.lf2, size='small', color=colors.white)
                        self.settings_option_surface_list[i] = {
                            'id': self.settings_manager.settings_list[i]['id'],
                            'surface': text,
                            'left_arrow_scale': 0,
                            'right_arrow_scale': 0,
                        }
                    self.settings_manager.reset_settings()
                    for i in range(len(self.settings_manager.settings_list)):
                        if self.current_settings_index[i] != self.settings_manager.settings_list[i]['value_default_index']:
                            self.game.apply_settings(i)
                    self.current_settings_index = self.settings_manager.load_all_settings_index()

                elif button.id == 'back':
                    self.exit_state()
            """
            UGLIEST CODE EVER!! DON'T LOOK!!!!!
            """
                    
        utils.set_cursor(cursor=self.cursor)
        self.cursor = cursors.normal


    def render(self, canvas):
        utils.blit(dest=canvas, source=self.page_title, pos=(constants.canvas_width/2, 120), pos_anchor='center')
        for i, option in enumerate(self.settings_option_surface_list):
            utils.blit(dest=canvas, source=option['surface'], pos=(constants.canvas_width/2, 200 + i*50), pos_anchor='center')
            scaled_left_arrow = pygame.transform.scale_by(surface=self.arrow_left, factor=option['left_arrow_scale'])
            scaled_right_arrow = pygame.transform.scale_by(surface=self.arrow_right, factor=option['right_arrow_scale'])
            utils.blit(dest=canvas,
                        source=scaled_left_arrow,
                        pos=(constants.canvas_width/2 - 180, 200 + i*50),
                        pos_anchor='center')
            utils.blit(dest=canvas,
                        source=scaled_right_arrow,
                        pos=(constants.canvas_width/2 + 180, 200 + i*50),
                        pos_anchor='center')
            
        for i, option in enumerate(self.button_option_surface_list):
            scaled_surface = pygame.transform.scale_by(surface=option['surface'], factor=option['scale'])
            utils.blit(dest=canvas, source=scaled_surface, pos=(constants.canvas_width/2, 515 + i*65), pos_anchor='center')
            