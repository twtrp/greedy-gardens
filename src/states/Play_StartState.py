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

        def on_complete():
            self.parent.transitioning = False
            self.parent.tween_list.clear()
        self.parent.tween_list.append(tween.to(
            container=self.parent,
            key='mask_circle_radius',
            end_value=750,
            time=1,
            ease_type=tweencurves.easeInQuint
        ).on_complete(on_complete))
        
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
                            self.card_drawn_image = self.parent.cards_fruit_sprites[f"card_{self.card_drawn.card_name}"]
                            self.seasonal_not_drawn = False
                        elif self.card_drawn and self.day1_not_drawn:
                            self.parent.day1_fruit = self.card_drawn.card_name
                            # self.parent.drawn_cards_fruit.append(self.card_drawn)
                            self.card_drawn_image = self.parent.cards_fruit_sprites[f"card_{self.card_drawn.card_name}"]
                            self.day1_not_drawn = False
                        elif self.card_drawn and self.day2_not_drawn:
                            self.parent.day2_fruit = self.card_drawn.card_name
                            # self.parent.drawn_cards_fruit.append(self.card_drawn)
                            self.card_drawn_image = self.parent.cards_fruit_sprites[f"card_{self.card_drawn.card_name}"]
                            self.day2_not_drawn = False
                    elif self.magic_fruit3_not_drawn:
                        self.card_drawn = self.parent.deck_event.draw_card()
                        if self.card_drawn and self.magic_fruit1_not_drawn:
                            self.parent.magic_fruit1_event = self.card_drawn.card_name
                            self.parent.drawn_cards_event.append(self.card_drawn)
                            self.card_drawn_image = self.parent.cards_event_sprites[f"card_{self.card_drawn.card_name}"]
                            self.magic_fruit1_not_drawn = False
                            self.parent.magicing_number = 1
                        elif self.card_drawn and self.magic_fruit2_not_drawn:
                            self.parent.magic_fruit2_event = self.card_drawn.card_name
                            self.parent.drawn_cards_event.append(self.card_drawn)
                            self.card_drawn_image = self.parent.cards_event_sprites[f"card_{self.card_drawn.card_name}"]
                            self.magic_fruit2_not_drawn = False
                            self.parent.magicing_number = 2
                        elif self.card_drawn and self.magic_fruit3_not_drawn:
                            self.parent.magic_fruit3_event = self.card_drawn.card_name
                            self.parent.drawn_cards_event.append(self.card_drawn)
                            self.card_drawn_image = self.parent.cards_event_sprites[f"card_{self.card_drawn.card_name}"]
                            self.magic_fruit3_not_drawn = False
                            self.parent.magicing_number = 3
                    else: 
                        self.parent.magicing_number = 0
                        self.parent.drawing = True
                        self.parent.setup_start_state=True
                        self.exit_state()

        utils.set_cursor(cursor=self.cursor)
        self.cursor = cursors.normal

    def render(self, canvas):
        if self.card_drawn_image:
            scaled_card_drawn = pygame.transform.scale_by(surface=self.card_drawn_image, factor=2)
            utils.blit(dest=canvas, source=scaled_card_drawn, pos=(constants.canvas_width/2, constants.canvas_height/2), pos_anchor='center')
            if self.parent.magicing_number > 0:
                self.scaled_magic_fruit = pygame.transform.scale_by(surface=getattr(self.parent, f'magic_fruit{self.parent.magicing_number}_image'), factor=2)
                utils.blit(dest=canvas, source=self.scaled_magic_fruit, pos=(constants.canvas_width/2, constants.canvas_height/2 - 128 - 16), pos_anchor='center')