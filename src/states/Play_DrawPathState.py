from src.library.essentials import *
from src.template.BaseState import BaseState

class Play_DrawPathState(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)
        self.parent = parent

        print("Drawing path")

        # state
        self.not_drawn = True
        self.card_drawn_image = None

    def update(self, dt, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.not_drawn:
                        self.card_drawn = self.parent.deck_path.draw_card()
                        self.parent.drawn_cards_path.append(self.card_drawn)
                        self.card_drawn_image = utils.get_sprite(sprite_sheet=spritesheets.cards_path, target_sprite=f"card_{self.card_drawn.card_name}")
                        self.parent.current_path = self.card_drawn.card_name
                        self.not_drawn = False
                    else:
                        self.parent.placing = True
                        if "strike" in self.parent.current_path:
                            self.parent.strikes += 1
                        print("exiting draw path")
                        self.exit_state()
 
        utils.set_cursor(cursor=self.cursor)
        self.cursor = cursors.normal

    def render(self, canvas):
        if self.card_drawn_image:
            scaled_card_drawn = pygame.transform.scale_by(surface=self.card_drawn_image, factor=2)
            utils.blit(dest=canvas, source=scaled_card_drawn, pos=(constants.canvas_width/2, constants.canvas_height/2), pos_anchor='center')