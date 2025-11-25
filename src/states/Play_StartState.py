from src.library.essentials import *
from src.template.BaseState import BaseState

class Play_StartState(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)

        # print("Starting")

        # state
        self.card_drawn = None
        self.card_drawn_image = None
        self.card_drawn_text = None

        self.seasonal_not_drawn = True
        self.day1_not_drawn = True
        self.day2_not_drawn = True
        self.magic_fruit1_not_drawn = True
        self.magic_fruit2_not_drawn = True
        self.magic_fruit3_not_drawn = True
        self.path_card_text_shown = False

        self.previous_card_drawn = None

        def on_complete():
            self.parent.transitioning = False
            self.parent.day_title_tween_chain()
        self.parent.tween_list.append(tween.to(
            container=self.parent,
            key='mask_circle_radius',
            end_value=750,
            time=1,
            ease_type=tweencurves.easeInQuint
        ).on_complete(on_complete))

        utils.sound_play(sound=sfx.chicken_crowing, volume=self.game.sfx_volume)
        
    def update(self, dt, events):
        # Check if in tutorial mode and get input permissions
        get_module_func = getattr(self.parent, '_get_active_allow_input_module', None)
        allow_input_module = get_module_func() if get_module_func else None
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.parent.transitioning and self.parent.shown_day_title:
                    # Check if drawing card is allowed
                    if allow_input_module is None or allow_input_module.is_draw_card_allowed():
                        if allow_input_module is not None:
                            allow_input_module.consume_draw_card()
                        self._handle_card_drawing()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3 and not self.parent.transitioning and self.parent.shown_day_title:  # Right click
                    # Check if drawing card is allowed
                    if allow_input_module is None or allow_input_module.is_draw_card_allowed():
                        if allow_input_module is not None:
                            allow_input_module.consume_draw_card()
                        self._handle_card_drawing()

        utils.set_cursor(cursor=self.cursor)
        self.cursor = cursors.normal

    def _handle_card_drawing(self):
        # for testing
        if self.day2_not_drawn:
            self.card_drawn = self.parent.deck_fruit.draw_card()
            self.card_drawn_image_props = {
                'x': 1080,
                'y': 130,
                'scale': 1,
            }
            def on_complete():
                self.parent.tween_list.clear()
            utils.multitween(
                tween_list=self.parent.tween_list,
                container=self.card_drawn_image_props,
                keys=['x', 'y', 'scale'],
                end_values=[constants.canvas_width/2, constants.canvas_height/2, 2],
                time=0.3,
                ease_type=tweencurves.easeOutQuart,
                on_complete=on_complete
            )
            if self.card_drawn and self.seasonal_not_drawn:
                utils.sound_play(sound=sfx.card, volume=self.game.sfx_volume, pitch_variation=0.15)
                # self.parent.seasonal_fruit = self.card_drawn.card_name
                # self.parent.drawn_cards_fruit.append(self.card_drawn)
                self.card_drawn_image = self.parent.cards_fruit_sprites[f"card_{self.card_drawn.card_name}"]
                self.card_drawn_text = utils.get_text(text='Seasonal Fruit', font=fonts.wacky_pixels, size='medium', color=colors.white)
                self.seasonal_not_drawn = False
                self.parent.left_box_none_text = utils.get_text(text='Draw day 1 fruit', font=fonts.wacky_pixels, size='tiny', color=colors.white)
                self.parent.animate_task_text()  # Trigger task text animation
                self.previous_card_drawn = self.card_drawn
            elif self.card_drawn and self.day1_not_drawn:
                utils.sound_play(sound=sfx.card, volume=self.game.sfx_volume, pitch_variation=0.15)
                self.parent.seasonal_fruit = self.previous_card_drawn.card_name
                # self.parent.day1_fruit = self.card_drawn.card_name
                # self.parent.drawn_cards_fruit.append(self.card_drawn)
                self.card_drawn_image = self.parent.cards_fruit_sprites[f"card_{self.card_drawn.card_name}"]
                self.card_drawn_text = utils.get_text(text='Day 1 Fruit', font=fonts.wacky_pixels, size='medium', color=colors.white)
                self.day1_not_drawn = False
                self.parent.left_box_none_text = utils.get_text(text='Draw day 2 fruit', font=fonts.wacky_pixels, size='tiny', color=colors.white)
                self.parent.animate_task_text()  # Trigger task text animation
                self.previous_card_drawn = self.card_drawn
            elif self.card_drawn and self.day2_not_drawn:
                utils.sound_play(sound=sfx.card, volume=self.game.sfx_volume, pitch_variation=0.15)
                self.parent.day1_fruit = self.previous_card_drawn.card_name
                # self.parent.day2_fruit = self.card_drawn.card_name
                # self.parent.drawn_cards_fruit.append(self.card_drawn)
                self.card_drawn_image = self.parent.cards_fruit_sprites[f"card_{self.card_drawn.card_name}"]
                self.card_drawn_text = utils.get_text(text='Day 2 Fruit', font=fonts.wacky_pixels, size='medium', color=colors.white)
                self.day2_not_drawn = False
                self.parent.left_box_none_text = utils.get_text(text='Draw magic fruit 1', font=fonts.wacky_pixels, size='tiny', color=colors.white)
                self.parent.animate_task_text()  # Trigger task text animation
                self.previous_card_drawn = self.card_drawn
        elif self.magic_fruit3_not_drawn:
            self.card_drawn = self.parent.deck_event.draw_card()
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
                time=0.3,
                ease_type=tweencurves.easeOutQuart,
                on_complete=on_complete
            )
            if self.card_drawn and self.magic_fruit1_not_drawn:
                utils.sound_play(sound=sfx.card, volume=self.game.sfx_volume, pitch_variation=0.15)
                self.parent.day2_fruit = self.previous_card_drawn.card_name
                # self.parent.magic_fruit1_event = self.card_drawn.card_name
                self.parent.drawn_cards_event.append(self.card_drawn)
                self.card_drawn_image = self.parent.cards_event_sprites[f"card_{self.card_drawn.card_name}"]
                self.card_drawn_text = utils.get_text(text='Magic fruit 1 Event', font=fonts.wacky_pixels, size='medium', color=colors.white)
                self.magic_fruit1_not_drawn = False
                self.parent.magicing_number = 1
                self.parent.left_box_none_text = utils.get_text(text='Draw magic fruit 2', font=fonts.wacky_pixels, size='tiny', color=colors.white)
                self.parent.animate_task_text()  # Trigger task text animation
                self.previous_card_drawn = self.card_drawn
            elif self.card_drawn and self.magic_fruit2_not_drawn:
                utils.sound_play(sound=sfx.card, volume=self.game.sfx_volume, pitch_variation=0.15)
                self.parent.magic_fruit1_event = self.previous_card_drawn.card_name
                # self.parent.magic_fruit2_event = self.card_drawn.card_name
                self.parent.drawn_cards_event.append(self.card_drawn)
                self.card_drawn_image = self.parent.cards_event_sprites[f"card_{self.card_drawn.card_name}"]
                self.card_drawn_text = utils.get_text(text='Magic fruit 2 Event', font=fonts.wacky_pixels, size='medium', color=colors.white)
                self.magic_fruit2_not_drawn = False
                self.parent.magicing_number = 2
                self.parent.left_box_none_text = utils.get_text(text='Draw magic fruit 3', font=fonts.wacky_pixels, size='tiny', color=colors.white)
                self.parent.animate_task_text()  # Trigger task text animation
                self.previous_card_drawn = self.card_drawn
            elif self.card_drawn and self.magic_fruit3_not_drawn:
                utils.sound_play(sound=sfx.card, volume=self.game.sfx_volume, pitch_variation=0.15)
                self.parent.magic_fruit2_event = self.previous_card_drawn.card_name
                # self.parent.magic_fruit3_event = self.card_drawn.card_name
                self.parent.drawn_cards_event.append(self.card_drawn)
                self.card_drawn_image = self.parent.cards_event_sprites[f"card_{self.card_drawn.card_name}"]
                self.card_drawn_text = utils.get_text(text='Magic fruit 3 Event', font=fonts.wacky_pixels, size='medium', color=colors.white)
                self.magic_fruit3_not_drawn = False
                self.parent.magicing_number = 3
                if not self.path_card_text_shown:
                    self.parent.left_box_none_text = utils.get_text(text='Draw path card', font=fonts.wacky_pixels, size='tiny', color=colors.white)
                    self.parent.animate_task_text()  # Trigger task text animation
                    self.path_card_text_shown = True
                self.previous_card_drawn = self.card_drawn
        else: 
            self.parent.magic_fruit3_event = self.previous_card_drawn.card_name
            self.parent.magicing_number = 0
            self.parent.drawing = True
            self.parent.setup_start_state=True
            # Set the previous task state to match what the main state will use to prevent double animation
            self.parent.previous_task_state = "draw_path"
            self.exit_state()

    def render(self, canvas):
        if self.card_drawn_image:
            utils.blit(dest=canvas, source=self.card_drawn_text, pos=(constants.canvas_width/2, constants.canvas_height/2 - 170), pos_anchor='center')
            scaled_card_drawn = pygame.transform.scale_by(surface=self.card_drawn_image, factor=self.card_drawn_image_props['scale'])
            # scaled_card_drawn = utils.effect_outline(surface=scaled_card_drawn, distance=4, color=colors.white)
            utils.blit(dest=canvas, source=scaled_card_drawn, pos=(self.card_drawn_image_props['x'], self.card_drawn_image_props['y']), pos_anchor='center')