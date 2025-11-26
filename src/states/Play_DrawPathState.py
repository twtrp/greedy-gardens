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

    def update(self, dt, events):
        # Check if in tutorial mode and get input permissions
        get_module_func = getattr(self.parent, '_get_active_allow_input_module', None)
        allow_input_module = get_module_func() if get_module_func else None
        
        for event in events:
            should_trigger = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and self.parent.shown_day_title:
                should_trigger = True
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3 and self.parent.shown_day_title:
                should_trigger = True
            
            # Check if drawing card is allowed in tutorial
            if should_trigger and allow_input_module is not None:
                if not allow_input_module.is_draw_card_allowed():
                    should_trigger = False
                elif should_trigger:
                    allow_input_module.consume_draw_card()
            
            if should_trigger: 
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
                        ease_type=tweencurves.easeOutQuart,
                        on_complete=on_complete
                    )
                    utils.sound_play(sound=sfx.card, volume=self.game.sfx_volume, pitch_variation=0.15)
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
