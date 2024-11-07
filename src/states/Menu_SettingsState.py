from src.library.essentials import *
from src.template.BaseState import BaseState
from src.classes.Button import Button
from src.classes.SettingsManager import SettingsManager

class Menu_SettingsState(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)
        self.settings_manager = SettingsManager()
        print(self.settings_manager.load_all_settings())

        
    #Main methods

    def update(self, dt, events):
        utils.set_cursor(cursor=self.cursor)
        self.cursor = cursors.normal


    def render(self, canvas):
        pass
