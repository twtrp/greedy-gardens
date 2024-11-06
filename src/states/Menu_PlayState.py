from src.library.essentials import *
from src.template.BaseState import BaseState
from src.components.Button import Button

class Menu_PlayState(BaseState):
    def __init__(self, parent, stack):
        BaseState.__init__(self, parent, stack)

        self.back_button = Button(id='back',
                                  surface=self.parent.back_text,
                                  pos=(constants.canvas_width/2, constants.canvas_height/2),
                                  pos_anchor='center')


    #Main methods

    def update(self, dt, events):
        self.back_button.update(dt=dt, events=events)

        if self.back_button.clicked:
            self.exit_state()


    def render(self, canvas):
        utils.blit(dest=canvas,
                   source=self.parent.back_text,
                   pos=(constants.canvas_width/2, constants.canvas_height/2),
                   pos_anchor='center')
