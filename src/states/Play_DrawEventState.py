from src.library.essentials import *
from src.template.BaseState import BaseState
from src.classes.Button import Button
 


class Play_DrawEventState(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)

        # print("Drawing event")

        # state
        self.not_drawn = True
        self.card_drawn_image = None
        self.parent.drawing_event_card = True

    def update(self, dt, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.not_drawn:
                        self.card_drawn_image_props = {
                            'x': 1080,
                            'y': 400,
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
                        self.card_drawn = self.parent.deck_event.draw_card()
                        self.parent.drawn_cards_event.append(self.card_drawn)
                        self.card_drawn_image = self.parent.cards_event_sprites[f"card_{self.card_drawn.card_name}"]
                        if len(self.parent.revealed_event) > 0:
                            self.parent.revealed_event.pop()
                            # Update buttons for revealed event cards after removing revealed event
                            # Remove existing revealed event buttons
                            self.parent.button_list = [btn for btn in self.parent.button_list if not btn.id.startswith('revealed_event_individual_')]
                            
                            # Add new buttons for each revealed event card with larger hitboxes to eliminate gaps
                            for i, card in enumerate(self.parent.revealed_event):
                                # Create a larger invisible surface for better hover detection
                                button_surface = pygame.Surface((self.parent.revealed_event_button_width, self.parent.revealed_event_button_height), pygame.SRCALPHA)
                                button_x = constants.canvas_width - self.parent.box_width - self.parent.revealed_event_button_width
                                button_y = self.parent.revealed_event_button_y_base + i * self.parent.revealed_event_button_y_spacing
                                self.parent.button_list.append(Button(
                                    game=self.parent.game,
                                    id=f'revealed_event_individual_{i}',
                                    surface=button_surface,  # Use larger invisible surface for hitbox
                                    pos=(button_x, button_y),
                                    pos_anchor='topleft',
                                    hover_cursor=cursors.hand,
                                ))
                        self.not_drawn = False
                    else:
                        self.parent.is_current_task_event = True
                        self.parent.current_event = self.card_drawn.card_name
                        self.parent.is_strike = False
                        self.parent.eventing = True
                        self.parent.drawing_event_card = False
                        # print("exiting draw event") 
                        self.exit_state()

        utils.set_cursor(cursor=self.cursor)
        self.cursor = cursors.normal

    def render(self, canvas):
        if self.card_drawn_image:
            scaled_card_drawn = pygame.transform.scale_by(surface=self.card_drawn_image, factor=self.card_drawn_image_props['scale'])
            # scaled_card_drawn = utils.effect_outline(surface=scaled_card_drawn, distance=4, color=colors.white)
            utils.blit(dest=canvas, source=scaled_card_drawn, pos=(self.card_drawn_image_props['x'], self.card_drawn_image_props['y']), pos_anchor='center')

