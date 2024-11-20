from src.library.essentials import *
from src.template.BaseState import BaseState
from src.classes.Button import Button
from src.states.Menu_PlayState import Menu_PlayState
from src.states.Menu_RecordsState import Menu_RecordsState
from src.states.Menu_SettingsState import Menu_SettingsState

class Menu_TitleState(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)

        self.button_list = []
        for i, option in enumerate(self.parent.title_button_option_surface_list):
            self.button_list.append(Button(
                game=self.game,
                id=option['id'],
                width=300,
                height=80,
                pos=(constants.canvas_width/2, 340 + i*80),
                pos_anchor=posanchors.center
            ))


    #Main methods

    def update(self, dt, events):
        
        if not self.parent.transitioning:
            for button in self.button_list:
                button.update(dt=dt, events=events)
                
                if button.hovered:
                    self.cursor = button.hover_cursor
                    for option in self.parent.title_button_option_surface_list:
                        if button.id == option['id']:
                            option['scale'] = min(option['scale'] + 2.4*dt, 1.2)
                else:
                    for option in self.parent.title_button_option_surface_list:
                        if button.id == option['id']:
                            option['scale'] = max(option['scale'] - 2.4*dt, 1.0)
                
                if button.clicked:
                    if button.id == 'play':
                        utils.sound_play(sound=sfx.select, volume=self.game.sfx_volume)
                        Menu_PlayState(game=self.game, parent=self.parent, stack=self.stack).enter_state()
                    elif button.id == 'records':
                        utils.sound_play(sound=sfx.select, volume=self.game.sfx_volume)
                        Menu_RecordsState(game=self.game, parent=self.parent, stack=self.stack).enter_state()
                    elif button.id == 'settings':
                        utils.sound_play(sound=sfx.select, volume=self.game.sfx_volume)
                        Menu_SettingsState(game=self.game, parent=self.parent, stack=self.stack).enter_state()
                    elif button.id == 'quit':
                        utils.sound_play(sound=sfx.deselect, volume=self.game.sfx_volume)
                        pygame.mixer.stop()
                        pygame.quit()
                        sys.exit()
        
        utils.set_cursor(cursor=self.cursor)
        self.cursor = cursors.normal


    def render(self, canvas):
        # Render game logo
        utils.blit(dest=canvas, source=self.parent.game_logo, pos=(constants.canvas_width/2, 150), pos_anchor=posanchors.center)
        # Render menu options
        for i, option in enumerate(self.parent.title_button_option_surface_list):
            scaled_surface = pygame.transform.scale_by(surface=option['surface'], factor=option['scale'])
            utils.blit(dest=canvas, source=scaled_surface, pos=(constants.canvas_width/2, 340 + i*80), pos_anchor=posanchors.center)
        