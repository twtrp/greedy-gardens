from src.library.essentials import *
from src.template.BaseState import BaseState
from src.states.Menu_PlayState import Menu_PlayState
from src.components.Button import Button

class Menu_TitleState(BaseState):
    def __init__(self, parent, stack):
        BaseState.__init__(self, parent, stack)

        self.button_list = []
        for i, option in enumerate(self.parent.title_options_surfaces_list):
            self.button_list.append(Button(id=option['id'],
                                           surface=option['surface'],
                                           pos=(constants.canvas_width/2, 340 + i*80),
                                           pos_anchor='center'))


    #Main methods

    def update(self, dt, events):
        for button in self.button_list:
            button.update(dt=dt, events=events)
            if button.clicked:
                if button.id == 'play':
                    Menu_PlayState(parent=self.parent, stack=self.stack).enter_state()
                elif button.id == 'quit':
                    self.exit_state()


    def render(self, canvas):
        # Render game logo
        utils.blit(dest=canvas, source=self.parent.game_logo, pos=(constants.canvas_width/2, 150), pos_anchor='center')
        # Render menu options
        for i, option in enumerate(self.parent.title_options_surfaces_list):
            utils.blit(dest=canvas, source=option['surface'], pos=(constants.canvas_width/2, 340 + i*80), pos_anchor='center')