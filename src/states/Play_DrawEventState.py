from src.library.essentials import *
from src.template.BaseState import BaseState
 


class Play_DrawEventState(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)

        print("Drawing event")

        # state
        self.not_drawn = True
        self.card_drawn_image = None
        self.parent.drawing_event_card = True

    def update(self, dt, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.not_drawn:
                        utils.sound_play(sound=sfx.card, volume=self.game.sfx_volume)
                        self.card_drawn = self.parent.deck_event.draw_card()
                        self.parent.drawn_cards_event.append(self.card_drawn)
                        self.card_drawn_image = self.parent.cards_event_sprites[f"card_{self.card_drawn.card_name}"]
                        self.parent.current_event = self.card_drawn.card_name
                        if len(self.parent.revealed_event) > 0:
                            self.parent.revealed_event.pop()
                        self.not_drawn = False
                    else:
                        self.parent.is_strike = False
                        self.parent.eventing = True
                        self.parent.drawing_event_card = False
                        print("exiting draw event") 
                        self.exit_state()

        utils.set_cursor(cursor=self.cursor)
        self.cursor = cursors.normal

    def render(self, canvas):
        if self.card_drawn_image:
            scaled_card_drawn = pygame.transform.scale_by(surface=self.card_drawn_image, factor=2)
            scaled_card_drawn = utils.effect_outline(surface=scaled_card_drawn, distance=4, color=colors.white)
            utils.blit(dest=canvas, source=scaled_card_drawn, pos=(constants.canvas_width/2, constants.canvas_height/2), pos_anchor='center')
