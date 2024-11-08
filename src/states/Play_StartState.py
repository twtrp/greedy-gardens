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
        canvas_width = self.game.canvas.get_width()
        canvas_height = self.game.canvas.get_height()

        # Render left white box
        utils.draw_rect(dest=canvas,
                            size=(272, canvas_height),
                            pos=(0, 0),
                            pos_anchor='topleft',
                            color=(*colors.white, 191), # 75% transparency
                            inner_border_width=4,
                            outer_border_width=0,
                            outer_border_color=colors.black)
        
        # Render right white box
        utils.draw_rect(dest=canvas,
                            size=(272, canvas_height),
                            pos=(canvas_width - 272, 0),
                            pos_anchor='topleft',
                            color=(*colors.white, 191), # 75% transparency
                            inner_border_width=4,
                            outer_border_width=0,
                            outer_border_color=colors.black)
        