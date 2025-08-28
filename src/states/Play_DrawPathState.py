from src.library.essentials import *
from src.template.BaseState import BaseState

class Play_DrawPathState(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)

        # print("Drawing path")

        # state
        self.not_drawn = True
        self.card_drawn_image = None
        self.parent.drawing_path_card = True
        self.parent.current_turn += 1
        self.parent.right_box_title = utils.get_text(text=f'Turn {self.parent.current_turn}', font=fonts.lf2, size='small', color=colors.white)

    def update(self, dt, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.parent.shown_day_title:
                    if self.not_drawn:
                        self.card_drawn_image_props = {
                            'x': 1080,
                            'y': 265,
                            'scale': 1,
                        }
                        def on_complete():
                            self.parent.tween_list.clear()
                        utils.multitween(
                            tween_list=self.parent.tween_list,
                            container=self.card_drawn_image_props,
                            keys=['x', 'y', 'scale'],
                            end_values=[constants.canvas_width/2, constants.canvas_height/2, 2],
                            time=0.4,
                            ease_type=tweencurves.easeOutQuint,
                            on_complete=on_complete
                        )
                        utils.sound_play(sound=sfx.card, volume=self.game.sfx_volume)
                        self.card_drawn = self.parent.deck_path.draw_card()
                        self.parent.drawn_cards_path.append(self.card_drawn)
                        self.card_drawn_image = self.parent.cards_path_sprites[f"card_{self.card_drawn.card_name}"]
                        if len(self.parent.revealed_path) > 0:
                            self.parent.revealed_path.pop()
                        self.not_drawn = False
                    else:
                        self.parent.current_path = self.card_drawn.card_name
                        self.parent.placing = True
                        if "strike" in self.parent.current_path:
                            self.parent.strikes += 1
                        # print("exiting draw path")
                        self.parent.drawing_path_card = False
                        self.exit_state()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3 and self.parent.shown_day_title:  # Right click
                    if self.not_drawn:
                        self.card_drawn_image_props = {
                            'x': 1080,
                            'y': 265,
                            'scale': 1,
                        }
                        def on_complete():
                            self.parent.tween_list.clear()
                        utils.multitween(
                            tween_list=self.parent.tween_list,
                            container=self.card_drawn_image_props,
                            keys=['x', 'y', 'scale'],
                            end_values=[constants.canvas_width/2, constants.canvas_height/2, 2],
                            time=0.4,
                            ease_type=tweencurves.easeOutQuint,
                            on_complete=on_complete
                        )
                        utils.sound_play(sound=sfx.card, volume=self.game.sfx_volume)
                        self.card_drawn = self.parent.deck_path.draw_card()
                        self.parent.drawn_cards_path.append(self.card_drawn)
                        self.card_drawn_image = self.parent.cards_path_sprites[f"card_{self.card_drawn.card_name}"]
                        if len(self.parent.revealed_path) > 0:
                            self.parent.revealed_path.pop()
                        self.not_drawn = False
                    else:
                        self.parent.current_path = self.card_drawn.card_name
                        self.parent.placing = True
                        if "strike" in self.parent.current_path:
                            self.parent.strikes += 1
                        # print("exiting draw path")
                        self.parent.drawing_path_card = False
                        self.exit_state()
 
        utils.set_cursor(cursor=self.cursor)
        self.cursor = cursors.normal

    def render(self, canvas):
        if self.card_drawn_image:
            scaled_card_drawn = pygame.transform.scale_by(surface=self.card_drawn_image, factor=self.card_drawn_image_props['scale'])
            # scaled_card_drawn = utils.effect_outline(surface=scaled_card_drawn, distance=4, color=colors.white)
            utils.blit(dest=canvas, source=scaled_card_drawn, pos=(self.card_drawn_image_props['x'], self.card_drawn_image_props['y']), pos_anchor='center')
