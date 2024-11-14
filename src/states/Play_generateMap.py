from src.library.essentials import *
from src.template.BaseState import BaseState
import random as rand

class Play_GenerateMapState(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)
        self.parent = parent
        print("Generating Map")
        
        self.cell_pos = -1
        self.house_index = rand.randint(0,63)
        
        self.load_assets()

    def load_assets(self):
        self.selecting_tile = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='selecting_tile')
        
    def update(self, dt):
        self.parent.game_board.set_home(self.house_index)
        
    def render(self, canvas):
        utils.blit(dest=canvas, source=self.selecting_tile , pos=(self.parent.grid_start_x + ((self.cell_pos % 8) * self.parent.cell_size), self.parent.grid_start_y + ((self.cell_pos // 8) * self.parent.cell_size)), pos_anchor='topleft')

        