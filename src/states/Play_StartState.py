from src.library.essentials import *
from src.template.BaseState import BaseState

class Play_StartState(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)
        self.parent = parent

        print("Starting")

        # state
        self.card_drawn = None
        self.card_drawn_image = None

        self.seasonal_not_drawn = True
        self.day1_not_drawn = True
        self.day2_not_drawn = True
        self.magic_fruit1_not_drawn = True
        self.magic_fruit2_not_drawn = True
        self.magic_fruit3_not_drawn = True
        
    def update(self, dt, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # for testing
                    if self.day2_not_drawn:
                        self.card_drawn = self.parent.deck_fruit.draw_card()
                        if self.card_drawn and self.seasonal_not_drawn:
                            self.parent.seasonal_fruit = self.card_drawn.card_name
                            # self.parent.drawn_cards_fruit.append(self.card_drawn)
                            self.card_drawn_image = utils.get_sprite(sprite_sheet=spritesheets.cards_fruit, target_sprite=f"card_{self.card_drawn.card_name}")
                            self.seasonal_not_drawn = False
                        elif self.card_drawn and self.day1_not_drawn:
                            self.parent.day1_fruit = self.card_drawn.card_name
                            # self.parent.drawn_cards_fruit.append(self.card_drawn)
                            self.card_drawn_image = utils.get_sprite(sprite_sheet=spritesheets.cards_fruit, target_sprite=f"card_{self.card_drawn.card_name}")
                            self.day1_not_drawn = False
                        elif self.card_drawn and self.day2_not_drawn:
                            self.parent.day2_fruit = self.card_drawn.card_name
                            # self.parent.drawn_cards_fruit.append(self.card_drawn)
                            self.card_drawn_image = utils.get_sprite(sprite_sheet=spritesheets.cards_fruit, target_sprite=f"card_{self.card_drawn.card_name}")
                            self.day2_not_drawn = False
                    elif self.magic_fruit3_not_drawn:
                        self.card_drawn = self.parent.deck_event.draw_card()
                        if self.card_drawn and self.magic_fruit1_not_drawn:
                            self.parent.magic_fruit1_event = self.card_drawn.card_name
                            self.parent.drawn_cards_event.append(self.card_drawn)
                            self.card_drawn_image = utils.get_sprite(sprite_sheet=spritesheets.cards_event, target_sprite=f"card_{self.card_drawn.card_name}")
                            self.magic_fruit1_not_drawn = False
                        elif self.card_drawn and self.magic_fruit2_not_drawn:
                            self.parent.magic_fruit2_event = self.card_drawn.card_name
                            self.parent.drawn_cards_event.append(self.card_drawn)
                            self.card_drawn_image = utils.get_sprite(sprite_sheet=spritesheets.cards_event, target_sprite=f"card_{self.card_drawn.card_name}")
                            self.magic_fruit2_not_drawn = False
                        elif self.card_drawn and self.magic_fruit3_not_drawn:
                            self.parent.magic_fruit3_event = self.card_drawn.card_name
                            self.parent.drawn_cards_event.append(self.card_drawn)
                            self.card_drawn_image = utils.get_sprite(sprite_sheet=spritesheets.cards_event, target_sprite=f"card_{self.card_drawn.card_name}")
                            self.magic_fruit3_not_drawn = False
                    else: 
                        self.parent.drawing = True
                        self.exit_state()

        utils.set_cursor(cursor=self.cursor)
        self.cursor = cursors.normal

    def render(self, canvas):
        if self.card_drawn_image:
            scaled_card_drawn = pygame.transform.scale_by(surface=self.card_drawn_image, factor=2)
            utils.blit(dest=canvas, source=scaled_card_drawn, pos=(constants.canvas_width/2, constants.canvas_height/2), pos_anchor='center')
