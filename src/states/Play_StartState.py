from src.library.essentials import *
from src.template.BaseState import BaseState
from src.classes.Button import Button

class Play_StartState(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)

        self.load_assets()

    def load_assets(self):
        # left text
        self.left_box_title = utils.get_text(text='Score', font=fonts.lf2, size='small', color=colors.white)

        self.score_list = [
            {'text': 'Day 1',},
            {'text': 'Day 2',},
            {'text': 'Day 3',},
            {'text': 'Day 4',},
            {'text': 'Seasonal',},
            {'text': 'Total',},
        ]

        self.score_title_list = []
        for score in self.score_list:
            text = utils.get_text(text=score['text'], font=fonts.lf2, size='smaller', color=colors.white)
            self.score_title_list.append(text)

        self.left_box_strike = utils.get_text(text='Event Strikes', font=fonts.lf2, size='small', color=colors.white)

        self.blank_strike_image = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='strike_blank')

        self.left_box_task = utils.get_text(text='Current task', font=fonts.lf2, size='small', color=colors.white)

        self.left_box_path_text = utils.get_text(text='Place drawn path', font=fonts.lf2, size='tiny', color=colors.white)

        # right text
        self.right_box_title = utils.get_text(text='Cards', font=fonts.lf2, size='small', color=colors.white)

        self.deck_list = [
            {'text': 'Fruit',},
            {'text': 'Path',},
            {'text': 'Event',},
        ]

        self.deck_title_list = []
        for score in self.deck_list:
            text = utils.get_text(text=score['text'], font=fonts.lf2, size='smaller', color=colors.white)
            self.deck_title_list.append(text)

        self.right_remaining = utils.get_text(text='Remaining', font=fonts.lf2, size='smaller', color=colors.white)
        

    def update(self, dt, events):
        utils.set_cursor(cursor=self.cursor)
        self.cursor = cursors.normal

    def render(self, canvas):
        box_width = 272

        # Render left white box
        utils.draw_rect(dest=canvas,
                            size=(box_width, constants.canvas_height),
                            pos=(0, 0),
                            pos_anchor='topleft',
                            color=(*colors.white, 191), # 75% transparency
                            inner_border_width=4,
                            outer_border_width=0,
                            outer_border_color=colors.black)
        
        # Render text in left white box
        utils.blit(dest=canvas, source=self.left_box_title, pos=(box_width/2, 40), pos_anchor='center')
        for i, score in enumerate(self.score_title_list):
            utils.blit(dest=canvas, source=score, pos=(60, 80 + i*45), pos_anchor='topleft')
        utils.blit(dest=canvas, source=self.left_box_strike, pos=(box_width/2, 390), pos_anchor='center')
        utils.blit(dest=canvas, source=self.left_box_task, pos=(box_width/2, 510), pos_anchor='center')
        utils.blit(dest=canvas, source=self.left_box_path_text, pos=(box_width/2, 550), pos_anchor='center')

        # Render strike box in left white box
        scaled_blank_strike = pygame.transform.scale_by(surface=self.blank_strike_image, factor=0.625)
        for i in range(3):
                utils.blit(dest=canvas, source=scaled_blank_strike, pos=(40 + i*64, 420), pos_anchor='topleft')
        
        # Render right white box
        utils.draw_rect(dest=canvas,
                            size=(box_width, constants.canvas_height),
                            pos=(constants.canvas_width - box_width, 0),
                            pos_anchor='topleft',
                            color=(*colors.white, 191), # 75% transparency
                            inner_border_width=4,
                            outer_border_width=0,
                            outer_border_color=colors.black)
        
        # Render text in right white box
        utils.blit(dest=canvas, source=self.right_box_title, pos=(constants.canvas_width - box_width/2, 40), pos_anchor='center')
        for i, deck in enumerate(self.deck_title_list):
            utils.blit(dest=canvas, source=deck, pos=(1150, 90 + i*125), pos_anchor='topleft')
            utils.blit(dest=canvas, source=self.right_remaining, pos=(1150, 115 + i*125), pos_anchor='topleft')

        # Render strike box in right white box
        scaled_blank_strike = pygame.transform.scale_by(surface=self.blank_strike_image, factor=0.625)
