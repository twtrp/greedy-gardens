from src.library.essentials import *
from src.template.BaseState import BaseState
from src.classes.Button import Button

class Play_StartState(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)

        self.load_assets()

    def load_assets(self):
        pass
        

    def update(self, dt, events):
        utils.set_cursor(cursor=self.cursor)
        self.cursor = cursors.normal

    def render(self, canvas):
        pass
