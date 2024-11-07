from src.library.essentials import *
from src.template.BaseState import BaseState
from src.classes.Button import Button

class Play_StartState(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)

        print("Entered Start State")

    def update(self, dt, events):
        self.exit_state()

    def render(self, canvas):
        pass