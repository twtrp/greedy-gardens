from src.library.essentials import *
from src.template.BaseState import BaseState
from src.classes.Button import Button
from src.classes.Deck import Deck
from src.classes.Cards import Cards

class Play_StartState(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)
        self.parent = parent

        print("Starting")

        self.card_drawn = None
        self.card_fruit_drawn_image = None

        self.load_assets()


    def load_assets(self):
        pass
        

    def update(self, dt, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # for testing
                    self.card_drawn = self.parent.deck_fruit.draw_card()
                    if self.card_drawn:
                        self.parent.seasonal_fruit = self.card_drawn.card_name
                        self.parent.drawn_cards_fruit.append(self.card_drawn)
                        self.card_fruit_drawn_image = utils.get_sprite(sprite_sheet=spritesheets.cards_fruit, target_sprite=f"card_fruit_{self.card_drawn.card_name}")

        utils.set_cursor(cursor=self.cursor)
        self.cursor = cursors.normal

    def render(self, canvas):
        if self.card_fruit_drawn_image:
            scaled_card_fruit_drawn = pygame.transform.scale_by(surface=self.card_fruit_drawn_image, factor=2)
            utils.blit(dest=canvas, source=scaled_card_fruit_drawn, pos=(constants.canvas_width/2, constants.canvas_height/2), pos_anchor='center')
