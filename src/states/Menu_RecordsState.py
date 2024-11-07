from src.library.essentials import *
from src.template.BaseState import BaseState
from src.classes.Button import Button

class Menu_RecordsState(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)


    #Main methods

    def update(self, dt, events):
        utils.set_cursor(cursor=self.cursor)
        self.cursor = cursors.normal


    def render(self, canvas):
        pass